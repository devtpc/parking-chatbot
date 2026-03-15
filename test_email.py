from src.email_notifier import send_admin_reservation_email

send_admin_reservation_email(
    reservation_id=1,
    name="John Doe",
    car_number="ABC-123",
    start_time="2026-03-20T08:00:00",
    end_time="2026-03-20T12:00:00",
)