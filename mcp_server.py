# mcp_server.py
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
MCP_API_KEY = os.getenv("MCP_API_KEY")

APPROVED_RESERVATIONS_FILE = Path("data/approved_reservations.txt")

def verify_api_key(x_api_key: str | None) -> None:
    if not MCP_API_KEY:
        raise HTTPException(status_code=500, detail="MCP_API_KEY is not configured.")

    if x_api_key != MCP_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized.")



class ApprovedReservationPayload(BaseModel):
    name: str
    car_number: str
    start_time: str
    end_time: str
    approval_time: str

@app.get("/")
def root():
    return {"status": "ok", "service": "parking reservation MCP server"}

@app.post("/approved-reservations")
def write_approved_reservation(
    payload: ApprovedReservationPayload,
    x_api_key: str | None = Header(default=None),
):
    verify_api_key(x_api_key)

    line = (
        f"{payload.name} | {payload.car_number} | "
        f"{payload.start_time} - {payload.end_time} | {payload.approval_time}\n"
    )

    APPROVED_RESERVATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with APPROVED_RESERVATIONS_FILE.open("a", encoding="utf-8") as f:
        f.write(line)

    return {"status": "ok"}