from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..ai import service as ai
from ..auth import get_current_user
from ..database import get_db
from ..models import CANDIDATE_STATUSES, Candidate, Job
from ..schemas import StatusUpdateRequest
from ..services import file_parser

router = APIRouter(prefix="/api", tags=["candidates"], dependencies=[Depends(get_current_user)])


def candidate_summary_dict(c: Candidate) -> dict:
    return {
        "id": c.id,
        "job_id": c.job_id,
        "job_title": c.job.title if c.job else "",
        "name": c.name,
        "email": c.email,
        "phone": c.phone,
        "status": c.status,
        "source_filename": c.source_filename,
        "cv_score": c.analysis.total_score if c.analysis else None,
        "cv_recommendation": c.analysis.recommendation if c.analysis else None,
        "interview_score": c.evaluation.score if c.evaluation else None,
        "has_questions": c.question_set is not None,
        "has_report": c.final_report is not None,
        "created_at": c.created_at.isoformat(),
    }


def candidate_detail_dict(c: Candidate) -> dict:
    data = candidate_summary_dict(c)
    data.update({
        "parsed_cv": c.parsed_cv,
        "raw_cv_text": c.raw_cv_text,
        "analysis": c.analysis.result if c.analysis else None,
        "questions": c.question_set.questions if c.question_set else None,
        "evaluation": {
            "ratings": c.evaluation.ratings,
            "interviewer_notes": c.evaluation.interviewer_notes,
            "score": c.evaluation.score,
            "ai_summary": c.evaluation.ai_summary,
        } if c.evaluation else None,
        "final_report": {
            "content": c.final_report.content,
            "recommendation": c.final_report.recommendation,
            "salary_range": c.final_report.salary_range,
            "hr_notes": c.final_report.hr_notes,
        } if c.final_report else None,
        "job_extracted": c.job.extracted if c.job else {},
        "interview_session": {
            "token": c.interview_session.token,
            "status": c.interview_session.status,
            "transcript": c.interview_session.transcript or [],
            "expires_at": c.interview_session.expires_at.isoformat() if c.interview_session.expires_at else None,
            "completed_at": c.interview_session.completed_at.isoformat() if c.interview_session.completed_at else None,
            "ai_assessment": c.interview_session.ai_assessment or None,
        } if c.interview_session else None,
    })
    return data


@router.post("/jobs/{job_id}/candidates/upload")
def upload_cvs(job_id: int, files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    """Upload one or more CVs (PDF/DOCX/TXT). Each is parsed and AI-extracted."""
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    created, errors = [], []
    for upload in files:
        filename = upload.filename or "cv"
        try:
            text = file_parser.extract_text(filename, upload.file.read())
            parsed = ai.extract_cv(text)
        except file_parser.UnsupportedFileError as exc:
            errors.append({"filename": filename, "error": str(exc)})
            continue
        except ai.AIServiceError as exc:
            errors.append({"filename": filename, "error": str(exc)})
            continue
        candidate = Candidate(
            job_id=job.id,
            name=parsed.get("name") or filename,
            email=parsed.get("email", ""),
            phone=parsed.get("phone", ""),
            source_filename=filename,
            raw_cv_text=text,
            parsed_cv=parsed,
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        created.append(candidate_summary_dict(candidate))
    return {"created": created, "errors": errors}


@router.get("/candidates")
def list_candidates(job_id: int | None = None, status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Candidate)
    if job_id:
        query = query.filter(Candidate.job_id == job_id)
    if status:
        query = query.filter(Candidate.status == status)
    candidates = query.order_by(Candidate.created_at.desc()).all()
    return [candidate_summary_dict(c) for c in candidates]


@router.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate_detail_dict(candidate)


@router.patch("/candidates/{candidate_id}/status")
def update_status(candidate_id: int, body: StatusUpdateRequest, db: Session = Depends(get_db)):
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if body.status not in CANDIDATE_STATUSES:
        raise HTTPException(status_code=422, detail=f"Status must be one of: {', '.join(CANDIDATE_STATUSES)}")
    candidate.status = body.status
    db.commit()
    return candidate_summary_dict(candidate)


@router.delete("/candidates/{candidate_id}")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    db.delete(candidate)
    db.commit()
    return {"deleted": candidate_id}
