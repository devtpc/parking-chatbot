import re
from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from src.admin_agent import admin_chat, build_admin_agent, escalate_reservation_to_admin, approve_reservation_action
from src.chatbot import build_agent, chat, create_pending_reservation_action
from src.database import get_reservation_by_id
from src.mcp_client import write_approved_reservation_via_mcp

import json

class WorkflowState(TypedDict):
    role: str
    user_input: str
    chat_history: list
    response: str
    reservation_id: int | None
    notify_admin: bool
    approved_reservation_id: int | None
    should_record: bool

def user_interaction_node(state: WorkflowState) -> WorkflowState:
    agent = build_agent()

    result = agent.invoke(
        {
            "messages": state["chat_history"] + [
                {"role": "user", "content": state["user_input"]}
            ]
        }
    )

    messages = result["messages"]
    last = messages[-1]
    response = last.content if hasattr(last, "content") else last["content"]

    reservation_id = None

    for message in messages:
        name = getattr(message, "name", None)
        content = getattr(message, "content", None)

        if name == "handle_reservation_request" and isinstance(content, str):
            try:
                payload = json.loads(content)
                reservation_id = payload.get("reservation_id")
                break
            except json.JSONDecodeError:
                pass

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
        user_input = state["user_input"].strip().lower()

        approve_match = re.search(r"approve(?:\s+reservation)?\s+(\d+)", user_input)
        if approve_match:
            reservation_id = int(approve_match.group(1))
            result = approve_reservation_action(reservation_id)

            return {
                **state,
                "response": result["message"],
                "approved_reservation_id": result["approved_reservation_id"],
                "should_record": result["approved_reservation_id"] is not None,
            }

        agent = build_admin_agent()
        response = admin_chat(
            agent=agent,
            user_input=state["user_input"],
            chat_history=state["chat_history"],
        )

        return {
            **state,
            "response": response,
            "approved_reservation_id": None,
            "should_record": False,
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