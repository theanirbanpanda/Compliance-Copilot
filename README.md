# 🤖 Compliance Copilot

**An interactive, AI-powered workspace for instantly analyzing and understanding complex regulatory documents.**

This project is a full-stack, portfolio-ready application demonstrating a complete product lifecycle, from backend data processing with Python and AI to a modern, interactive SvelteKit frontend.

### 🎥 Live Demo Screenshots




**Main Dashboard:**
![Dashboard](<assets/Screenshot 2025-11-03 at 9.51.27 AM.png>)




---

## 🎯 The Product Vision

### The Problem
Small business owners and startup teams are drowning in complex regulatory documents (tax codes, labor laws, compliance requirements). They don't have the time to read hundreds of pages, and they can't afford expensive legal teams. Missing one update can lead to costly fines or legal issues.

### The Solution
Compliance Copilot is an interactive tool that solves this. A user can paste any document text, and the AI-powered backend will:
1.  **Instantly Analyze:** Read the document and provide a simple, 2-sentence summary.
2.  **Categorize & Tag:** Automatically tag the document with relevant categories (e.g., `finance`, `legal`, `labor`).
3.  **Verify:** Run the AI's tags against a set of business rules to check for consistency and flag potential issues.
4.  **Enable Q&A:** Allow the user to "chat" with the document and ask follow-up questions in plain English (e.g., "What is the effective date for the new overtime regulations?").
5.**Change Alerts :** Based on user interaction ,the information will be stored and user will get alerts if anything changes with time,(ex: tax law changes)
---

## 🛠️ Technical Architecture

This project is a full-stack application built with a modern, decoupled architecture.

### Backend (`Python / Flask / Gemini`)
* **API Server:** A **Flask** server provides a local API (with `/api/analyze` and `/api/ask` endpoints).
* **Data Pipeline:** A robust Python pipeline (`run_pipeline.py`) that uses `requests` and `PyPDF2` to download and extract text from source documents.
* **AI Engine:** A consolidated `DocumentProcessor` class that uses the **Google Gemini API** for:
    * **Summarization & Tagging:** Generating insights from raw text.
    * **RAG (Retrieval-Augmented Generation):** Powering the interactive Q&A feature.
* **Verification Layer:** A custom-built rules engine (`VERIFICATION_RULES`) that runs after the AI to ensure the quality and consistency of the tagged data.

### Frontend (`SvelteKit / Tailwind CSS`)
* **Framework:** A fast and modern **SvelteKit** application.
* **Styling:** A professional, responsive UI built with **Tailwind CSS**.
* **Interactivity:** The app makes live `fetch` calls to the local Python backend, creating a seamless, full-stack user experience.

---

## 🚀 How to Run This Project Locally

**Prerequisites:**
* Python 3.9+
* Node.js & npm
* A `GEMINI_API_KEY` set in a `.env` file

**1. Setup the Project:**
```bash
# Clone the repository
git clone [https://github.com/theanirbanpanda/Compliance-Copilot.git](https://github.com/theanirbanpanda/Compliance-Copilot.git)
cd Compliance-Copilot

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Frontend dependencies
cd frontend
npm install
cd ..

#TO Run:
python run_pipeline.py
cd frontend
npm run dev