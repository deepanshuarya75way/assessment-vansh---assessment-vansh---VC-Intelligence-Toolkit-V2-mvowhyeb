# VC Intelligence Toolkit

> **An AI-powered decision-support platform that augments VC Fund's early investment workflow — from discovering promising AI startups to evaluating technical moats and recommending the right founder pathway.**

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![React](https://img.shields.io/badge/React-Frontend-61DAFB)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange)
![Groq](https://img.shields.io/badge/Groq-LLM-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-blue)

---

## Overview

VC Intelligence Toolkit is a full-stack AI platform designed specifically for **VC Fund**, an operator-led AI venture capital firm.

Rather than building isolated AI agents, this project models the actual workflow followed by an investment team. It combines three connected decision-support systems into a single application that assists analysts throughout the early investment lifecycle.
> 📖 **For developers:** Explore the complete technical documentation, architecture, and implementation details in the **[Technical README](https://github.com/vanshbhutani1405/VC-Intelligence-Toolkit/tree/main/vc-intelligence-toolkit#readme)**.

```text
Discover
    ↓
Evaluate
    ↓
Route
```

Every module can run independently or as part of a complete end-to-end pipeline.

---

# Modules

## 🛰 Corridor Atlas

Discover high-potential AI startups from GitHub, Hacker News, and arXiv.

The system learns VC Fund's investment thesis from its existing portfolio, performs semantic similarity search using embeddings, explains **"Why VC?"**, assigns confidence scores, and creates structured candidate reports.

---

## 🧠 AI MoatLens

An AI-native diligence engine built specifically for evaluating AI startups.

Instead of relying on a single LLM response, multiple agents debate both the investment opportunity and potential risks before producing a structured diligence report covering:

- Wrapper Risk
- Model Dependency
- Data Moat
- Technical Defensibility
- AI Differentiation
- Human Review Recommendation

---

## 🧭 SwarmSpace Navigator

Routes founders to the most appropriate VC Fund pathway.

Instead of simply recommending **Invest** or **Reject**, Navigator analyzes founder applications and recommends pathways such as:

- Investment
- AI Studio
- Research Lab
- Community
- Monitor

while generating reasoning, interview questions, confidence scores, and missing evidence.

---

# Architecture

The application follows a connected workflow:

```text
GitHub
Hacker News
arXiv
        │
        ▼
Corridor Atlas
        │
        ▼
Candidate Database
        │
        ▼
AI MoatLens
        │
        ▼
Diligence Report
        │
        ▼
SwarmSpace Navigator
        │
        ▼
Final Recommendation
```

Each module stores structured outputs inside PostgreSQL, allowing downstream modules to continue the workflow while still remaining independently runnable.

---

# Technology Stack

### Frontend

- React
- Vite
- Tailwind CSS
- shadcn/ui

### Backend

- FastAPI
- LangGraph
- SQLAlchemy

### AI Stack

- Groq LLM
- sentence-transformers
- pgvector
- PostgreSQL

### Deployment

- Frontend → Vercel
- Backend → Render
- Database → Supabase PostgreSQL

---

# Features

- Multi-Agent AI Workflows
- Semantic Startup Discovery
- AI-Specific Investment Diligence
- Founder Routing Recommendations
- Explainable AI Decisions
- Human-in-the-Loop Design
- Visible Reasoning Logs
- Modern Full-Stack Architecture

---

# Quick Start

## Backend

```bash
cd backend

python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt

uvicorn main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## Environment Variables

Create a `.env` file using `.env.example`.

Required variables:

- GROQ_API_KEY
- DATABASE_URL
- GITHUB_TOKEN
- SUPABASE_URL
- SUPABASE_KEY
- MODEL_NAME
- EMBEDDING_MODEL
- LOG_LEVEL

---

# API Endpoints

| Module | Endpoint |
|----------|-------------------------------|
| Corridor Atlas | `/api/corridor/discover` |
| AI MoatLens | `/api/moatlens/evaluate` |
| SwarmSpace Navigator | `/api/navigator/route` |
| History | `/api/history` |

---

# Project Structure

```
backend/
frontend/
docs/
scripts/
```

---

# Assignment Context

This project was built as part of the **VC Fund Technical Intern Assignment**.

The objective was not simply to build AI agents, but to design practical decision-support systems tailored specifically to VC Fund's operator-led investment workflow.

---
