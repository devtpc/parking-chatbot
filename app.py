import streamlit as st
from dotenv import load_dotenv

from src.workflow import build_workflow

load_dotenv()

st.set_page_config(page_title="Parking Chatbot", page_icon="🚗")
st.title("Parking Reservation Chatbot")

if "workflow" not in st.session_state:
    st.session_state.workflow = build_workflow()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask about parking or make a reservation")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    result = st.session_state.workflow.invoke(
        {
            "role": "user",
            "user_input": user_input,
            "chat_history": st.session_state.chat_history,
            "response": "",
            "reservation_id": None,
            "notify_admin": False,
            "approved_reservation_id": None,
            "should_record": False,
        }
    )

    reply = result["response"]

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.chat_history.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.markdown(reply)