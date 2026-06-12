"""Database models.

JSON columns hold the structured output of the AI modules (extracted job
requirements, parsed CV, scoring breakdown, generated questions, reports).
"""
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

CANDIDATE_STATUSES = [
    "New",
    "Shortlisted",
    "Interview Scheduled",
    "Interviewed",
    "Recommended",
    "Rejected",
    "Hired",
]


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    raw_description: Mapped[str] = mapped_column(Text)
    # AI-extracted structure: skills, experience, education, responsibilities...
    extracted: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    candidates: Mapped[list["Candidate"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    name: Mapped[str] = mapped_column(String(255), default="Unknown")
    email: Mapped[str] = mapped_column(String(255), default="")
    phone: Mapped[str] = mapped_column(String(100), default="")
    source_filename: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(50), default="New")
    raw_cv_text: Mapped[str] = mapped_column(Text, default="")
    # AI-extracted CV structure: education, experience, skills, projects...
    parsed_cv: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    job: Mapped["Job"] = relationship(back_populates="candidates")
    analysis: Mapped["Analysis"] = relationship(
        back_populates="candidate", uselist=False, cascade="all, delete-orphan"
    )
    question_set: Mapped["QuestionSet"] = relationship(
        back_populates="candidate", uselist=False, cascade="all, delete-orphan"
    )
    evaluation: Mapped["InterviewEvaluation"] = relationship(
        back_populates="candidate", uselist=False, cascade="all, delete-orphan"
    )
    final_report: Mapped["FinalReport"] = relationship(
        back_populates="candidate", uselist=False, cascade="all, delete-orphan"
    )
    interview_session: Mapped["InterviewSession"] = relationship(
        back_populates="candidate", uselist=False, cascade="all, delete-orphan"
    )


class Analysis(Base):
    """CV-vs-job matching, scoring and candidate summary."""

    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), unique=True)
    total_score: Mapped[float] = mapped_column(Float, default=0)  # out of 100
    match_percentage: Mapped[float] = mapped_column(Float, default=0)
    recommendation: Mapped[str] = mapped_column(String(50), default="")  # Strong/Good/Average/Weak Match
    # Full structured result: score breakdown, strengths, missing skills, risks, summary
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    candidate: Mapped["Candidate"] = relationship(back_populates="analysis")


class QuestionSet(Base):
    """AI-generated interview questions for a candidate."""

    __tablename__ = "question_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), unique=True)
    questions: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    candidate: Mapped["Candidate"] = relationship(back_populates="question_set")


class InterviewEvaluation(Base):
    """Structured interview scorecard filled by HR + AI-generated summary."""

    __tablename__ = "interview_evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), unique=True)
    # {technical_skills: 1-5, problem_solving: 1-5, ...}
    ratings: Mapped[dict] = mapped_column(JSON, default=dict)
    interviewer_notes: Mapped[str] = mapped_column(Text, default="")
    score: Mapped[float] = mapped_column(Float, default=0)  # out of 100
    ai_summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    candidate: Mapped["Candidate"] = relationship(back_populates="evaluation")


class InterviewSession(Base):
    """AI-conducted interview reachable by the candidate through a tokenized link.

    The transcript is a list of {"role": "interviewer"|"candidate", "text": str}
    entries. When the interview completes, the AI produces a suggested scorecard
    (ai_assessment) that pre-fills the InterviewEvaluation for human review.
    """

    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), unique=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/in_progress/completed
    transcript: Mapped[list] = mapped_column(JSON, default=list)
    ai_assessment: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    candidate: Mapped["Candidate"] = relationship(back_populates="interview_session")


class FinalReport(Base):
    """Final recruitment report combining CV analysis and interview results."""

    __tablename__ = "final_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), unique=True)
    content: Mapped[dict] = mapped_column(JSON, default=dict)
    recommendation: Mapped[str] = mapped_column(String(50), default="")
    salary_range: Mapped[str] = mapped_column(String(255), default="")
    hr_notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    candidate: Mapped["Candidate"] = relationship(back_populates="final_report")
