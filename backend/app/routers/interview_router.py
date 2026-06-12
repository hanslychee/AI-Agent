"""AI-conducted interviews.

HR generates a tokenized link for a candidate; the candidate opens it (no
login) and is interviewed by the AI in a chat. When the interview completes,
the AI produces a suggested scorecard that pre-fills the InterviewEvaluation —
the human recruiter reviews, edits, and confirms it.
"""
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..ai import service as ai
from ..auth import get_current_user
from ..database import get_db
from ..models import Candidate, InterviewEvaluation, InterviewSession
from .candidates_router import candidate_detail_dict

LINK_VALIDITY_DAYS = 7

hr_router = APIRouter(
    prefix="/api/candidates", tags=["ai-interview"], dependencies=[Depends(get_current_user)]
)
public_router = APIRouter(prefix="/api/interview", tags=["ai-interview-public"])


class CandidateMessage(BaseModel):
    text: str = Field(min_length=1, max_length=ai.MAX_CANDIDATE_MESSAGE_CHARS)


def session_dict(session: InterviewSession, include_assessment: bool = False) -> dict:
    data = {
        "token": session.token,
        "status": session.status,
        "transcript": session.transcript or [],
        "created_at": session.created_at.isoformat(),
        "expires_at": session.expires_at.isoformat() if session.expires_at else None,
        "completed_at": session.completed_at.isoformat() if session.completed_at else None,
        "has_assessment": bool(session.ai_assessment),
    }
    if include_assessment:
        data["ai_assessment"] = session.ai_assessment or None
    return data


# ---------------------------------------------------------------------------
# HR endpoints (authenticated)
# ---------------------------------------------------------------------------
@hr_router.post("/{candidate_id}/interview-link")
def create_interview_link(candidate_id: int, db: Session = Depends(get_db)):
    """Create (or regenerate) the candidate's AI interview link."""
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if candidate.interview_session:
        db.delete(candidate.interview_session)
        db.flush()
    session = InterviewSession(
        candidate_id=candidate.id,
        token=secrets.token_urlsafe(24),
        status="pending",
        transcript=[],
        expires_at=datetime.utcnow() + timedelta(days=LINK_VALIDITY_DAYS),
    )
    db.add(session)
    if candidate.status in ("New", "Shortlisted"):
        candidate.status = "Interview Scheduled"
    db.commit()
    db.refresh(session)
    return session_dict(session)


