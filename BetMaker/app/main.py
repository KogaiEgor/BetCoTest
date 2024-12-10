import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.bets import router
from app.bets.consumer import consume_events


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(consume_events())
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router.router, tags=["Bets"])
