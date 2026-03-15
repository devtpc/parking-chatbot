import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", SMTP_USER)

EMAIL_DEBUG = os.getenv("EMAIL_DEBUG", "false").lower() == "true"


def send_admin_reservation_email(
    reservation_id: int,
    name: str,
    car_number: str,
    start_time: str,
    end_time: str,
):
    subject = f"Parking reservation request #{reservation_id}"

    body = f"""
New parking reservation request

Reservation ID: {reservation_id}

Name: {name}
Car number: {car_number}

Start time: {start_time}
End time: {end_time}

Open admin dashboard to approve or reject:
http://localhost:8501/admin
""".strip()

    if EMAIL_DEBUG:
        print("\n=== EMAIL DEBUG MODE ===")
        print(f"To: {ADMIN_EMAIL}")
        print(f"From: {SENDER_EMAIL}")
        print(f"Subject: {subject}")
        print()
        print(body)
        print("=== END EMAIL ===\n")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = ADMIN_EMAIL
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)