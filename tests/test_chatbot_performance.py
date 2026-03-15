import time
from src.chatbot import build_agent, chat


def test_chatbot_response_time():
    agent = build_agent()

    start = time.perf_counter()

    response = chat(
        agent=agent,
        user_input="How many parking spaces are there?",
        chat_history=[]
    )

    elapsed = time.perf_counter() - start

    assert response is not None
    assert elapsed < 10   # generous threshold