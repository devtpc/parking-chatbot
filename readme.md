# Parking Reservation Chatbot -- Stage 1

## Note

This project is a project homework task. Although it's public, it's not intended to use in production.
Chatbot implements a hypotetical parking reservation system at a company

## Overview

This project implements a chatbot that helps employees interact with
**XYZ Company's parking lot system**.\
The chatbot can answer parking-related questions and collect reservation
requests through conversation.

The system demonstrates: - Retrieval Augmented Generation (RAG) - LLM
agent with tool usage - Vector database retrieval - SQLite database
usage - Guardrails to prevent exposure of internal data

------------------------------------------------------------------------

## Tech Stack

-   Python
-   LangChain
-   OpenAI (gpt-4o-mini)
-   OpenAI embeddings (text-embedding-3-small)
-   Chroma vector database
-   SQLite
-   Streamlit
-   pytest

------------------------------------------------------------------------

## Project Structure

```
parking/
│
├── app.py
├── init.py
├── requirements.txt
│
├── src/
│   ├── chatbot.py
│   ├── database.py
│   └── rag.py
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
│   └── test_rag.py
```

---

------------------------------------------------------------------------

## Setup

1.  Install dependencies

```
 pip install -r requirements.txt
```
   
2.  Create `.env` file and place your OPEN_AI API key there

```
    OPENAI_API_KEY=your_api_key_here
```


3. Initialize system

```
    python init.py
```

------------------------------------------------------------------------

## Run the Chatbot

    streamlit run app.py

------------------------------------------------------------------------

## Run Tests

    pytest

------------------------------------------------------------------------

## RAG Evaluation

    python evaluate_rag.py

This prints simple **Recall@K** and **Precision@K** metrics for
retrieval quality.

------------------------------------------------------------------------

## Guardrails

The chatbot prevents exposure of internal system data.

Protection includes: 
- system prompt restrictions 
- input filtering for sensitive queries (e.g.dumps, system, etc.)
