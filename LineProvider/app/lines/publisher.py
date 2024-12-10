import os
import json
import aio_pika

from app.lines.models import EventState


RABBITMQ_URL = os.getenv("RABBITMQ_URL")


async def publish_event(event_id: str, status: EventState):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps({
                    "event_id": event_id,
                    "status": status.value,
                }).encode()
            ),
            routing_key="events",
        )
