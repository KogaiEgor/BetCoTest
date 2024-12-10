import asyncio

import pytest
import pydantic
import time
from app.lines.services import (
    create_event,
    process_event,
    update_event,
    get_event,
    get_active_events,
)
from app.lines.models import CreateEvent, UpdateEvent, EventState


@pytest.mark.asyncio
async def test_create_event_invalid_coefficient_negative():
    with pytest.raises(ValueError, match="Input should be greater than 0"):
        CreateEvent(
            coefficient=-1.5,
            deadline=int(time.time()) + 3600,
            state=EventState.NEW,
        )


@pytest.mark.asyncio
async def test_create_event_invalid_coefficient_too_low():
    with pytest.raises(ValueError, match="Coefficient must be a number more than 1"):
        CreateEvent(
            coefficient=0.9,
            deadline=int(time.time()) + 3600,
            state=EventState.NEW,
        )


@pytest.mark.asyncio
async def test_create_event_past_deadline():
    with pytest.raises(ValueError, match="Deadline must be greater than the current time"):
        CreateEvent(
            coefficient=1.5,
            deadline=int(time.time()) - 100,
            state=EventState.NEW,
        )


@pytest.mark.asyncio
async def test_create_event_missing_fields():
    with pytest.raises(pydantic.ValidationError, match="Field required"):
        await create_event(CreateEvent())


@pytest.mark.asyncio
async def test_create_event_success():
    event_data = CreateEvent(
        coefficient=1.5,
        deadline=int(time.time()) + 3600,
        state=EventState.NEW,
    )

    event = await create_event(event_data)

    assert event.coefficient == event_data.coefficient
    assert event.deadline == event_data.deadline
    assert event.state == event_data.state
    assert event.event_id is not None


@pytest.mark.asyncio
async def test_process_event_update_status():
    event_data = CreateEvent(
        coefficient=1.5,
        deadline=int(time.time()) + 3600,
        state=EventState.NEW,
    )
    event = await create_event(event_data)

    updates = UpdateEvent(state=EventState.FINISHED_WIN)
    updated_event = await process_event(event.event_id, updates)

    assert updated_event.state == EventState.FINISHED_WIN
    assert updated_event.coefficient == event.coefficient
    assert updated_event.deadline == event.deadline


@pytest.mark.asyncio
async def test_process_event_not_found():
    updates = UpdateEvent(state=EventState.FINISHED_WIN)

    with pytest.raises(ValueError, match="Event not found"):
        await process_event("event id", updates)


@pytest.mark.asyncio
async def test_update_event_deadline_error():
    event_data = CreateEvent(
        coefficient=1.5,
        deadline=int(time.time()) + 3600,
        state=EventState.NEW,
    )
    event = await create_event(event_data)

    updates = {"deadline": int(time.time()) - 100}

    with pytest.raises(ValueError, match="A new deadline must be equal or greater than the previous one."):
        await update_event(event, updates)


@pytest.mark.asyncio
async def test_update_event_deadline_must_update_error():
    event_data = CreateEvent(
        coefficient=1.5,
        deadline=int(time.time() + 1),
        state=EventState.NEW,
    )
    event = await create_event(event_data)
    await asyncio.sleep(1)

    updates = {"coefficient": 1.7}

    with pytest.raises(ValueError, match="Current deadline has passed. A new deadline must be provided explicitly."):
        await update_event(event, updates)



@pytest.mark.asyncio
async def test_get_event_success():
    event_data = CreateEvent(
        coefficient=1.5,
        deadline=int(time.time()) + 3600,
        state=EventState.NEW,
    )
    event = await create_event(event_data)

    fetched_event = await get_event(event.event_id)
    assert fetched_event == event


@pytest.mark.asyncio
async def test_get_event_not_found():
    with pytest.raises(ValueError, match="Event not found"):
        await get_event("event id")


@pytest.mark.asyncio
async def test_get_active_events():
    current_time = int(time.time())
    from app.lines.services import repository
    repository.events.clear()

    await create_event(
        CreateEvent(
            coefficient=1.5,
            deadline=current_time + 3600,
            state=EventState.NEW,
        )
    )
    await create_event(
        CreateEvent(
            coefficient=1.7,
            deadline=current_time + 4000,
            state=EventState.NEW,
        )
    )

    active_events = await get_active_events()
    assert len(active_events) == 2
