from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..ai import service as ai
from ..auth import get_current_user
from ..database import get_db
from ..models import Job
from ..schemas import JobCreateRequest

router = APIRouter(prefix="/api/jobs", tags=["jobs"], dependencies=[Depends(get_current_user)])


def job_to_dict(job: Job, include_description: bool = False) -> dict:
    data = {
        "id": job.id,
        "title": job.title,
        "extracted": job.extracted,
        "candidate_count": len(job.candidates),
        "created_at": job.created_at.isoformat(),
    }
    if include_description:
        data["raw_description"] = job.raw_description
    return data


@router.post("")
def create_job(body: JobCreateRequest, db: Session = Depends(get_db)):
    try:
        extracted = ai.extract_job(body.description)
    except ai.AIServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    job = Job(
        title=extracted.get("job_title") or "Untitled Role",
        raw_description=body.description,
        extracted=extracted,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job_to_dict(job, include_description=True)


@router.get("")
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return [job_to_dict(j) for j in jobs]


@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_to_dict(job, include_description=True)


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"deleted": job_id}
