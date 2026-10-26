# 🚀 VC Intelligence Toolkit

> **An AI-powered decision-support platform built for VC Fund to augment the investment workflow from startup discovery to AI diligence and founder routing.**

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=flat-square)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-LLM-red?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791?style=flat-square)

---

## 📌 Overview

VC Intelligence Toolkit is a full-stack AI platform designed specifically for **VC Fund**. It models the early investment workflow through **three connected but independently runnable AI modules**.

```text
Discover
    ↓
Evaluate
    ↓
Route
```

---

## 🏗️ System Architecture

<p align="center">
<img src="docs/VC%20System%20Architecture.png" width="700">
</p>

---

## 🛰️ Corridor Atlas

Discovers promising AI startups from **GitHub, Hacker News and arXiv**, compares them with VC Fund's portfolio using semantic search, and generates **Why VC?** explanations with confidence scores.

<p align="center">
<img src="docs/CorridorAtlas%20Agent%20Diagram.png" width="700">
</p>

---

## 🧠 AI MoatLens

A multi-agent diligence engine that evaluates:

- Wrapper Risk
- Data Moat
- Model Dependency
- Technical Defensibility

using **Bull → Bear → Reflection → Synthesis** reasoning.

<p align="center">
<img src="docs/MoatLens%20Agent%20Diagram.png" width="700">
</p>

---

## 🧭 SwarmSpace Navigator

Analyzes founder applications and recommends the best VC pathway:

- Investment
- AI Studio
- Research Lab
- Community
- Monitor

along with reasoning, interview questions, confidence, and human review guidance.

<p align="center">
<img src="docs/SwarmSpace%20Agent%20Diagram.png" width="700">
</p>

---

## ⚙️ Tech Stack

| Layer | Technology |
|--------|------------|
| Frontend | React, Vite, TailwindCSS, shadcn/ui |
| Backend | FastAPI, LangGraph |
| AI | Groq + sentence-transformers |
| Database | Supabase PostgreSQL + pgvector |
| ORM | SQLAlchemy |
| Deployment | Vercel + Render + Supabase |

---

## 📖 Documentation

- 📄 **Technical Writeup:** [docs/writeup.md](docs/writeup.md)

---

## 🚀 Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## 📌 Assignment

Built as part of the **VC Fund Technical Intern Assignment** to demonstrate practical AI-powered decision-support systems tailored to an operator-led venture capital firm's workflow.

---

<p align="center">

**⭐ Built with FastAPI • LangGraph • Groq • React • PostgreSQL ⭐**

</p>
