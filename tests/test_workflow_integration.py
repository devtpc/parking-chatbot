from src.workflow import build_workflow


def test_full_workflow_user_request():
    workflow = build_workflow()

    result = workflow.invoke(
        {
            "role": "user",
            "user_input": "I want to reserve parking tomorrow from 08:00 to 12:00. My name is John and my car is ABC-123",
            "chat_history": [],
            "response": "",
            "reservation_id": None,
            "notify_admin": False,
            "approved_reservation_id": None,
            "should_record": False,
        }
    )

    assert "Request id" in result["response"]