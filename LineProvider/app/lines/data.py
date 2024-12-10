from typing import Dict, Optional
from app.lines.models import Event


class EventRepository:
    def __init__(self):
        self.events: Dict[str, Event] = {}

    async def create_event(self, event: Event):
        if event.event_id in self.events:
            raise ValueError("Event with this ID already exists")
        self.events[event.event_id] = event

    async def update_event(self, event_id: str, updates: dict):
        if event_id not in self.events:
            raise ValueError("Event not found")
        for field, value in updates.items():
            setattr(self.events[event_id], field, value)

    async def get_event(self, event_id: str) -> Optional[Event]:
        return self.events.get(event_id)

    async def get_active_events(self, current_time: int):
        return [event for event in self.events.values() if event.deadline > current_time]
