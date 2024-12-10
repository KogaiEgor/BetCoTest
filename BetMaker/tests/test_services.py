import pytest
import aio_pika
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import delete
from app.bets.schemas import BetCreate
from app.bets.models import Bet
from app.bets.services import (
    get_event_from_provider,
    validate_event,
    create_new_bet,
    create_bet_service,
    get_bets_history_service,
    get_bet,
    get_all_events_from_provider,
    update_status,
    process_message
)
from fastapi import HTTPException


@pytest.mark.asyncio
@patch("app.bets.services.httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_get_event_from_provider_success(mock_http_get):
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = lambda: {"event_id": "event1", "deadline": 9999999999, "state": 1}
    mock_response.raise_for_status = AsyncMock()
    mock_http_get.return_value = mock_response

    result = await get_event_from_provider("event1")
    assert result["event_id"] == "event1"
    assert result["deadline"] == 9999999999
    assert result["state"] == 1


@pytest.mark.asyncio
@patch("app.bets.services.httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_get_event_from_provider_failure(mock_http_get):
    mock_http_get.side_effect = HTTPException(status_code=404, detail="Event not found")

    with pytest.raises(HTTPException) as e:
        await get_event_from_provider("empty")
    assert e.value.status_code == 404
    assert e.value.detail == "Event not found"


@pytest.mark.asyncio
async def test_validate_event_success():
    event = {"event_id": "event1", "deadline": 9999999999, "state": 1}
    await validate_event(event)


@pytest.mark.asyncio
async def test_validate_event_failure_deadline():
    event = {"event_id": "event1", "deadline": 1, "state": 1}

    with pytest.raises(HTTPException) as exc:
        await validate_event(event)
    assert exc.value.status_code == 400
    assert exc.value.detail == "Betting deadline has passed"


@pytest.mark.asyncio
async def test_validate_event_failure_market_closed():
    event = {"event_id": "event1", "deadline": 9999999999, "state": 2}

    with pytest.raises(HTTPException) as exc:
        await validate_event(event)
    assert exc.value.status_code == 400
    assert exc.value.detail == "Market closed"


@pytest.mark.asyncio
async def test_create_new_bet(async_session: AsyncSession):
    bet_data = BetCreate(event_id="event1", amount=100.0)
    new_bet = await create_new_bet(bet_data, async_session)

    assert new_bet.event_id == bet_data.event_id
    assert new_bet.amount == bet_data.amount
    assert new_bet.status == "not_played"


@pytest.mark.asyncio
@patch("app.bets.services.get_event_from_provider", new_callable=AsyncMock)
@patch("app.bets.services.validate_event", new_callable=AsyncMock)
async def test_create_bet_service(mock_validate_event, mock_get_event_from_provider, async_session: AsyncSession):
    mock_get_event_from_provider.return_value = {"event_id": "event1", "deadline": 9999999999, "state": 1}
    bet_data = BetCreate(event_id="event1", amount=100.0)

    new_bet = await create_bet_service(bet_data, async_session)

    assert new_bet.event_id == bet_data.event_id
    assert new_bet.amount == bet_data.amount
    assert new_bet.status == "not_played"


@pytest.mark.asyncio
async def test_get_bets_history_service(async_session: AsyncSession):
    await async_session.execute(delete(Bet))
    await async_session.commit()

    bet = Bet(event_id="event 1", amount=100.0, status="not_played")
    async_session.add(bet)
    await async_session.commit()

    history = await get_bets_history_service(async_session)

    assert len(history) == 1
    assert history[0].event_id == bet.event_id


@pytest.mark.asyncio
async def test_get_bet_success(async_session: AsyncSession):
    await async_session.execute(delete(Bet))
    await async_session.commit()

    bet = Bet(event_id="event1", amount=100.0, status="not_played")
    async_session.add(bet)
    await async_session.commit()

    retrieved_bet = await get_bet("event1", async_session)

    assert retrieved_bet.event_id == bet.event_id


@pytest.mark.asyncio
async def test_get_bet_failure(async_session: AsyncSession):
    with pytest.raises(ValueError) as exc:
        await get_bet("empty", async_session)
    assert "Bet with event_id empty not found" in str(exc.value)


@pytest.mark.asyncio
@patch("app.bets.services.httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_get_all_events_from_provider_success(mock_http_get):
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = lambda: [{"event_id": "event1"}, {"event_id": "event2"}]
    mock_response.raise_for_status = AsyncMock()
    mock_http_get.return_value = mock_response

    events = await get_all_events_from_provider()

    assert len(events) == 2
    assert events[0]["event_id"] == "event1"


@pytest.mark.asyncio
@patch("app.bets.services.httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_get_all_events_from_provider_failure(mock_http_get):
    mock_http_get.side_effect = HTTPException(status_code=500, detail="Connection error")

    with pytest.raises(HTTPException) as exc:
        await get_all_events_from_provider()
    assert exc.value.status_code == 500
    assert "Connection error" in exc.value.detail


@pytest.mark.asyncio
async def test_update_status_success():
    bet = Bet(event_id="event1", amount=100.0, status="not_played")

    await update_status(bet, 2)
    assert bet.status == "won"

    await update_status(bet, 3)
    assert bet.status == "lost"


@pytest.mark.asyncio
async def test_update_status_failure():
    bet = Bet(event_id="event1", amount=100.0, status="not_played")

    with pytest.raises(ValueError) as exc:
        await update_status(bet, 4)
    assert "Unknown status: 4" in str(exc.value)


@pytest.mark.asyncio
@patch("app.bets.services.get_bet", new_callable=AsyncMock)
async def test_process_message_success(mock_get_bet, async_session: AsyncSession):
    bet = Bet(event_id="event1", amount=100.0, status="not_played")
    mock_get_bet.return_value = bet

    message = MagicMock(spec=aio_pika.IncomingMessage)
    message.body = b'{"event_id": "event1", "status": 2}'

    await process_message(message, async_session)

    assert bet.status == "won"
