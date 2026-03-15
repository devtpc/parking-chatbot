import os
from pathlib import Path
import sqlite3
from datetime import datetime, UTC

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / os.getenv("PARKING_DB_FILE", "sqlite.db")


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            DROP TABLE IF EXISTS reservation_requests;
            DROP TABLE IF EXISTS parking_lots;

            CREATE TABLE parking_lots (
                lot_id INTEGER PRIMARY KEY
            );

            CREATE TABLE reservation_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                car_number TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                assigned_lot INTEGER,
                approval_time TEXT,
                FOREIGN KEY (assigned_lot) REFERENCES parking_lots(lot_id)
            );
            """
        )

        conn.executemany(
            "INSERT INTO parking_lots (lot_id) VALUES (?)",
            [(i,) for i in range(1, 21)],
        )
        conn.commit()


def count_free_lots(start_time: str, end_time: str) -> int:
    query = """
    SELECT COUNT(*) AS free_count
    FROM parking_lots pl
    WHERE NOT EXISTS (
        SELECT 1
        FROM reservation_requests rr
        WHERE rr.assigned_lot = pl.lot_id
          AND rr.status = 'APPROVED'
          AND rr.start_time < ?
          AND rr.end_time > ?
    )
    """
    with get_connection() as conn:
        row = conn.execute(query, (end_time, start_time)).fetchone()
        return row["free_count"]


def insert_pending_reservation(
    name: str,
    car_number: str,
    start_time: str,
    end_time: str,
) -> int:
    now = datetime.now(UTC).isoformat(timespec="seconds")

    query = """
    INSERT INTO reservation_requests (
        name, car_number, start_time, end_time, status, created_at, assigned_lot, approval_time
    )
    VALUES (?, ?, ?, ?, 'PENDING_APPROVAL', ?, NULL, NULL)
    """
    with get_connection() as conn:
        cur = conn.execute(query, (name, car_number, start_time, end_time, now))
        conn.commit()
        return cur.lastrowid

def get_pending_reservations():
    query = """
    SELECT id, name, car_number, start_time, end_time, created_at
    FROM reservation_requests
    WHERE status = 'PENDING_APPROVAL'
    ORDER BY created_at ASC
    """
    with get_connection() as conn:
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]

def get_reservation_by_id(reservation_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, name, car_number, start_time, end_time, status, created_at, assigned_lot, approval_time
            FROM reservation_requests
            WHERE id = ?
            """,
            (reservation_id,),
        ).fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "name": row[1],
        "car_number": row[2],
        "start_time": row[3],
        "end_time": row[4],
        "status": row[5],
        "created_at": row[6],
        "assigned_lot": row[7],
        "approval_time": row[8],
    }

def reject_reservation(reservation_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE reservation_requests
            SET status = ?
            WHERE id = ? AND status = ?
            """,
            ("REJECTED", reservation_id, "PENDING_APPROVAL"),
        )
        conn.commit()
        return cursor.rowcount > 0

def find_free_lot(start_time: str, end_time: str) -> int | None:
    query = """
    SELECT pl.lot_id
    FROM parking_lots pl
    WHERE NOT EXISTS (
        SELECT 1
        FROM reservation_requests rr
        WHERE rr.assigned_lot = pl.lot_id
          AND rr.status = 'APPROVED'
          AND rr.start_time < ?
          AND rr.end_time > ?
    )
    LIMIT 1
    """

    with get_connection() as conn:
        row = conn.execute(query, (end_time, start_time)).fetchone()
        return row["lot_id"] if row else None


def approve_reservation(reservation_id: int) -> bool:
    approval_time = datetime.now(UTC).isoformat()

    with get_connection() as conn:

        reservation = conn.execute(
            """
            SELECT start_time, end_time
            FROM reservation_requests
            WHERE id = ? AND status = ?
            """,
            (reservation_id, "PENDING_APPROVAL"),
        ).fetchone()

        if not reservation:
            return False

        lot = conn.execute(
            """
            SELECT pl.lot_id
            FROM parking_lots pl
            WHERE NOT EXISTS (
                SELECT 1
                FROM reservation_requests rr
                WHERE rr.assigned_lot = pl.lot_id
                  AND rr.status = 'APPROVED'
                  AND rr.start_time < ?
                  AND rr.end_time > ?
            )
            LIMIT 1
            """,
            (reservation["end_time"], reservation["start_time"]),
        ).fetchone()

        if not lot:
            return False

        cursor = conn.execute(
            """
            UPDATE reservation_requests
            SET status = ?, approval_time = ?, assigned_lot = ?
            WHERE id = ?
            """,
            ("APPROVED", approval_time, lot["lot_id"], reservation_id),
        )

        conn.commit()
        return cursor.rowcount > 0

def get_reservations_by_status(status: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, name, car_number, start_time, end_time, status, created_at, assigned_lot, approval_time
            FROM reservation_requests
            WHERE status = ?
            ORDER BY created_at DESC
            """,
            (status,),
        ).fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "car_number": row[2],
            "start_time": row[3],
            "end_time": row[4],
            "status": row[5],
            "created_at": row[6],
            "assigned_lot": row[7],
            "approval_time": row[8],
        }
        for row in rows
    ]
