import os
from pathlib import Path

from src.database import (
    init_database,
    count_free_lots,
    insert_pending_reservation,
)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DB_PATH = DATA_DIR / "sqlite.db"


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