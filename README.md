# Naye Pankh - NGO Campaign Planning Copilot 🕊️

An AI-powered planning agent designed to assist NGO coordinators in transforming campaign topics and logistics into highly structured, professional execution plans.

The application follows a structured workflow where a central coordinator agent manages multiple sub-modules (Objectives, Timeline, Resources, Volunteers, Risks, and Metrics) to produce a unified, downloadable Markdown report.

---

## 🛠️ Tech Stack & Architecture

- **Frontend**: [Gradio](https://github.com/gradio-app/gradio) (Python web-framework with custom theme & responsive grid layout)
- **Backend**: Python 3.11+
- **AI Engine**: Google Gemini API (default model: `gemini-1.5-flash`)
- **Security Check**: Custom input sanitization, character boundaries validation, and prompt injection heuristical filtering.

---

## 🚀 Local Installation & Execution

### 1. Clone or Move to Directory
Navigate to the `NGO-Agent` folder:
```bash
cd NGO-Agent
```

### 2. Set Up Virtual Environment (Recommended)
Create and activate a Python virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install all required packages:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root of the `NGO-Agent/` folder:
```env
# Google AI Studio Gemini API Key
# Get a free key from: https://aistudio.google.com/
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Optional: override default model (e.g. gemini-2.5-flash or gemini-1.5-flash)
GEMINI_MODEL=gemini-1.5-flash
```

### 5. Launch the Application
Run the main app file:
```bash
python app.py
```
Open the provided URL (e.g., `http://127.0.0.1:7860`) in your browser to interact with the Copilot!

---

## 🛡️ Security & Privacy Guardrails

1. **Prompt Injection Shield**: Intercepts and rejects malicious prompts trying to force the system to bypass formatting rules or reveal prompt instructions.
2. **PII Protection**: Designed strictly for session-based planning. No volunteer phone numbers, email addresses, or personal identity documents are collected or transmitted.
3. **Harm/Safety Filters**: The Gemini connection is configured to block hate speech, harassment, sexually explicit, and dangerous content at a strict threshold.
4. **Input Length Limits**: Restricts input fields to safe character boundaries (e.g., maximum 250 characters for details) to prevent abuse and manage API usage tokens.

---

## ☁️ Hugging Face Spaces Deployment Guide (Free Tier)

Hugging Face Spaces offers a completely free CPU basic tier that hosts Gradio apps natively.

### Step 1: Create a Space on Hugging Face
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Select **Gradio** as the SDK.
3. Choose the **Blank** template.
4. Set the space to **Public** (or **Private** depending on your team's needs).
5. Choose the **Free CPU basic** hardware.
6. Click **Create Space**.

### Step 2: Push App Files to HF Space
You can upload files directly through the Hugging Face Web UI or clone the space using git and push the files:
```bash
# Clone the empty Space repository (replace username and space-name)
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
cd YOUR_SPACE_NAME

# Copy all NGO-Agent files into the cloned folder:
# app.py, config.py, security.py, agent.py, requirements.txt, and the modules/ folder

# Add, commit, and push to Hugging Face
git add .
git commit -m "Deploy NGO Campaign Planning Copilot"
git push
```

### Step 3: Configure Gemini API Key Secrets
1. Navigate to your Hugging Face Space page.
2. Click on the **Settings** tab at the top right.
3. Scroll down to **Variables and secrets**.
4. Click **New secret**.
5. Set the name as `GEMINI_API_KEY` and the value as your **Google AI Studio API Key**.
6. Save the secret.

Your Space will automatically rebuild and be ready to run at the public Hugging Face URL. Anyone accessing it can use the service. If the server key exhausts its limit, users can also optionally paste their own API keys directly into the UI!
