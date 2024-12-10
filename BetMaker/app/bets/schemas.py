from pydantic import BaseModel, Field, ConfigDict


class BetCreate(BaseModel):
    event_id: str = Field(..., description="ID of the event")
    amount: float = Field(..., gt=0, description="Bet amount (positive number)")


class BetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)\

    id: int
    event_id: str
    amount: float
    status: str

