# TalentForge AI - Resume Analyzer & Interview Prep System

A production-quality, full-stack AI Resume Analyzer and Interview Preparation System. The application parses resume documents (PDF, DOCX), scores them against custom job descriptions using TF-IDF cosine similarity, highlights missing keywords, compiles structural feedback, and generates tailored interview preparation questions complete with answer strategies.

---

## Key Features
- **ATS Scoring & Resume Parsing**: Intelligent parsing of contact info, experience, education, and keywords using SpaCy.
- **Semantic Job Matching**: TF-IDF vectorization and cosine similarity matching using Scikit-learn.
- **Tailored Interview Prep**: Custom behavioral and technical interview questions based on candidate profile and missing gaps.
- **Interactive Analytics Dashboard**: Track average ATS scores, total uploads, and frequencies of missing skills.
- **Resilient Database Architecture**: Fallback mechanism trying to establish MySQL connections first, automatically falling back to an embedded SQLite instance if MySQL is unreachable.
- **Premium PDF Reports**: Elegant PDF compilation of match results using ReportLab.
- **JWT Authorization**: Token-based security gating file uploads, stats, and PDF downloads.

---

## Repository Structure

```text
C:/Users/poorn/Desktop/P2/
├── backend/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py            # User registration, login, and profile validation
│   │   ├── resume.py          # Resume file uploads and parsing triggers
│   │   ├── analysis.py        # ATS matching computations and PDF generation
│   │   └── dashboard.py       # Metrics and chart calculations
│   ├── app.py                 # Flask server entry point and CORS/JWT config
│   ├── config.py              # Application settings (secret keys, upload paths)
│   ├── database.py            # SQLAlchemy database models & resilience engine
│   ├── parser.py              # PDF/DOCX parser utilizing SpaCy and regex
│   ├── analyzer.py            # Cosine similarity and weighted ATS scorer
│   ├── questions.py           # Interview prep question templates and generator
│   ├── pdf_generator.py       # Elegant ReportLab PDF compiler
│   ├── requirements.txt       # Python dependencies (loosely pinned for Python 3.13)
│   └── .env                   # Environment variables (database URL, ports, keys)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx     # Navigation bar with user context links
│   │   │   ├── Card.jsx       # Reusable glassmorphic panel container
│   │   │   └── FileUpload.jsx # Drag-and-drop file uploader with feedback
│   │   ├── context/
│   │   │   └── AuthContext.jsx# React Context for login states and Axios defaults
│   │   ├── pages/
│   │   │   ├── Login.jsx      # Premium login view
│   │   │   ├── Register.jsx   # Registration view
│   │   │   ├── Dashboard.jsx  # Analytics summary and charts
│   │   │   ├── UploadAnalyze.jsx # Dual-panel matching workflow
│   │   │   ├── AnalysisResult.jsx# radial score gauge and keyword mapping tables
│   │   │   └── InterviewPrep.jsx# Interactive flashcard prep cards
│   │   ├── App.jsx            # Main router and auth guards
│   │   ├── index.css          # Primary CSS imports (Tailwind and glassmorphism)
│   │   ├── App.css            # Base styled stylesheet (cleared)
│   │   └── main.jsx           # Root DOM renderer
│   ├── package.json           # Frontend package dependencies (Vite, Tailwind, Recharts)
│   ├── tailwind.config.js     # Tailwind content matching settings
│   └── postcss.config.js      # PostCSS processor mapping
├── test_backend.py            # Automated logic integration check script
└── README.md                  # System documentation (This file)
```

---

## REST API Documentation

### Authentication Blueprints (`/api/auth`)
- `POST /register`: Registers a new user. Expects `{ "username": "...", "email": "...", "password": "..." }`.
- `POST /login`: Logs in and returns a JWT access token. Expects `{ "email": "...", "password": "..." }`.
- `GET /me`: Returns the current user's profile metadata. Requires authorization token header.

### Resume Blueprints (`/api/resumes`)
- `POST /upload`: Accepts `file` field via `multipart/form-data`. Saves and parses the file using SpaCy. Returns parsed profile. Requires token header.
- `GET /`: Lists all resumes uploaded by the current user. Requires token header.
- `DELETE /<id>`: Deletes a specific resume from the database. Requires token header.

### Analysis Blueprints (`/api/analysis`)
- `POST /analyze`: Links a resume and a job description. Returns computed ATS scores and generated questions. Expects `{ "resume_id": 1, "job_title": "...", "job_description": "..." }`. Requires token header.
- `GET /history`: Returns the history of all user match reports. Requires token header.
- `GET /<id>`: Returns detailed match information, including job criteria and prepared questions. Requires token header.
- `GET /<id>/report`: Compiles and streams the styled PDF report download. Requires token header.

### Dashboard Blueprints (`/api/dashboard`)
- `GET /stats`: Returns metrics like average scores, upload counts, score trends over time, and a frequency mapping of top missing keywords. Requires token header.

---

## Deployment & Setup Guide

### 1. Prerequisites
- **Python 3.10+** (Python 3.13.5 was used to build this application)
- **Node.js v18+**
- **MySQL Database Server** (Optional; will fallback to SQLite if offline)

### 2. Backend Installation (Flask)
From the root project directory:
```bash
# Navigate to backend (using terminal shell)
cd backend

# Create a virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # On Windows

# Install Python requirements
pip install -r requirements.txt

# Download the SpaCy language model
python -m spacy download en_core_web_sm

# Start the Flask development server (runs on port 5000)
python app.py
```

### 3. Frontend Installation (React)
Open a separate terminal window from the root project directory:
```bash
# Navigate to frontend
cd frontend

# Install Node modules
npm install

# Run the local development server (runs on port 5173)
npm run dev
```

### 4. Verification Tests
Ensure backend services are working correctly by running the validation suite:
```bash
python test_backend.py
```
