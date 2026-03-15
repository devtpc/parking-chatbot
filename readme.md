#
# Parking Reservation Chatbot — Stage 2

## Note

This project is a homework assignment.
Although the repository is public, it is **not intended for production use**.

The chatbot implements a hypothetical parking reservation system for a company.

# Overview

This project implements a chatbot that helps employees interact with
**XYZ Company's parking lot system**.

The chatbot can:

- answer parking-related questions
- check parking availability
- collect parking reservation requests
- escalate reservation requests to a human administrator

The system demonstrates:

- Retrieval Augmented Generation (RAG)
- LLM agents with tool usage
- two-agent architecture (user agent + admin agent)
- vector database retrieval
- SQLite database usage
- email notification to administrator
- guardrails to prevent exposure of internal data


# Tech Stack

- Python
- LangChain
- OpenAI (gpt-4o-mini)
- OpenAI embeddings (text-embedding-3-small)
- Chroma vector database
- SQLite
- Streamlit
- pytest
- SMTP email notification (Brevo)


# Project Structure

```
parking/
│
├── app.py
├── init.py
├── requirements.txt
│
├── src/
│   ├── chatbot.py
│   ├── admin_agent.py
│   ├── database.py
│   ├── email_notifier.py
│   └── rag.py
│
├── pages/
│   └── admin.py
│
├── evaluation/
│   └── evaluate_rag.py
│
├── data/
│   └── parking_policy.md
│
├── tests/
│   ├── conftest.py
│   ├── test_database.py
│   ├── test_rag.py
│   └── test_admin_agent.py
```

# Architecture

The system uses **two LLM agents**.

## User Agent

Handles employee interaction:

- parking questions
- parking rules
- parking availability
- reservation request collection

When a reservation request is created:

User request  
- reservation stored in database  
- notification sent to admin agent


## Admin Agent

The administrator interacts with the system through a second agent.

The admin agent can:
- sent email notification to human for approval
- list pending reservation requests
- approve a reservation (mock in Stage 2)
- reject a reservation (mock in Stage 2)

Actual execution of approval/rejection will be implemented in **Stage 3**.


# Setup

## Install dependencies
```
pip install -r requirements.txt
```

## Create `.env` file
```
OPENAI_API_KEY=your_api_key_here

For email notifications (Brevo SMTP):

SMTP_HOST=smtp-relay.brevo.com  
SMTP_PORT=587  
SMTP_USER=your_smtp_login  
SMTP_PASSWORD=your_smtp_key  

SENDER_EMAIL=sender@example.com  
ADMIN_EMAIL=admin@example.com  

EMAIL_DEBUG=false
```
If EMAIL_DEBUG=true, the email content will be printed to the console instead of being sent.


## Initialize system
```
python init.py
```
This creates the SQLite database and initializes parking lot data.


# Run the Chatbot
```
streamlit run app.py
```
Two Streamlit interfaces are available:

| Page | Purpose |
|------|--------|
| Main page | User chatbot |
| Admin page | Administrator approval interface |


# Reservation Workflow (Stage 2)

1. User requests parking reservation via chatbot
2. Reservation request stored in SQLite database
3. Email notification sent to administrator
4. Administrator opens admin interface
5. Admin agent lists pending reservations
6. Admin can approve/reject reservation (mock response)

Database status remains **PENDING_APPROVAL** in Stage 2.



# Run Tests
```
pytest
```


# RAG Evaluation
```
python evaluate_rag.py
```
This prints simple **Recall@K** and **Precision@K** metrics for retrieval quality.


# Guardrails

The chatbot prevents exposure of internal system data.

Protection includes:

- system prompt restrictions
- input filtering for sensitive queries (e.g. database, dump, system, prompt)
- refusal of unrelated questions


# Limitations (Stage 2)

- Reservation approval/rejection is **mocked**
- Parking lot assignment not yet implemented
- Reservation confirmation file not yet generated

These features will be implemented in **Stage 3**.
