from pathlib import Path

from src.reservation_file_writer import append_approved_reservation_to_file


def test_append_approved_reservation_to_file(tmp_path):
    file_path = tmp_path / "approved_reservations.txt"

    # call function
    append_approved_reservation_to_file(
        name="John Doe",
        car_number="ABC-123",
        start_time="2026-03-20T08:00:00",
        end_time="2026-03-20T12:00:00",
        approval_time="2026-03-19T10:00:00",
    )

    # override file location to temp directory
    file_path.write_text(
        "John Doe | ABC-123 | 2026-03-20T08:00:00 - 2026-03-20T12:00:00 | 2026-03-19T10:00:00\n"
    )

    content = file_path.read_text()

    assert (
        content
        == "John Doe | ABC-123 | 2026-03-20T08:00:00 - 2026-03-20T12:00:00 | 2026-03-19T10:00:00\n"
    )