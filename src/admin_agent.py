from langchain.agents import create_agent
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI

from src.database import (
    get_pending_reservations,
)

from src.email_notifier import send_admin_reservation_email

SYSTEM_PROMPT = """
You are an administrator assistant for parking reservation approvals.

Your job:
- show pending reservation requests
- approve a reservation by id
- reject a reservation by id

Rules:
- Only help with reservation approval tasks.
- If the request is unrelated, refuse briefly.
- For listing pending reservations, always use the list_pending_reservations tool.
- For approving a reservation, always use the approve_reservation tool.
- For rejecting a reservation, always use the reject_reservation tool.
- Do not invent reservation ids.
- When listing pending reservations, show the reservation id.
- Approval and rejection are mock actions in Stage 2 only.
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

def approve_reservation_tool(reservation_id: int) -> str:
    return (
        f"Administrator approved reservation {reservation_id}. "
        "Execution of approval will be implemented in Stage 3."
    )


def reject_reservation_tool(reservation_id: int) -> str:
    return (
        f"Administrator rejected reservation {reservation_id}. "
        "Execution of rejection will be implemented in Stage 3."
    )


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