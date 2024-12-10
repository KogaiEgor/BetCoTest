from sqlalchemy import Column, Integer, String, Numeric
from app.bets.db import Base


class Bet(Base):
    __tablename__ = "bets"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, nullable=False, default="not_played")
