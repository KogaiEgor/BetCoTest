from fastapi import FastAPI
from app.lines.router import router as lines_router


app = FastAPI()

app.include_router(lines_router, prefix="/events", tags=["Events"])
