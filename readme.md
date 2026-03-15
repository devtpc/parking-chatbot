# Parking Reservation Chatbot --- Stage 3

## Note

This project is a homework assignment.\
Although the repository is public, it is **not intended for production
use**.

The chatbot implements a hypothetical parking reservation system for a
company.


# Overview

This project implements a chatbot that helps employees interact with
**XYZ Company's parking lot system**.

The chatbot can:

-   answer parking-related questions
-   check parking availability
-   collect parking reservation requests
-   escalate reservation requests to a human administrator
-   process approved reservations through a lightweight MCP-style server

The system demonstrates:

-   Retrieval Augmented Generation (RAG)
-   LLM agents with tool usage
-   two-agent architecture (user agent + admin agent)
-   vector database retrieval
-   SQLite database usage
-   parking lot capacity management
-   external MCP-style service integration
-   email notification to administrator
-   guardrails to prevent exposure of internal data



# Tech Stack

-   Python
-   LangChain
-   OpenAI (gpt-4o-mini)
-   OpenAI embeddings (text-embedding-3-small)
-   Chroma vector database
-   SQLite
-   Streamlit
-   FastAPI (lightweight MCP server)
-   pytest
-   SMTP email notification (Brevo)

Additional libraries:

-   requests
-   uvicorn



# Project Structure

    parking/
    │
    ├── app.py
    ├── init.py
    ├── requirements.txt
    │
    ├── mcp_server.py                # Lightweight MCP-style reservation server
    │
    ├── src/
    │   ├── chatbot.py
    │   ├── admin_agent.py
    │   ├── database.py
    │   ├── email_notifier.py
    │   ├── rag.py
    │   └── mcp_client.py            # Client for communicating with MCP server
    │
    ├── pages/
    │   └── admin.py
    │
    ├── evaluation/
    │   └── evaluate_rag.py
    │
    ├── data/
    │   ├── parking_policy.md
    │   └── approved_reservations.txt
    │
    ├── tests/
    │   ├── conftest.py
    │   ├── test_database.py
    │   ├── test_rag.py
    │   └── test_admin_agent.py



# Architecture

The system uses **two LLM agents** and a lightweight **reservation
processing server**.

## User Agent

Handles employee interaction:

-   parking questions
-   parking rules
-   parking availability
-   reservation request collection

When a reservation request is created:
-   reservation stored in database
-   admin agent is called


The reservation remains in status:

    PENDING_APPROVAL

until a human administrator processes it.



## Admin Agent

The administrator interacts with the system through a second agent.

The admin agent can:
-   send notification to human administrator
-   list pending reservations
-   list approved reservations
-   list rejected reservations
-   approve reservations
-   reject reservations


## Lightweight MCP Server

Stage 3 introduces a **separate service responsible for processing confirmed reservations**.

Instead of writing reservation confirmations directly from the chatbot
application, the system sends a request to a lightweight server
implemented with **FastAPI**.

Responsibilities of the MCP server:

-   receive confirmed reservation data
-   validate API key authentication
-   append reservation details to a file

File format:

    Name | Car Number | Reservation Period | Approval Time

Example:

    John Doe | ABC-123 | 2026-03-20T08:00:00 - 2026-03-20T12:00:00 | 2026-03-15T20:00:00+00:00



# Reservation Workflow (Stage 3)

1.  User requests parking reservation via chatbot
2.  Reservation stored in SQLite database with status:

```
PENDING_APPROVAL
```   

3.  Email notification sent to administrator
4.  Administrator opens admin interface
5.  Admin agent lists pending reservations
6.  Administrator approves or rejects reservation

If **approved**:

7.  System checks available parking capacity
8.  A free parking lot is assigned
9.  Reservation status updated to:

```
    APPROVED
```


10. Reservation details are sent to the MCP server
11. MCP server writes the reservation to:

```
    data/approved_reservations.txt
```


If **rejected**:

-   reservation status becomes `REJECTED`
-   no file entry is created


# Parking Capacity Control

To prevent overbooking, the system enforces parking lot capacity.

Before approval:

-   the system checks available parking lots for the requested time
    interval
-   overlapping approved reservations are considered
-   if no free lot exists, approval is denied

Example response:

    Reservation cannot be approved. All parking spaces are occupied for this period.

When a reservation is approved:

-   a free parking lot is automatically assigned
-   the lot number is stored in the database


# Security (Stage 3)

The MCP server is protected using **API key authentication**.

Authentication mechanism:

-   API key stored in `.env`
-   client sends key in HTTP header
-   server verifies the key before accepting requests

Header used:

    x-api-key

Unauthorized requests return:

    HTTP 401 Unauthorized

This ensures the reservation server is **protected against unauthorized
access**.

# Setup

## Install dependencies

    pip install -r requirements.txt


## Create `.env` file

    OPENAI_API_KEY=your_api_key_here

    # Email notifications (Brevo SMTP)

    SMTP_HOST=smtp-relay.brevo.com
    SMTP_PORT=587
    SMTP_USER=your_smtp_login
    SMTP_PASSWORD=your_smtp_key

    SENDER_EMAIL=sender@example.com
    ADMIN_EMAIL=admin@example.com

    EMAIL_DEBUG=false

    # MCP server configuration

    MCP_API_KEY=super-secret-local-key

If `EMAIL_DEBUG=true`, email content will be printed to console instead
of being sent.


# Initialize system

    python init.py

This creates the SQLite database and initializes parking lot data.


# Start MCP Server

Run the reservation processing server:

    uvicorn mcp_server:app --reload --port 8001

Swagger documentation will be available at:

    http://localhost:8001/docs


# Run the Chatbot

In a separate terminal:

    streamlit run app.py

Two Streamlit interfaces are available:

  Page         Purpose
  ------------ ----------------------------------
  Main page    User chatbot
  Admin page   Administrator approval interface


# Run Tests

    pytest

Tests cover:

-   database logic
-   RAG retrieval
-   admin agent functionality


# RAG Evaluation

    python evaluate_rag.py

This prints simple **Recall@K** and **Precision@K** metrics for
retrieval quality.


# Guardrails

The chatbot prevents exposure of internal system data.

Protection includes:

-   system prompt restrictions
-   input filtering for sensitive queries (e.g. database, dump, system,
    prompt)
-   refusal of unrelated questions


