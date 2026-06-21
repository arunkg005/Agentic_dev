---
title: NGO Campaign Copilot
emoji: 🚀
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
---

# AI Campaign Copilot 🚀

An AI-powered strategic planning assistant designed for coordinators. It transforms campaign ideas into structured, professional, and downloadable execution plans—complete with SMART objectives, action timelines, budget/resource allocation, volunteer roles, risk mitigation, and key success metrics.

## 🌟 Project Vision & Motivation

NGO coordinators and field volunteers often spend countless hours drafting operational plans, estimating logistics, and structuring basic budgets before they can even begin their actual groundwork. This project was built to solve that exact bottleneck. The goal is to provide an accessible "copilot" that instantly generates a structured, professional baseline plan from a few simple inputs—freeing up coordinators to focus on what matters most: community engagement, execution, and impact.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-4285F4?logo=google&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3-FF6600?logo=meta&logoColor=white)

---

## ⚡ Key Features

* **Multi-Stage Orchestration:** Runs a 6-module AI pipeline sequentially to cover all aspects of campaign planning (Objectives → Timeline → Resources → Volunteers → Risks → Metrics).
* **Real-Time Streaming:** Streams plan-generation progress updates to the frontend via NDJSON.
* **Interactive AI Chat:** Allows real-time refinement of the generated plan using natural language (e.g., "increase the budget", "add a risk for bad weather").
* **Multi-Format Export:** Instant downloads as Markdown (`.md`), Word Document (`.docx`), or PDF (`.pdf`).
* **Dual LLM Failover:** Routes primary requests to Google Gemini with automatic, seamless fallback to Groq (Llama 3.3).
* **Modern Premium UI:** Charcoal-and-emerald dark mode with responsive glassmorphism and subtle micro-animations.

---

## 🎯 Current State & Scope

This project is currently a **highly polished Minimum Viable Product (MVP)** and proof-of-concept. It successfully demonstrates complex AI orchestration, modular architecture, and dynamic UI streaming, providing a strong baseline for automated campaign planning.

### 🚀 Future Enhancements (Scope for Production)
While structurally sound and fully functional as a prototype, the following architectural upgrades would elevate this tool to a production-ready application for unsupervised, large-scale NGO deployment:

* **Persistent Database Integration:** Transitioning from a stateless architecture to a persistent database (e.g., PostgreSQL, Firebase) to enable user authentication, project saving, and collaborative editing.
* **Dynamic Data Integrations:** Upgrading the current heuristic-based budget and resource estimations to pull real-time external data (e.g., live local pricing, geographic logistics) for pinpoint accuracy.
* **Enterprise API Scaling:** Migrating from free-tier LLM API keys to a high-capacity, paid-tier API with token pooling to support high-traffic, concurrent usage without hitting rate limits.

---

## 🔒 Security & Safety Features

This project implements rigorous security and safety boundaries to ensure responsible AI usage and API protection:

* **Prompt Injection Defenses:** Deep regex heuristic checks actively scan user inputs for malicious commands designed to override system instructions, extract sensitive keys, force roleplay bypasses, or leak internal prompts. Any suspicious input immediately aborts the pipeline.
* **Input Sanitization:** All user-provided fields undergo rigorous HTML tag stripping to neutralize Cross-Site Scripting (XSS) vectors and prevent downstream document corruption during Word/PDF compilation.
* **Global Rate Limiting:** A robust token-bucket rate limiter restricts the frequency of requests (e.g., 5 requests per 60 seconds) to prevent Denial of Wallet (DoW) attacks and protect backend API quotas.
* **Granular Error Handling:** Rate limits from upstream LLM providers (e.g., HTTP 429 errors) are safely caught and presented to the user as clean, generic fallback messages rather than raw API traces, preventing internal endpoint or SDK information leakage.
* **Provider-Level Safety Enforcements:** Hardcoded system prompts restrict the LLM solely to campaign planning topics. Provider safety filters are fully enabled to reject sexually explicit, dangerous, or harassing content generations.

---

## 🏗️ Architecture

```
┌───────────────────────────────────────────────────────┐
│                   Frontend (Vanilla JS)               │
│  ┌─────────────────────────────────────────────────┐  │
│  │           Campaign Agent (Orchestrator)         │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │  │
│  │  │Objectives│ │ Timeline │ │    Resources     │ │  │
│  │  └──────────┘ └──────────┘ └──────────────────┘ │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │  │
│  │  │Volunteers│ │  Risks   │ │     Metrics      │ │  │
│  │  └──────────┘ └──────────┘ └──────────────────┘ │  │
│  └─────────────────────────────────────────────────┘  │
│       │                                               │
│       ▼                                               │
│  ┌─────────────────────────────────────────────────┐  │
│  │       Compiler (MD → PDF / DOCX / HTML)         │  │
│  └─────────────────────────────────────────────────┘  │
│       │                                               │
│       ▼                                               │
│  ┌──────────────┐                                     │
│  │  LLM Router  │ Gemini (primary) ↔ Groq (fallback)  │
│  └──────────────┘                                     │
└───────────────────────────────────────────────────────┘
```

---

## 🛠️ Quick Start

### 1. Clone & Navigate
```bash
git clone https://github.com/arunkg005/Agentic_dev.git
cd Agentic_dev
```

### 2. Set Up Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
Copy the example environment template:
```bash
cp .env.example .env
```
Open `.env` and configure your API keys (at least one is required):
```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Launch
```bash
python main.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your web browser.

---

## 📁 Project Structure

```
├── main.py              # FastAPI server and main endpoints
├── agent.py             # Orchestrates the 6-module generation pipeline
├── config.py            # LLM API configuration & model routing
├── security.py          # Input sanitization, prompt injection filter, rate limiting
├── requirements.txt     # Python package requirements
├── .env.example         # Template for environment variables
├── modules/             # Pipeline components
│   ├── objectives.py    # SMART Objectives generator
│   ├── timeline.py      # Timeline & milestones generator
│   ├── resources.py     # Budget & materials estimator
│   ├── volunteers.py    # Staffing & roles planner
│   ├── risks.py         # Risk identification & mitigation generator
│   ├── metrics.py       # Metrics & success indicators planner
│   └── compiler.py      # Combines modules, handles HTML/PDF/Word rendering & chat updates
├── static/              # Frontend web assets
│   ├── index.html       # Single-page interface
│   ├── style.css        # Premium dark glassmorphic styling
│   └── script.js        # Form validation, SSE streaming, and chat refinement logic
└── output/              # Local storage directory for compiled reports (gitignored)
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
