from fastapi import APIRouter, HTTPException
from app.lines.models import CreateEvent, UpdateEvent, Event
from app.lines.services import create_event, process_event, get_event, get_active_events


router = APIRouter()


@router.post("/", response_model=Event)
async def create_event_endpoint(event_request: CreateEvent):
    try:
        event = await create_event(event_request)
        return event
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{event_id}", response_model=Event)
async def update_event_endpoint(event_id: str, updates: UpdateEvent):
    try:
        updated_event = await process_event(event_id, updates)
        return updated_event
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{event_id}")
async def get_event_endpoint(event_id: str):
    try:
        return await get_event(event_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/")
async def get_active_events_endpoint():
    return await get_active_events()
