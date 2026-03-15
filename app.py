import streamlit as st
from dotenv import load_dotenv

from src.chatbot import build_agent, chat

load_dotenv()

st.set_page_config(page_title="Parking Chatbot", page_icon="🚗")
st.title("Parking Reservation Chatbot")

if "agent" not in st.session_state:
    st.session_state.agent = build_agent()

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

    reply = chat(
        agent=st.session_state.agent,
        user_input=user_input,
        chat_history=st.session_state.chat_history,
    )

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.chat_history.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.markdown(reply)