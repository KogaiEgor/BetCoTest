from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.bets.db import get_async_session
from app.bets.schemas import BetCreate, BetResponse
from app.bets.services import (
    create_bet_service,
    get_bets_history_service,
    get_all_events_from_provider,
)

router = APIRouter()


@router.post("/bet", response_model=BetResponse)
async def create_bet(bet: BetCreate, db: AsyncSession = Depends(get_async_session)):
    try:
        return await create_bet_service(bet, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/bets", response_model=list[BetResponse])
async def get_bets_history(db: AsyncSession = Depends(get_async_session)):
    try:
        return await get_bets_history_service(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/events")
async def get_events():
    try:
        return await get_all_events_from_provider()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
