# Parking Reservation Chatbot --- Stage 4

## Presentation

A presentation with screenshots of the system and workflows is available
here:

**[artifacts/DeckChatbot.pptx](artifacts/DeckChatbot.pptx)**

------------------------------------------------------------------------

## Note

This project is a homework assignment. Although the repository is
public, it is **not intended for production use**.

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
-   orchestrate the reservation workflow using LangGraph

The system demonstrates:

-   Retrieval Augmented Generation (RAG)
-   LLM agents with tool usage
-   two-agent architecture (user agent + admin agent)
-   LangGraph workflow orchestration
-   vector database retrieval
-   SQLite database usage
-   parking lot capacity management
-   external MCP-style service integration
-   email notification to administrator
-   guardrails to prevent exposure of internal data

# Tech Stack

-   Python
-   LangChain
-   LangGraph
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
    │   ├── workflow.py              # LangGraph workflow orchestration
    │   └── mcp_client.py            # Client communicating with MCP server
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
    ├── artifacts/
    │   └── DeckChatbot.pptx         # Presentation with screenshots
    │
    ├── tests/
    │   ├── conftest.py
    │   ├── test_database.py
    │   ├── test_rag.py
    │   └── test_admin_agent.py

# Architecture

Stage 4 introduces **workflow orchestration using LangGraph**.

Instead of components calling each other directly, the system now
coordinates the reservation process through a **state graph workflow**.

The system still uses **two LLM agents**, but orchestration is handled
by the LangGraph workflow layer.

Main components:

-   User Agent
-   Admin Agent
-   LangGraph workflow orchestration
-   Lightweight MCP reservation server

## LangGraph Workflow

The workflow is implemented as a **single LangGraph graph** with three
nodes:

1.  User Interaction Node
2.  Administrator Approval Node
3.  Data Recording Node

User requests and administrator actions enter the graph and are routed
through the appropriate workflow path.

### User Reservation Flow

START\
→ User Interaction Node\
→ Administrator Approval Node (admin notification)\
→ END

### Administrator Approval Flow

START\
→ Administrator Approval Node\
→ Data Recording Node\
→ END

The orchestration layer coordinates:

-   reservation submission
-   administrator notification
-   reservation approval
-   external reservation recording

This separation improves **modularity, maintainability, and system
clarity**.

# Reservation Workflow (Stage 4)

1.  User requests parking reservation via chatbot
2.  Reservation stored in SQLite database with status:


```
    PENDING_APPROVAL
```

3.  LangGraph workflow triggers administrator notification
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
10. LangGraph workflow triggers the data recording node
11. Reservation details are sent to the MCP server
12. MCP server writes the reservation to:


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

# Security

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


