from unittest.mock import patch

from src.admin_agent import (
    escalate_reservation_to_admin,
    approve_reservation_tool,
    reject_reservation_tool,
)


@patch("src.admin_agent.send_admin_reservation_email")
def test_escalate_reservation_to_admin_sends_email(mock_send_email):
    escalate_reservation_to_admin(
        reservation_id=1,
        name="John Doe",
        car_number="ABC-123",
        start_time="2026-03-20T08:00:00",
        end_time="2026-03-20T12:00:00",
    )

    mock_send_email.assert_called_once_with(
        reservation_id=1,
        name="John Doe",
        car_number="ABC-123",
        start_time="2026-03-20T08:00:00",
        end_time="2026-03-20T12:00:00",
    )


@patch("src.admin_agent.append_approved_reservation_to_file")
@patch("src.admin_agent.get_reservation_by_id")
@patch("src.admin_agent.approve_reservation")
def test_approve_reservation_tool_calls_database(
    mock_approve, mock_get_reservation, mock_file_write
):
    mock_approve.return_value = True
    mock_get_reservation.return_value = {
        "name": "John Doe",
        "car_number": "ABC-123",
        "start_time": "2026-03-20T08:00:00",
        "end_time": "2026-03-20T12:00:00",
        "approval_time": "2026-03-19T10:00:00",
    }

    result = approve_reservation_tool(5)

    mock_approve.assert_called_once_with(5)
    mock_file_write.assert_called_once()

    assert result == "Reservation 5 was approved successfully."


@patch("src.admin_agent.reject_reservation")
def test_reject_reservation_tool_calls_database(mock_reject):
    mock_reject.return_value = True

    result = reject_reservation_tool(7)

    mock_reject.assert_called_once_with(7)
    assert result == "Reservation 7 was rejected successfully."