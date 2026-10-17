# AI Career Mentor: Intelligent Resume Analysis & Career Guidance System

![Version](https://img.shields.io/badge/version-1.0.0-indigo)
![Framework](https://img.shields.io/badge/Framework-Django%204.2%2B-green)
![UI](https://img.shields.io/badge/UI-Bootstrap%205%20Dark-cyan)
![AI Architecture](https://img.shields.io/badge/Architecture-Multi--Agent%20System-blue)

A complete, production-ready **AI-Powered Career Mentor Web Application** built using **Django**, **Bootstrap 5**, **Scikit-learn**, **PyPDF2**, **NLTK**, and **Google Gemini API** with smart local fallback algorithms.

---

## 🌟 Key Features

1. **User Authentication & Career Profile Management**:
   - Secure Registration, Login, Logout, Profile update.
   - Comprehensive profile tracking (Education, Degree, University, Graduation Year, Experience Level, Target Role, Years of Experience, Career Objective).

2. **PDF Resume Text Extraction & NLP Skill Detection**:
   - Upload PDF resumes securely (validated for size <= 4MB and PDF content).
   - PyPDF2 text extraction service.
   - NLTK & database-driven Skill Dictionary for technical skill extraction.

3. **ATS Resume Scoring Engine**:
   - Calculates dynamic ATS Score from 0 to 100 based on weighted metrics:
     - Skills Match (25%)
     - Keyword Alignment for Target Role (25%)
     - Resume Structure & Section Completeness (15%)
     - Education (15%)
     - Experience History (10%)
     - Projects & Portfolio (10%)
   - Generates actionable strengths, weaknesses, and step-by-step improvement recommendations.

4. **ML Job Recommendation Engine**:
   - Benchmark database of realistic sample jobs.
   - Powered by **Scikit-learn TF-IDF Vectorization** and **Cosine Similarity** + Skill set overlap matching.
   - Ranks job postings with exact match percentages and provides matched vs. missing skill breakdowns.

5. **Skill Gap Analysis & Generative Learning Roadmap**:
   - Compares user's extracted skills against target career requirements to identify missing skills.
   - Generates personalized monthly and weekly learning curriculums (using Gemini API or rule-based fallback).
   - Interactive progress bar and milestone checklist with completion toggling.

6. **Agentic AI System (Multi-Agent Architecture)**:
   - **Resume Agent**: Inspects document structure, calculates ATS scores, suggests keyword improvements.
   - **Job Agent**: Analyzes job descriptions, computes similarity, explains job fit.
   - **Planner Agent**: Identifies skill gaps, synthesizes learning roadmaps, prioritizes tasks.
   - **Central Orchestrator**: Parses user natural language prompts and dispatches to specialized sub-agents or Gemini LLM.

7. **Interactive AI Career Chatbot**:
   - Persistent chat session stored in SQLite/PostgreSQL.
   - Context-aware answers based on live user resume metrics, roadmap progress, and career goals.

8. **Analytical Dashboard & Data Visualizations**:
   - Real-time aggregate metric cards.
   - Chart.js Doughnut chart (Mastered vs. Missing Skills) and Bar chart (ATS Category Breakdown).

9. **Django Admin Panel**:
   - Full administration management for Users, Profiles, Resumes, Resume Analyses, Skills, Jobs, Job Recommendations, Roadmaps, Roadmap Tasks, and Chat Conversations.

---

## 🏗️ Technology Stack

- **Backend**: Python 3.13+, Django 4.2+, Django REST Framework
- **Frontend**: HTML5, CSS3, Bootstrap 5 (Custom Dark Glassmorphic Theme), Vanilla JavaScript
- **Database**: SQLite3 (Local Dev) / PostgreSQL ready
- **AI / ML / Data Science**: Scikit-learn (TF-IDF & Cosine Similarity), Pandas, NumPy, NLTK, Google Gemini API (`google-generativeai`)
- **PDF Extraction**: PyPDF2
- **Data Visualization**: Chart.js

---

## 📁 Project Architecture

```text
ai_career_mentor/
│
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── resumes/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── services.py
│   ├── urls.py
│   └── admin.py
│
├── jobs/
│   ├── models.py
│   ├── views.py
│   ├── services.py
│   ├── urls.py
│   └── admin.py
│
├── skills/
│   ├── models.py
│   └── admin.py
│
├── recommendations/
│   ├── models.py
│   └── admin.py
│
├── roadmap/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── chatbot/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── agents/
│   ├── resume_agent.py
│   ├── job_agent.py
│   ├── planner_agent.py
│   └── orchestrator.py
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── dashboard.html
│   ├── accounts/
│   ├── resumes/
│   ├── jobs/
│   ├── roadmap/
│   └── chatbot/
│
├── static/
│   └── css/
│       └── styles.css
│
└── utils/
    ├── seed_db.py
    └── create_admin.py
```

---

## ⚡ Quick Start & Installation Commands

### 1. Virtual Environment Setup
```bash
# Clone repository
git clone https://github.com/your-username/ai-career-mentor.git
cd ai-career-mentor

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Generate a private Django secret key and set it in `.env`. Keep `.env` out of Git:
```env
SECRET_KEY=<a-long-random-secret>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GEMINI_API_KEY=your_gemini_api_key_here
```
The development server generates a temporary key when `SECRET_KEY` is blank. Production requires an explicitly configured key and `DEBUG=False`.
*(Note: If `GEMINI_API_KEY` is left blank, the application will seamlessly fall back to local rule-based and NLP algorithms).*

### 4. Database Setup & Migrations
```bash
python manage.py migrate
```

### 5. Seed Skills & Sample Job Listings
```bash
python utils/seed_db.py
```

### 6. Create Admin Credentials
```bash
python manage.py createsuperuser
```
Choose a unique password when prompted. Do not use shared or default administrator credentials.

---

## ☁️ Deploy to Vercel with Supabase

This repository is a **Django** project, not a Streamlit app. Deploy it on Vercel as a Python project; do not configure a `streamlit_app.py` entry point. The Vercel function entry point is `api/index.py`, and `vercel.json` configures Django routing and static-file collection.

### 1. Prepare Supabase

1. Create a Supabase project and copy its PostgreSQL connection-pooler URI with SSL enabled.
2. Create a **private** Supabase Storage bucket for resumes and profile images.
3. In Supabase Storage settings, create S3 credentials. The endpoint format is `https://<project-ref>.supabase.co/storage/v1/s3`.
4. Keep the database password, S3 secret, and Django secret private.

### 2. Deploy on Vercel

Import this GitHub repository into Vercel. Set the project root to the repository root and select the Python runtime if prompted. Vercel reads `vercel.json` and installs dependencies from `requirements.txt`.

Add these environment variables in Vercel Project Settings → Environment Variables for Production (and Preview if needed):

| Variable | Value |
| --- | --- |
| `SECRET_KEY` | A newly generated, long random Django secret |
| `DATABASE_URL` | Supabase PostgreSQL connection-pooler URI with SSL |
| `SUPABASE_STORAGE_ENDPOINT` | Supabase S3 endpoint |
| `SUPABASE_STORAGE_BUCKET` | Name of the private Storage bucket |
| `SUPABASE_STORAGE_ACCESS_KEY_ID` | Supabase Storage S3 access key |
| `SUPABASE_STORAGE_SECRET_ACCESS_KEY` | Supabase Storage S3 secret |
| `SUPABASE_STORAGE_REGION` | Supabase S3 region, usually `us-east-1` |
| `GEMINI_API_KEY` | Optional; without it, rule-based guidance is used |
| `CSRF_TRUSTED_ORIGINS` | Optional comma-separated `https://` origins for custom domains |

Vercel deployments automatically disable Django debug mode and allow Vercel hostnames. For a custom domain, add its hostname to `ALLOWED_HOSTS` and its `https://` origin to `CSRF_TRUSTED_ORIGINS`. Do not expose secrets to browser code. Django uses HTTPS redirects, secure cookies, login throttling, PDF upload validation, and password validators.

### 3. Initialize the Supabase database

Before using the app, run migrations against Supabase from a trusted local terminal with `DATABASE_URL` set in your untracked `.env` file:

```bash
python manage.py migrate
python utils/seed_db.py
python manage.py createsuperuser
```

Do not run migrations on each serverless request. Uploaded resumes and profile images use Supabase Storage; the app will refuse to start on Vercel if the storage credentials are incomplete.

Do not use `*` for `ALLOWED_HOSTS`, and do not expose database or Storage secrets to browser code. PDF uploads are size-limited and checked for PDF content, and password registration applies Django's password validators.

ATS scores are estimates from project heuristics, and job results are based on records in the app database (including its seeded sample jobs), not live job listings.

---

## 🚀 Running the Web Application

Start the local development server:
```bash
python manage.py runserver
```
Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

Access the Django Admin Dashboard at:
```
http://127.0.0.1:8000/admin/
```

---

## 🧪 Running Automated Unit Tests

Run the test suite to verify authentication, PDF parsing, ATS scoring, ML job matching, and roadmap generation:
```bash
python manage.py test
```

---

## 🤖 Multi-Agent AI Workflow

```text
                     [ User Natural Language Prompt ]
                                    │
                                    ▼
                          [ Central Orchestrator ]
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
  [ Resume Agent ]           [ Job Agent ]             [ Planner Agent ]
  • PDF Extraction           • TF-IDF Vectorizer       • Skill Gap Matrix
  • ATS Scoring (0-100)      • Cosine Similarity       • 3-Month Roadmap
  • Keyword Feedback         • Skill Overlap Fit       • Milestone Progress
```

---

## 📄 License & Attribution

Developed as a Final MCA Capstone Project. Designed for academic and professional career guidance applications.
