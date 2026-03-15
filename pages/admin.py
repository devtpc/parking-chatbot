import streamlit as st

from src.database import get_pending_reservations
from src.workflow import build_workflow

st.set_page_config(page_title="Admin – Parking Reservations", page_icon="🛠")
st.title("Admin – Reservation Approval")

if "admin_workflow" not in st.session_state:
    st.session_state.admin_workflow = build_workflow()

if "admin_messages" not in st.session_state:
    st.session_state.admin_messages = []

if "last_pending_count" not in st.session_state:
    st.session_state.last_pending_count = 0

pending = get_pending_reservations()
pending_count = len(pending)

if pending_count > st.session_state.last_pending_count:
    st.toast("New reservation request received")

st.session_state.last_pending_count = pending_count

st.subheader("Pending requests")
if not pending:
    st.info("No pending reservations.")
else:
    for r in pending:
        st.markdown(
            f"- **ID {r['id']}** | {r['name']} | {r['car_number']} | "
            f"{r['start_time']} → {r['end_time']}"
        )

st.divider()
st.subheader("Admin chat")

for message in st.session_state.admin_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input(
    "Example: show pending reservations / approve reservation 3 / reject reservation 3"
)

if user_input:
    st.session_state.admin_messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    result = st.session_state.admin_workflow.invoke(
        {
            "role": "admin",
            "user_input": user_input,
            "chat_history": st.session_state.admin_messages,
            "response": "",
            "reservation_id": None,
            "notify_admin": False,
            "approved_reservation_id": None,
            "should_record": False,
        }
    )

    reply = result["response"]

    st.session_state.admin_messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.markdown(reply)

    st.rerun()