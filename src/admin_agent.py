from langchain.agents import create_agent
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI

from src.database import (
    get_pending_reservations, approve_reservation, reject_reservation, get_reservation_by_id,
    get_reservations_by_status, count_free_lots
)
from datetime import datetime, UTC

from src.email_notifier import send_admin_reservation_email


SYSTEM_PROMPT = f"""
You are an administrator assistant for parking reservations.
Current system time: {datetime.now(UTC).isoformat()}.
Your job:
- show pending reservation requests
- show approved reservation requests
- show rejected reservation requests
- approve a reservation by id
- reject a reservation by id

Rules:
- Only help with parking reservation administration tasks and closely related reservation queries.
- If the request is unrelated, refuse briefly.
- For listing pending reservations, always use the list_pending_reservations tool.
- For listing approved reservations, always use the list_approved_reservations tool.
- For listing rejected reservations, always use the list_rejected_reservations tool.
- For approving a reservation, always use the approve_reservation tool.
- For rejecting a reservation, always use the reject_reservation tool.
- Do not invent reservation ids.
- When listing reservations, always show the reservation id.
- If the user asks for approved or rejected reservations "for today", interpret "today" as the current date.
- If the user asks for a date-specific reservation list, filter the tool result by the reservation start date when possible.
"""



def list_pending_reservations() -> str:
    rows = get_pending_reservations()

    if not rows:
        return "There are no pending reservations."

    lines = []
    for r in rows:
        lines.append(
            f"ID {r['id']} | {r['name']} | {r['car_number']} | "
            f"{r['start_time']} -> {r['end_time']}"
        )

    return "\n".join(lines)

def list_approved_reservations() -> str:
    reservations = get_reservations_by_status("APPROVED")
    if not reservations:
        return "No approved reservations found."

    return "\n".join(
        f'ID {r["id"]}: {r["name"]}, {r["car_number"]}, {r["start_time"]} - {r["end_time"]}, approved at {r["approval_time"]}'
        for r in reservations
    )

def list_rejected_reservations() -> str:
    reservations = get_reservations_by_status("REJECTED")
    if not reservations:
        return "No rejected reservations found."

    return "\n".join(
        f'ID {r["id"]}: {r["name"]}, {r["car_number"]}, {r["start_time"]} - {r["end_time"]}'
        for r in reservations
    )

def escalate_reservation_to_admin(
    reservation_id: int,
    name: str,
    car_number: str,
    start_time: str,
    end_time: str,
) -> None:
    send_admin_reservation_email(
        reservation_id=reservation_id,
        name=name,
        car_number=car_number,
        start_time=start_time,
        end_time=end_time,
    )

def approve_reservation_action(reservation_id: int) -> dict:
    reservation = get_reservation_by_id(reservation_id)
    if reservation is None:
        return {
            "ok": False,
            "message": f"Reservation {reservation_id} does not exist.",
            "approved_reservation_id": None,
        }

    if reservation["status"] != "PENDING_APPROVAL":
        return {
            "ok": False,
            "message": (
                f"Reservation {reservation_id} could not be approved. "
                "It is no longer pending."
            ),
            "approved_reservation_id": None,
        }

    free_lots = count_free_lots(
        reservation["start_time"],
        reservation["end_time"],
    )

    if free_lots <= 0:
        return {
            "ok": False,
            "message": (
                f"Reservation {reservation_id} cannot be approved. "
                "All parking spaces are occupied in this period."
            ),
            "approved_reservation_id": None,
        }

    success = approve_reservation(reservation_id)

    if not success:
        return {
            "ok": False,
            "message": (
                f"Reservation {reservation_id} could not be approved. "
                "It may not exist or is no longer pending."
            ),
            "approved_reservation_id": None,
        }

    return {
        "ok": True,
        "message": f"Reservation {reservation_id} was approved successfully.",
        "approved_reservation_id": reservation_id,
    }

def approve_reservation_tool(reservation_id: int) -> str:
    result = approve_reservation_action(reservation_id)
    return result["message"]

def reject_reservation_tool(reservation_id: int) -> str:
    success = reject_reservation(reservation_id)

    if not success:
        return (
            f"Reservation {reservation_id} could not be rejected. "
            "It may not exist or is no longer pending."
        )

    return f"Reservation {reservation_id} was rejected successfully."


def build_admin_agent():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    tools = [
        StructuredTool.from_function(
            func=list_pending_reservations,
            name="list_pending_reservations",
            description="List all reservation requests waiting for approval.",
        ),
        StructuredTool.from_function(
            func=approve_reservation_tool,
            name="approve_reservation",
            description="Approve a reservation request by reservation_id.",
        ),
        StructuredTool.from_function(
            func=reject_reservation_tool,
            name="reject_reservation",
            description="Reject a reservation request by reservation_id.",
        ),
        StructuredTool.from_function(
            func=list_approved_reservations,
            name="list_approved_reservations",
            description="List all approved reservations.",
        ),
        StructuredTool.from_function(
            func=list_rejected_reservations,
            name="list_rejected_reservations",
            description="List all rejected reservations.",
        ),
    ]

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )


def admin_chat(agent, user_input: str, chat_history: list) -> str:
    result = agent.invoke(
        {
            "messages": chat_history + [{"role": "user", "content": user_input}]
        }
    )
    last = result["messages"][-1]
    return last.content if hasattr(last, "content") else last["content"]