@hr_router.get("/{candidate_id}/interview-session")
def get_interview_session(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if not candidate.interview_session:
        raise HTTPException(status_code=404, detail="No interview session for this candidate")
    return session_dict(candidate.interview_session, include_assessment=True)


@hr_router.post("/{candidate_id}/interview-session/assess")
def rerun_assessment(candidate_id: int, db: Session = Depends(get_db)):
    """(Re)generate the AI assessment for a completed interview."""
    candidate = db.get(Candidate, candidate_id)
    if not candidate or not candidate.interview_session:
        raise HTTPException(status_code=404, detail="No interview session for this candidate")
    session = candidate.interview_session
    if session.status != "completed":
        raise HTTPException(status_code=409, detail="The interview has not been completed yet.")
    try:
        _assess_and_apply(candidate, session, db)
    except ai.AIServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    db.commit()
    db.refresh(candidate)
    return candidate_detail_dict(candidate)


# ---------------------------------------------------------------------------
# Public endpoints (token-based, used by the candidate)
# ---------------------------------------------------------------------------
def _get_session_by_token(token: str, db: Session) -> InterviewSession:
    session = db.query(InterviewSession).filter(InterviewSession.token == token).first()
    if not session:
        raise HTTPException(status_code=404, detail="This interview link is invalid.")
    if session.expires_at and session.status != "completed" and datetime.utcnow() > session.expires_at:
        raise HTTPException(status_code=410, detail="This interview link has expired. Please contact the recruiter.")
    return session


def _public_dict(session: InterviewSession) -> dict:
    """Only what the candidate needs — never scores or assessments."""
    candidate = session.candidate
    return {
        "candidate_name": candidate.name,
        "job_title": candidate.job.title if candidate.job else "",
        "status": session.status,
        "transcript": session.transcript or [],
    }


@public_router.get("/{token}")
def get_public_interview(token: str, db: Session = Depends(get_db)):
    return _public_dict(_get_session_by_token(token, db))


@public_router.post("/{token}/start")
def start_interview(token: str, db: Session = Depends(get_db)):
    session = _get_session_by_token(token, db)
    if session.status == "completed":
        raise HTTPException(status_code=409, detail="This interview has already been completed.")
    if session.status == "in_progress":
        return _public_dict(session)  # idempotent: rejoining shows the transcript

    candidate = session.candidate
    try:
        turn = ai.conduct_interview_turn(
            candidate_name=candidate.name,
            job_extracted=candidate.job.extracted,
            parsed_cv=candidate.parsed_cv,
            questions=candidate.question_set.questions if candidate.question_set else None,
            transcript=[],
        )
    except ai.AIServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    session.transcript = [{"role": "interviewer", "text": turn["message"]}]
    session.status = "in_progress"
    db.commit()
    db.refresh(session)
    return _public_dict(session)


@public_router.post("/{token}/message")
def send_message(token: str, body: CandidateMessage, db: Session = Depends(get_db)):
    session = _get_session_by_token(token, db)
    if session.status == "completed":
        raise HTTPException(status_code=409, detail="This interview has already been completed.")
    if session.status != "in_progress":
        raise HTTPException(status_code=409, detail="The interview has not started yet.")

    candidate = session.candidate
    transcript = list(session.transcript or [])
    transcript.append({"role": "candidate", "text": body.text.strip()})

    interviewer_turns = sum(1 for e in transcript if e["role"] == "interviewer")
    if interviewer_turns >= ai.HARD_TURN_LIMIT:
        # Safety cap: close without another model call.
        turn = {
            "message": (
                "Thank you for your time — that concludes our interview. "
                "The hiring team will review your answers and contact you about next steps."
            ),
            "is_complete": True,
        }
    else:
        try:
            turn = ai.conduct_interview_turn(
                candidate_name=candidate.name,
                job_extracted=candidate.job.extracted,
                parsed_cv=candidate.parsed_cv,
                questions=candidate.question_set.questions if candidate.question_set else None,
                transcript=transcript,
                force_wrap_up=interviewer_turns >= ai.MAX_INTERVIEWER_TURNS,
            )
        except ai.AIServiceError as exc:
            raise HTTPException(status_code=502, detail=str(exc))

    transcript.append({"role": "interviewer", "text": turn["message"]})
    session.transcript = transcript

    if turn.get("is_complete"):
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        if candidate.status in ("New", "Shortlisted", "Interview Scheduled"):
            candidate.status = "Interviewed"
        # Assessment is best-effort here; HR can re-run it from the dashboard.
        try:
            _assess_and_apply(candidate, session, db)
        except ai.AIServiceError:
            session.ai_assessment = {}

    db.commit()
    db.refresh(session)
    return _public_dict(session)


def _assess_and_apply(candidate: Candidate, session: InterviewSession, db: Session) -> None:
    """Generate the AI scorecard and pre-fill the InterviewEvaluation with it."""
    assessment = ai.assess_interview(
        candidate_name=candidate.name,
        job_title=candidate.job.title,
        job_extracted=candidate.job.extracted,
        transcript=session.transcript or [],
    )
    session.ai_assessment = assessment

    ratings = assessment["ratings"]
    score = ai.compute_interview_score(ratings)
    notes = "[AI-conducted interview — pending human review] " + assessment.get("notes", "")
    if candidate.evaluation:
        db.delete(candidate.evaluation)
        db.flush()
    db.add(InterviewEvaluation(
        candidate_id=candidate.id,
        ratings=ratings,
        interviewer_notes=notes,
        score=score,
        ai_summary=assessment.get("summary", ""),
    ))
