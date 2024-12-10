import time
import uuid

from app.lines.data import EventRepository
from app.lines.models import CreateEvent, UpdateEvent, Event
from app.lines.publisher import publish_event


repository = EventRepository()


async def create_event(event_data: CreateEvent) -> Event:
    event_id = str(uuid.uuid4())
    event = Event(
        event_id=event_id,
        coefficient=event_data.coefficient,
        deadline=event_data.deadline,
        state=event_data.state,
    )
    await repository.create_event(event)
    return event


async def process_event(event_id: str, updates: UpdateEvent) -> Event:
    event = await get_event(event_id)
    updates_dict = updates.model_dump(exclude_unset=True)

    if event.state != updates.state:
        await publish_event(
            event_id=event_id,
            status=updates.state,
        )

    await update_event(event, updates_dict)
    return event


async def update_event(event: Event, updates: dict) -> None:
    current_time = int(time.time())

    if "deadline" not in updates and event.deadline <= current_time:
        raise ValueError("Current deadline has passed. A new deadline must be provided explicitly.")
    elif "deadline" in updates and updates["deadline"] < event.deadline:
        raise ValueError("A new deadline must be equal or greater than the previous one.")

    await repository.update_event(event.event_id, updates)


async def get_event(event_id: str) -> Event:
    event = await repository.get_event(event_id)
    if not event:
        raise ValueError("Event not found")
    return event


async def get_active_events():
    return await repository.get_active_events(current_time=int(time.time()))
