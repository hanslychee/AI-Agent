# RecruitAI — AI Recruitment Assistant

A full-stack AI recruitment assistant that helps HR teams manage the hiring
process from CV review to interview preparation, structured evaluation, and a
final candidate report. The system is a **professional HR assistant, not a
replacement for human decision-making**.

> ⚖️ **Final hiring decisions must be reviewed and approved by a human
> recruiter or hiring manager.** This reminder is embedded in every AI prompt,
> every report, and the application UI.

---

## Features

| Module | What it does |
| --- | --- |
| **Job Description Input** | Paste a job description; the AI extracts title, required/preferred skills, experience, education, responsibilities, soft skills and evaluation criteria. |
| **CV Upload & Parsing** | Upload one or more CVs (PDF / DOCX / TXT). The AI extracts name, contact info, education, experience, skills, certifications, projects, achievements, languages and a career timeline. |
| **CV Matching & Scoring** | Scores each CV against the job out of 100 (required skills 30, experience 25, education 15, achievements 15, soft skills 10, role fit 5) with strengths, missing skills, risk factors and a Strong/Good/Average/Weak Match recommendation. Category caps and the total are enforced server-side. |
| **Candidate Summary** | HR-friendly summary: overview, best matching experience, top 5 strengths, possible concerns, suggested next step. |
| **Interview Question Generator** | Technical, behavioral, experience-based, culture-fit and practical-case questions — each with a suggested follow-up — targeted at the candidate's missing skills. |
| **Interview Evaluation** | 1–5 scorecard across 8 categories; the system computes a 0–100 interview score and writes a short AI evaluation. |
| **Final Candidate Report** | Combines CV screening + interview into an executive summary, strengths/weaknesses/concerns and a hiring recommendation (Highly Recommended → Not Recommended), with HR-owned salary-range and notes fields. Exportable as PDF. |
| **Ranking Dashboard** | All candidates ranked by final score (60% CV + 40% interview) with status management (New → Hired). |

### Fairness & ethics

Every AI prompt shares a fairness charter (see `backend/app/ai/prompts.py`):

- Only job-related criteria are assessed (skills, experience, education,
  achievements, projects).
- Protected/sensitive characteristics (age, gender, race, religion,
  nationality, marital status, disability, appearance, political opinion…) are
  explicitly excluded — the CV extractor is instructed not to even extract them.
- Every claim must be evidence-based (traceable to the CV, the job description,
  or the interview ratings). The model is told never to invent facts.
- The human-review reminder is appended to every analysis and report.

---

## Tech stack

- **Backend:** Python FastAPI, SQLAlchemy + SQLite, JWT auth, `pdfplumber` /
  `python-docx` for file parsing, `reportlab` for PDF export.
- **AI:** Anthropic Claude API (`claude-opus-4-8` by default) with structured
  outputs so every analysis returns validated JSON.
- **Frontend:** React 18 + Vite + React Router, custom HR-SaaS styling
  (cards, tables, filters, badges).

## Project structure

```
backend/
  requirements.txt
  .env.example
  app/
    main.py                 # FastAPI app, CORS, startup (DB + default admin)
    config.py               # Settings from env / .env
    database.py             # SQLAlchemy engine/session
    models.py               # Job, Candidate, Analysis, QuestionSet,
                            # InterviewEvaluation, FinalReport, User
    schemas.py              # Request bodies
    auth.py                 # PBKDF2 hashing + JWT bearer auth
    ai/
      prompts.py            # All reusable AI prompt templates + fairness charter
      service.py            # Claude calls with JSON-schema-enforced outputs
    services/
      file_parser.py        # PDF/DOCX/TXT text extraction
      pdf_export.py         # Final report PDF rendering
    routers/
      auth_router.py        # POST /api/auth/login, GET /api/auth/me
      jobs_router.py        # CRUD /api/jobs (AI extraction on create)
      candidates_router.py  # Upload CVs, list/get/status/delete candidates
      analysis_router.py    # analyze / questions / evaluation / report (+PDF)
      dashboard_router.py   # /api/dashboard, /api/ranking
frontend/
  src/
    api.js                  # Fetch wrapper + endpoints
    App.jsx                 # Routes + auth gate
    components/             # Layout, badges, candidate picker
    pages/                  # Dashboard, Jobs, UploadCVs, Candidates,
                            # CandidateDetail, InterviewQuestions,
                            # InterviewEvaluation, Reports, Ranking, Login
```

## API routes

| Method | Route | Purpose |
| --- | --- | --- |
| POST | `/api/auth/login` | Get a JWT (default admin: `admin` / `admin123`) |
| POST | `/api/jobs` | Add a job description (AI extracts structure) |
| GET / DELETE | `/api/jobs`, `/api/jobs/{id}` | List / read / delete jobs |
| POST | `/api/jobs/{id}/candidates/upload` | Upload one or more CVs (multipart) |
| GET | `/api/candidates?job_id=&status=` | List candidates with filters |
| GET / DELETE | `/api/candidates/{id}` | Candidate detail / delete |
| PATCH | `/api/candidates/{id}/status` | Update pipeline status |
| POST | `/api/candidates/{id}/analyze` | Score CV vs job + summary |
| POST | `/api/candidates/{id}/questions` | Generate interview questions |
| POST | `/api/candidates/{id}/evaluation` | Submit 1–5 scorecard → score + AI summary |
| POST / PATCH | `/api/candidates/{id}/report` | Generate report / update HR fields |
| GET | `/api/candidates/{id}/report/pdf` | Export the final report as PDF |
| GET | `/api/dashboard` | Pipeline stats |
| GET | `/api/ranking?job_id=` | Ranked candidate table |

Interactive API docs: `http://localhost:8000/docs` once the backend is running.

---

## Running locally

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                # then set ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```

On first start the database (`recruitai.db`) and the default admin account
(`admin` / `admin123` — configurable in `.env`) are created automatically.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173> and sign in with the admin account. The Vite dev
server proxies `/api/*` to the backend on port 8000.

### Typical workflow

1. **Job Descriptions** → paste a job description.
2. **Upload CVs** → upload candidate CVs for that job.
3. **Candidate Analysis** → run AI screening on each candidate.
4. **Interview Questions** → generate a tailored question set.
5. **Interview Evaluation** → fill in the 1–5 scorecard after the interview.
6. **Final Reports** → generate the report, add salary range and HR notes, export PDF.
7. **Candidate Ranking** → compare candidates and update statuses.

---

## Future improvements

- Multi-user accounts with roles (recruiter, hiring manager, viewer) and an
  audit log of AI outputs and human overrides.
- Async/batch processing for large CV uploads (Claude Message Batches API
  halves analysis costs for bulk screening).
- OCR fallback for scanned/image-only PDF CVs.
- Email integration: invite candidates, send interview schedules.
- Configurable scoring weights per job, and side-by-side candidate comparison.
- Prompt caching of the job description for cheaper multi-candidate screening.
- Anonymized screening mode (hide name/contact during review) to further
  reduce bias.
- PostgreSQL + Alembic migrations for production deployments.
- Export ranking tables to CSV/Excel; richer analytics dashboards.
