"""Reusable prompt templates for the AI recruitment assistant.

All prompts share a common fairness charter: the model is instructed to assess
only job-related criteria, to ignore protected or sensitive characteristics,
and to always defer the final decision to a human recruiter.
"""

HUMAN_REVIEW_REMINDER = (
    "Final hiring decisions must be reviewed and approved by a human recruiter "
    "or hiring manager."
)

FAIRNESS_CHARTER = f"""You are a professional, neutral HR recruitment assistant. You support human
recruiters; you never replace human decision-making.

Strict fairness rules — follow them in every output:
1. Assess ONLY job-related criteria: skills, experience, education, certifications,
   achievements, projects, and demonstrated competencies.
2. NEVER factor in, mention, or infer protected or sensitive characteristics:
   age, gender, race, ethnicity, religion, nationality, marital or family status,
   disability, physical appearance, political opinion, sexual orientation,
   or any photo on the CV. If such information appears in a document, ignore it
   completely — it must not influence any score, summary, or recommendation.
3. Be consistent: apply the same criteria and standards to every candidate.
4. Be evidence-based: every strength, weakness, or risk you report must be
   traceable to the CV, the job description, or the interview ratings provided.
   Never invent facts about a candidate.
5. Use professional, concise, neutral language.
6. Remember in all conclusions: {HUMAN_REVIEW_REMINDER}"""


# ---------------------------------------------------------------------------
# 1. Job description extraction
# ---------------------------------------------------------------------------
JOB_EXTRACTION_PROMPT = """Extract a structured profile from the job description below.

Rules:
- Use only information present in the text; leave lists empty when the
  information is absent. Do not invent requirements.
- "required_skills" are must-have skills; "preferred_skills" are nice-to-have.
- "years_of_experience" is the minimum number of years requested (0 if unstated).
- "evaluation_criteria" is a short list of the most important things a recruiter
  should check when screening candidates for this role.

<job_description>
{job_description}
</job_description>"""


# ---------------------------------------------------------------------------
# 2. CV extraction
# ---------------------------------------------------------------------------
CV_EXTRACTION_PROMPT = """Extract a structured candidate profile from the CV text below.

Rules:
- Use only information present in the CV; leave fields empty when absent.
- Do NOT extract or mention age, date of birth, gender, marital status,
  nationality, religion, photos, or any other protected characteristic,
  even if present in the document.
- "career_timeline" is a chronological list of roles, newest first, with
  approximate period strings exactly as written (e.g. "2021 - 2023").
- Keep descriptions short (one line each).

<cv_text>
{cv_text}
</cv_text>"""


# ---------------------------------------------------------------------------
# 3. Candidate scoring (CV vs job description)
# ---------------------------------------------------------------------------
SCORING_PROMPT = """Compare the candidate profile against the job requirements and score the match.

Scoring system (total = 100 points). Score each category independently and do
not exceed its maximum:
- required_skills_match: 0-30 — coverage of the required skills.
- relevant_experience: 0-25 — relevance and depth of work experience for this role.
- education_certifications: 0-15 — fit of education and certifications.
- achievements_projects: 0-15 — quality and relevance of achievements and projects.
- soft_skills_communication: 0-10 — soft-skill and communication indicators
  visible in the CV (clarity, leadership, teamwork, languages).
- overall_role_fit: 0-5 — holistic fit with the role's responsibilities.

Also produce:
- match_percentage: 0-100, your overall estimate of fit (usually close to the total score).
- key_strengths: 3-6 evidence-based strengths.
- missing_skills: required or preferred skills that are absent or weak.
- risk_factors: job-related concerns only (e.g. employment gaps relevant to skill
  currency, missing must-have skills, no evidence of a core responsibility).
- recommendation: exactly one of "Strong Match" (>=80), "Good Match" (65-79),
  "Average Match" (50-64), "Weak Match" (<50) — consistent with the total score.

Candidate summary section (HR-friendly, professional, concise, neutral):
- overview: 2-3 sentence candidate overview.
- best_matching_experience: the single most relevant experience for this role.
- top_strengths: top 5 strengths.
- possible_concerns: 1-4 possible concerns (job-related only).
- suggested_next_step: one short sentence (e.g. "Invite to technical interview").

<job_requirements>
{job_json}
</job_requirements>

<candidate_profile>
{cv_json}
</candidate_profile>"""


# ---------------------------------------------------------------------------
# 4. Interview question generation
# ---------------------------------------------------------------------------
QUESTIONS_PROMPT = """Generate a tailored interview question set for this candidate and role.

Base the questions on: the job requirements, the candidate's CV, the skills the
screening found missing, and the role's responsibilities. Questions must be
job-related only — never about protected characteristics or private life.

Produce:
- technical: 4-6 technical questions targeting the role's required skills,
  including 1-2 that probe the candidate's missing or weak skills.
- behavioral: 3-4 behavioral questions (STAR-friendly).
- experience_based: 3-4 questions about specific items on the candidate's CV.
- culture_fit: 2-3 questions about ways of working and collaboration
  (work style and values — not personal life).
- practical_case: 1-2 short practical case or scenario exercises realistic for
  this role.
- follow_ups: for each section above, the questions list pairs each question
  with one suggested follow-up probe.

<job_requirements>
{job_json}
</job_requirements>

<candidate_profile>
{cv_json}
</candidate_profile>

<screening_findings>
Missing skills: {missing_skills}
Key strengths: {strengths}
</screening_findings>"""


# ---------------------------------------------------------------------------
# 5. Interview evaluation summary
# ---------------------------------------------------------------------------
INTERVIEW_EVALUATION_PROMPT = """An HR interviewer rated the candidate below on a 1-5 scale per category and
added free-text notes. Write a short, professional evaluation (4-6 sentences):
what the ratings show, the candidate's strongest and weakest interview areas,
and what HR should verify or consider next. Base it only on the ratings and
notes provided. End with the human-review reminder.

Candidate: {candidate_name}
Role: {job_title}

Ratings (1 = poor, 5 = excellent):
{ratings_text}

Computed interview score: {score}/100

Interviewer notes:
{notes}"""


# ---------------------------------------------------------------------------
# 6. Final candidate report
# ---------------------------------------------------------------------------
FINAL_REPORT_PROMPT = """Produce the final recruitment report for this candidate by combining the CV
screening results and the interview evaluation.

Rules:
- Base everything strictly on the data provided below.
- strengths / weaknesses / concerns must be job-related and evidence-based.
- recommendation: exactly one of "Highly Recommended", "Recommended",
  "Consider with Caution", "Not Recommended". Weigh both the CV match score
  and the interview score; an excellent interview can offset an average CV and
  vice versa, but a failing score in either should cap the recommendation at
  "Consider with Caution".
- executive_summary: 3-5 sentences for a hiring manager who has 30 seconds.
- suggested_salary_range: leave as an empty string — this field is filled in
  by HR, not by you.

Candidate: {candidate_name}
Role: {job_title}
CV match score: {cv_score}/100 ({cv_recommendation})
Interview score: {interview_score}/100

<cv_screening>
{analysis_json}
</cv_screening>

<interview_evaluation>
Ratings: {ratings_json}
Interviewer notes: {notes}
AI interview summary: {interview_summary}
</interview_evaluation>"""
