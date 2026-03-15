import os
from pathlib import Path

from src.database import (
    init_database,
    count_free_lots,
    insert_pending_reservation,
    approve_reservation,
    reject_reservation,
    get_reservation_by_id,
)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DB_PATH = DATA_DIR / "test_sqlite.db"


def setup_module():
    # ensure clean DB for tests
    if DB_PATH.exists():
        os.remove(DB_PATH)
    init_database()


def test_initial_free_lots():
    free = count_free_lots(
        "2026-03-20T08:00:00",
        "2026-03-20T12:00:00",
    )
    assert free == 20


def test_pending_reservation_does_not_reduce_availability():
    insert_pending_reservation(
        name="John Doe",
        car_number="ABC-123",
        start_time="2026-03-20T08:00:00",
        end_time="2026-03-20T12:00:00",
    )

    free = count_free_lots(
        "2026-03-20T08:00:00",
        "2026-03-20T12:00:00",
    )

    # Pending reservations should not affect availability
    assert free == 20

def test_approve_reservation_updates_status_and_approval_time():
    reservation_id = insert_pending_reservation(
        name="Jane Doe",
        car_number="XYZ-999",
        start_time="2026-03-21T08:00:00",
        end_time="2026-03-21T12:00:00",
    )

    success = approve_reservation(reservation_id)

    assert success is True

    reservation = get_reservation_by_id(reservation_id)
    assert reservation is not None
    assert reservation["status"] == "APPROVED"
    assert reservation["approval_time"] is not None

def test_reject_reservation_updates_status():
    reservation_id = insert_pending_reservation(
        name="Mark Doe",
        car_number="REJ-123",
        start_time="2026-03-22T08:00:00",
        end_time="2026-03-22T12:00:00",
    )

    success = reject_reservation(reservation_id)

    assert success is True

    reservation = get_reservation_by_id(reservation_id)
    assert reservation is not None
    assert reservation["status"] == "REJECTED"