import re
from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from src.admin_agent import admin_chat, build_admin_agent, escalate_reservation_to_admin
from src.chatbot import build_agent, chat
from src.database import get_reservation_by_id
from src.mcp_client import write_approved_reservation_via_mcp


class WorkflowState(TypedDict):
    role: str
    user_input: str
    chat_history: list
    response: str
    reservation_id: int | None
    notify_admin: bool
    approved_reservation_id: int | None
    should_record: bool


def _extract_request_id(text: str) -> int | None:
    match = re.search(r"request\s*id\s*:\s*(\d+)", text, re.IGNORECASE)
    return int(match.group(1)) if match else None


def _extract_approved_id(text: str) -> int | None:
    match = re.search(r"Reservation\s+(\d+)", text)
    if match and "approved" in text.lower():
        return int(match.group(1))
    return None


def user_interaction_node(state: WorkflowState) -> WorkflowState:
    agent = build_agent()
    response = chat(
        agent=agent,
        user_input=state["user_input"],
        chat_history=state["chat_history"],
    )
    print(response)
    reservation_id = _extract_request_id(response)

    return {
        **state,
        "response": response,
        "reservation_id": reservation_id,
        "notify_admin": reservation_id is not None,
    }


def administrator_approval_node(state: WorkflowState) -> WorkflowState:
    if state["role"] == "user" and state["notify_admin"] and state["reservation_id"] is not None:
        reservation = get_reservation_by_id(state["reservation_id"])
        if reservation is not None:
            escalate_reservation_to_admin(
                reservation_id=reservation["id"],
                name=reservation["name"],
                car_number=reservation["car_number"],
                start_time=reservation["start_time"],
                end_time=reservation["end_time"],
            )

        return {
            **state,
            "notify_admin": False,
        }

    if state["role"] == "admin":
        agent = build_admin_agent()
        response = admin_chat(
            agent=agent,
            user_input=state["user_input"],
            chat_history=state["chat_history"],
        )
        approved_reservation_id = _extract_approved_id(response)

        return {
            **state,
            "response": response,
            "approved_reservation_id": approved_reservation_id,
            "should_record": approved_reservation_id is not None,
        }

    return state


def data_recording_node(state: WorkflowState) -> WorkflowState:
    reservation_id = state["approved_reservation_id"]
    if reservation_id is None:
        return state

    reservation = get_reservation_by_id(reservation_id)
    if reservation is None:
        return {
            **state,
            "response": (
                f"Reservation {reservation_id} was approved, "
                "but the reservation details could not be loaded for recording."
            ),
            "should_record": False,
        }

    try:
        write_approved_reservation_via_mcp(
            name=reservation["name"],
            car_number=reservation["car_number"],
            start_time=reservation["start_time"],
            end_time=reservation["end_time"],
            approval_time=reservation["approval_time"],
        )
    except Exception as e:
        return {
            **state,
            "response": (
                f"Reservation {reservation_id} was approved in the database, "
                f"but the MCP server failed: {e}"
            ),
            "should_record": False,
        }

    return {
        **state,
        "should_record": False,
    }


def route_from_start(state: WorkflowState) -> str:
    return "user_interaction_node" if state["role"] == "user" else "administrator_approval_node"


def route_after_user(state: WorkflowState):
    return "administrator_approval_node" if state["notify_admin"] else END


def route_after_admin(state: WorkflowState):
    return "data_recording_node" if state["should_record"] else END


def build_workflow():
    graph = StateGraph(WorkflowState)

    graph.add_node("user_interaction_node", user_interaction_node)
    graph.add_node("administrator_approval_node", administrator_approval_node)
    graph.add_node("data_recording_node", data_recording_node)

    graph.add_conditional_edges(
        START,
        route_from_start,
        {
            "user_interaction_node": "user_interaction_node",
            "administrator_approval_node": "administrator_approval_node",
        },
    )

    graph.add_conditional_edges(
        "user_interaction_node",
        route_after_user,
        {
            "administrator_approval_node": "administrator_approval_node",
            END: END,
        },
    )

    graph.add_conditional_edges(
        "administrator_approval_node",
        route_after_admin,
        {
            "data_recording_node": "data_recording_node",
            END: END,
        },
    )

    graph.add_edge("data_recording_node", END)

    return graph.compile()


def export_workflow_png(output_path: str = "data/langgraph_workflow.png") -> str:
    workflow = build_workflow()
    png_bytes = workflow.get_graph().draw_mermaid_png()

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png_bytes)

    return str(path)