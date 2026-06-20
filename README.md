# AI Campaign Copilot 🚀

An AI-powered strategic planning assistant that helps NGO coordinators transform campaign ideas into professional, downloadable execution plans — complete with objectives, timelines, budgets, volunteer roles, risk assessments, and success metrics.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi&logoColor=white)
![Gemini](https://img.shields.io/badge/Google_Gemini-2.0_Flash-4285F4?logo=google&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3-FF6600?logo=meta&logoColor=white)

---

## ✨ Features

| Feature | Description |
|---|---|
| **Multi-Module AI Pipeline** | 6 specialized AI modules (Objectives → Timeline → Resources → Volunteers → Risks → Metrics) orchestrated by a central agent |
| **Real-Time Streaming** | NDJSON-streamed progress updates during plan generation |
| **AI Refinement Chat** | Built-in chat interface to iteratively refine the generated plan with natural language prompts |
| **Multi-Format Export** | Download plans as Markdown (.md), PDF (.pdf), or Word (.docx) |
| **Dual LLM Provider** | Supports Google Gemini and Groq (Llama 3.3) with automatic failover |
| **Security First** | Prompt injection detection, input sanitization, rate limiting, and system-level safety filters |
| **Premium Dark UI** | Glassmorphic charcoal + emerald design with micro-animations |

---

## 🖥️ Screenshots

> Generate a campaign plan, refine it with AI chat, and download in your preferred format.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                   Frontend (Vanilla JS)               │
│  ┌─────────┐  ┌──────────┐  ┌──────────────────────┐ │
│  │Campaign │  │AI Refine │  │  Report Preview +     │ │
│  │  Form   │  │ Chatbar  │  │  Download Dropdown    │ │
│  └────┬────┘  └────┬─────┘  └──────────────────────┘ │
│       │             │                                  │
├───────┼─────────────┼──────────────────────────────────┤
│       ▼             ▼         FastAPI Backend          │
│  /api/generate  /api/refine                            │
│       │             │                                  │
│       ▼             ▼                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │           Campaign Agent (Orchestrator)          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │  │
│  │  │Objectives│ │ Timeline │ │    Resources     │ │  │
│  │  └──────────┘ └──────────┘ └──────────────────┘ │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │  │
│  │  │Volunteers│ │  Risks   │ │     Metrics      │ │  │
│  │  └──────────┘ └──────────┘ └──────────────────┘ │  │
│  └─────────────────────────────────────────────────┘  │
│       │                                                │
│       ▼                                                │
│  ┌─────────────────────────────────────────────────┐  │
│  │       Compiler (MD → PDF / DOCX / HTML)         │  │
│  └─────────────────────────────────────────────────┘  │
│       │                                                │
│       ▼                                                │
│  ┌──────────────┐                                     │
│  │  LLM Router  │ Gemini (primary) ↔ Groq (fallback) │
│  └──────────────┘                                     │
└──────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, Vanilla CSS (Glassmorphism), JavaScript |
| **Backend** | FastAPI, Uvicorn |
| **AI Models** | Google Gemini 2.0 Flash, Groq Llama 3.3 70B |
| **Export** | `markdown`, `xhtml2pdf` (PDF), `python-docx` (DOCX) |
| **Security** | Custom prompt injection filter, HTML sanitization, rate limiter |
| **Font** | [Outfit](https://fonts.google.com/specimen/Outfit) (Google Fonts) |

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/arunkg005/Agentic_dev.git
cd Agentic_dev
```

### 2. Create Virtual Environment

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

Copy the example env file and add your keys:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# Required — Get a free key from: https://aistudio.google.com/apikey
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# Optional (fallback) — Get a free key from: https://console.groq.com/keys
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

> **Note:** You need at least one API key. Groq is optional and acts as an automatic fallback if Gemini fails.

### 5. Run the Application

```bash
python main.py
```

Open **http://127.0.0.1:8000** in your browser.

---

## 📖 Usage Guide

1. **Fill in Campaign Details** — Title, Focus/Topic, Target Audience, Reach, Budget, Duration
2. **Click "Generate Campaign Plan"** — Watch the AI pipeline progress through 6 modules in real-time
3. **Review the Report** — The generated plan appears in the main panel with formatted sections
4. **Refine with AI Chat** — Use the chatbar to make changes (e.g., *"increase budget to 25,000"*, *"add a risk about weather"*)
5. **Download** — Click the dropdown to export as Markdown, PDF, or Word document

---

## 🛡️ Security

| Layer | Protection |
|---|---|
| **Prompt Injection** | 20+ regex patterns detect instruction override, identity hijacking, and secret extraction attempts |
| **Input Sanitization** | HTML escaping, control character removal, and field length limits |
| **System Instruction** | Enforced on every LLM call — restricts AI to campaign planning topics only |
| **Safety Filters** | Gemini safety settings block harassment, hate speech, explicit, and dangerous content |
| **Rate Limiting** | Token-bucket limiter (5 requests / 60 seconds) protects shared API keys |
| **No PII Collection** | No personal data (emails, phones, addresses) is collected or stored |

---

## 📁 Project Structure

```
.
├── main.py              # FastAPI server + API endpoints
├── agent.py             # Campaign orchestrator (pipeline coordinator)
├── config.py            # LLM provider routing (Gemini / Groq)
├── security.py          # Prompt injection, sanitization, rate limiting
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── modules/
│   ├── objectives.py    # SMART objectives generator
│   ├── timeline.py      # Execution timeline planner
│   ├── resources.py     # Resource & budget estimator
│   ├── volunteers.py    # Volunteer role distributor
│   ├── risks.py         # Risk assessment & mitigation
│   ├── metrics.py       # Success KPI generator
│   └── compiler.py      # Report compiler (MD → PDF / DOCX)
├── static/
│   ├── index.html       # Single-page app UI
│   ├── style.css        # Glassmorphic dark theme
│   └── script.js        # Frontend logic & chat handler
└── output/              # Generated campaign plans (gitignored)
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ using AI-powered agentic workflows
</p>
