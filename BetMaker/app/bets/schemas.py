from pydantic import BaseModel, Field, ConfigDict, condecimal


class BetCreate(BaseModel):
    event_id: str = Field(..., description="ID of the event")
    amount: condecimal(gt=0, max_digits=10, decimal_places=2) = Field(..., description="Bet amount (positive number)")


class BetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)\

    id: int
    event_id: str
    amount: float
    status: str
