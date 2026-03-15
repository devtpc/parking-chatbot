# src/mcp_client.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()
MCP_API_KEY = os.getenv("MCP_API_KEY")

def write_approved_reservation_via_mcp(
    name: str,
    car_number: str,
    start_time: str,
    end_time: str,
    approval_time: str,
) -> None:
    if not MCP_API_KEY:
        raise ValueError("MCP_API_KEY is not configured.")

    response = requests.post(
        "http://localhost:8001/approved-reservations",
        json={
            "name": name,
            "car_number": car_number,
            "start_time": start_time,
            "end_time": end_time,
            "approval_time": approval_time,
        },
        headers={"x-api-key": MCP_API_KEY},
        timeout=5,
    )
    response.raise_for_status()