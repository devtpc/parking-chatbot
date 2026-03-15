from pathlib import Path


APPROVED_RESERVATIONS_FILE = Path("data/approved_reservations.txt")


def append_approved_reservation_to_file(
    name: str,
    car_number: str,
    start_time: str,
    end_time: str,
    approval_time: str,
) -> None:
    line = f"{name} | {car_number} | {start_time} - {end_time} | {approval_time}\n"

    APPROVED_RESERVATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with APPROVED_RESERVATIONS_FILE.open("a", encoding="utf-8") as f:
        f.write(line)