import os
import aio_pika

from app.bets.db import AsyncSessionLocal
from app.bets.services import process_message


RABBITMQ_URL = os.getenv("RABBITMQ_URL")


async def consume_events():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("events", durable=True)

        async with AsyncSessionLocal() as db:
            async for message in queue.iterator():
                await process_message(message, db)
