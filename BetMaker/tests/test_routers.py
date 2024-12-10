import pytest
import time
from unittest.mock import AsyncMock, patch
from app.bets.schemas import BetResponse


@pytest.mark.asyncio
@patch("app.bets.router.create_bet_service", new_callable=AsyncMock)
async def test_create_bet_success(mock_create_bet_service, test_client):
    mock_create_bet_service.return_value = BetResponse(
        id=1,
        event_id="event1",
        amount=100,
        status="not_played",
    )

    response = test_client.post(
        "/bet",
        json={"event_id": "event1", "amount": 100},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["event_id"] == "event1"
    assert data["amount"] == 100
    assert data["status"] == "not_played"


@pytest.mark.asyncio
@patch("app.bets.router.create_bet_service", new_callable=AsyncMock)
async def test_create_bet_failure(mock_create_bet_service, test_client):
    mock_create_bet_service.side_effect = Exception("Unexpected error")

    response = test_client.post(
        "/bet",
        json={"event_id": "event1", "amount": 100.00},
    )

    assert response.status_code == 500
    assert "Unexpected error" in response.json()["detail"]


@pytest.mark.asyncio
@patch("app.bets.router.create_bet_service", new_callable=AsyncMock)
async def test_create_bet_invalid_data(mock_create_bet_service, test_client):
    response = test_client.post(
        "/bet",
        json={"amount": 100.00},
    )
    assert response.status_code == 422

    response = test_client.post(
        "/bet",
        json={"event_id": "event1", "amount": "invalid_amount"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
@patch("app.bets.router.create_bet_service", new_callable=AsyncMock)
async def test_create_bet_with_negative_amount(mock_create_bet_service, test_client):
    response = test_client.post(
        "/bet",
        json={"event_id": "event1", "amount": -100.00},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
@patch("app.bets.router.create_bet_service", new_callable=AsyncMock)
async def test_create_bet_with_zero_amount(mock_create_bet_service, test_client):
    response = test_client.post(
        "/bet",
        json={"event_id": "event1", "amount": 0},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
@patch("app.bets.router.get_bets_history_service", new_callable=AsyncMock)
async def test_get_bets_history_success(mock_get_bets_history_service, test_client):
    mock_get_bets_history_service.return_value = [
        BetResponse(
            id=1,
            event_id="event1",
            amount=100,
            status="not_played",
        )
    ]

    response = test_client.get("/bets")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["event_id"] == "event1"
    assert data[0]["amount"] == 100
    assert data[0]["status"] == "not_played"


@pytest.mark.asyncio
@patch("app.bets.router.get_bets_history_service", new_callable=AsyncMock)
async def test_get_bets_history_no_bets(mock_get_bets_history_service, test_client):
    mock_get_bets_history_service.return_value = []

    response = test_client.get("/bets")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


@pytest.mark.asyncio
@patch("app.bets.router.get_bets_history_service", new_callable=AsyncMock)
async def test_get_bets_history_failure(mock_get_bets_history_service, test_client):
    mock_get_bets_history_service.side_effect = Exception("Unexpected error")

    response = test_client.get("/bets")

    assert response.status_code == 500
    assert "Unexpected error" in response.json()["detail"]


@pytest.mark.asyncio
@patch("app.bets.router.get_all_events_from_provider", new_callable=AsyncMock)
async def test_get_events_success(mock_get_all_events_from_provider, test_client):
    t = int(time.time())
    mock_get_all_events_from_provider.return_value = [
        {"event_id": "event1", "coefficient": 1.5, "deadline": t, "state": 1}
    ]

    response = test_client.get("/events")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["event_id"] == "event1"
    assert data[0]["coefficient"] == 1.5
    assert data[0]["deadline"] == t


@pytest.mark.asyncio
@patch("app.bets.router.get_all_events_from_provider", new_callable=AsyncMock)
async def test_get_events_no_events(mock_get_all_events_from_provider, test_client):
    mock_get_all_events_from_provider.return_value = []

    response = test_client.get("/events")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


@pytest.mark.asyncio
@patch("app.bets.router.get_all_events_from_provider", new_callable=AsyncMock)
async def test_get_events_failure(mock_get_all_events_from_provider, test_client):
    mock_get_all_events_from_provider.side_effect = Exception("Unexpected error")

    response = test_client.get("/events")

    assert response.status_code == 500
    assert "Unexpected error" in response.json()["detail"]
