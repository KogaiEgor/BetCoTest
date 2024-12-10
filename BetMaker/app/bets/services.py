import httpx
import time
import json

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.bets.models import Bet
from app.bets.schemas import BetCreate


LINE_PROVIDER_URL = "http://line_provider:8001/events/"


async def get_event_from_provider(event_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{LINE_PROVIDER_URL}{event_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=404, detail="Event not found") from e


async def validate_event(event: dict) -> None:
    if event["deadline"] <= int(time.time()):
        raise HTTPException(status_code=400, detail="Betting deadline has passed")
    if event["state"] != 1:
        raise HTTPException(status_code=400, detail="Market closed")


async def create_new_bet(bet_data: BetCreate, db: AsyncSession) -> Bet:
    new_bet = Bet(event_id=bet_data.event_id, amount=bet_data.amount, status="not_played")
    db.add(new_bet)
    await db.commit()
    await db.refresh(new_bet)
    return new_bet


async def create_bet_service(bet_data: BetCreate, db: AsyncSession) -> Bet:
    event = await get_event_from_provider(bet_data.event_id)
    await validate_event(event)
    return await create_new_bet(bet_data, db)


async def get_bets_history_service(db: AsyncSession) -> list[Bet]:
    result = await db.execute(select(Bet))
    return list(result.scalars().all())


async def get_bet(event_id, db: AsyncSession) -> Bet:
    result = await db.execute(select(Bet).where(Bet.event_id == event_id))
    bet = result.scalar_one_or_none()

    if not bet:
        raise ValueError(f"Bet with event_id {event_id} not found")
    return bet


async def get_all_events_from_provider() -> list:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(LINE_PROVIDER_URL)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Connection error: {str(e)}")


async def update_status(bet: Bet, status: int) -> None:
    if status == 2:
        bet.status = "won"
    elif status == 3:
        bet.status = "lost"
    else:
        raise ValueError(f"Unknown status: {status}")


async def process_message(message, db: AsyncSession) -> None:
    async with message.process():
        event_data = json.loads(message.body)
        event_id = event_data["event_id"]
        status = event_data["status"]

        try:
            bet = await get_bet(event_id, db)
            await update_status(bet, status)
            await db.commit()
        except ValueError as e:
            print(f"{e}")
