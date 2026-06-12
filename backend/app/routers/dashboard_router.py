from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import CANDIDATE_STATUSES, Candidate, Job
from .candidates_router import candidate_summary_dict

router = APIRouter(prefix="/api", tags=["dashboard"], dependencies=[Depends(get_current_user)])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).all()
    analyzed = [c for c in candidates if c.analysis]
    by_status = {status: 0 for status in CANDIDATE_STATUSES}
    for c in candidates:
        by_status[c.status] = by_status.get(c.status, 0) + 1
    recent = sorted(candidates, key=lambda c: c.created_at, reverse=True)[:8]
    return {
        "jobs": db.query(Job).count(),
        "candidates": len(candidates),
        "analyzed": len(analyzed),
        "interviewed": sum(1 for c in candidates if c.evaluation),
        "reports": sum(1 for c in candidates if c.final_report),
        "average_cv_score": round(
            sum(c.analysis.total_score for c in analyzed) / len(analyzed), 1
        ) if analyzed else None,
        "by_status": by_status,
        "recent_candidates": [candidate_summary_dict(c) for c in recent],
    }


@router.get("/ranking")
def ranking(job_id: int | None = None, db: Session = Depends(get_db)):
    """Candidates ranked by final score (60% CV match + 40% interview).

    Candidates missing one of the two scores are ranked on the available one.
    """
    query = db.query(Candidate)
    if job_id:
        query = query.filter(Candidate.job_id == job_id)
    rows = []
    for c in query.all():
        cv = c.analysis.total_score if c.analysis else None
        interview = c.evaluation.score if c.evaluation else None
        if cv is not None and interview is not None:
            final = round(cv * 0.6 + interview * 0.4, 1)
        else:
            final = cv if cv is not None else interview
        item = candidate_summary_dict(c)
        item["final_score"] = final
        item["report_recommendation"] = c.final_report.recommendation if c.final_report else None
        rows.append(item)
    rows.sort(key=lambda r: (r["final_score"] is None, -(r["final_score"] or 0)))
    return rows
