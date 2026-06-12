"""CV scoring, interview questions, interview evaluation and final reports."""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ..ai import service as ai
from ..auth import get_current_user
from ..database import get_db
from ..models import Analysis, Candidate, FinalReport, InterviewEvaluation, QuestionSet
from ..schemas import EvaluationRequest, ReportUpdateRequest
from ..services.pdf_export import build_report_pdf
from .candidates_router import candidate_detail_dict

router = APIRouter(prefix="/api/candidates", tags=["analysis"], dependencies=[Depends(get_current_user)])


def _get_candidate(candidate_id: int, db: Session) -> Candidate:
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.post("/{candidate_id}/analyze")
def analyze(candidate_id: int, db: Session = Depends(get_db)):
    """Score the candidate's CV against the job and generate the HR summary."""
    candidate = _get_candidate(candidate_id, db)
    try:
        result = ai.score_candidate(candidate.job.extracted, candidate.parsed_cv)
    except ai.AIServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    if candidate.analysis:
        db.delete(candidate.analysis)
        db.flush()
    db.add(Analysis(
        candidate_id=candidate.id,
        total_score=result["total_score"],
        match_percentage=result["match_percentage"],
        recommendation=result["recommendation"],
        result=result,
    ))
    db.commit()
    db.refresh(candidate)
    return candidate_detail_dict(candidate)


@router.post("/{candidate_id}/questions")
def generate_questions(candidate_id: int, db: Session = Depends(get_db)):
    """Generate tailored interview questions for the candidate."""
    candidate = _get_candidate(candidate_id, db)
    analysis = candidate.analysis.result if candidate.analysis else None
    try:
        questions = ai.generate_questions(candidate.job.extracted, candidate.parsed_cv, analysis)
    except ai.AIServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    if candidate.question_set:
        db.delete(candidate.question_set)
        db.flush()
    db.add(QuestionSet(candidate_id=candidate.id, questions=questions))
    db.commit()
    db.refresh(candidate)
    return candidate_detail_dict(candidate)


@router.post("/{candidate_id}/evaluation")
def submit_evaluation(candidate_id: int, body: EvaluationRequest, db: Session = Depends(get_db)):
    """Save the HR interview scorecard and generate a short AI evaluation."""
    candidate = _get_candidate(candidate_id, db)

    missing = [c for c in ai.EVALUATION_CATEGORIES if c not in body.ratings]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing ratings for: {', '.join(missing)}")
    invalid = [c for c, v in body.ratings.items() if not 1 <= int(v) <= 5]
    if invalid:
        raise HTTPException(status_code=422, detail=f"Ratings must be 1-5: {', '.join(invalid)}")

    score = ai.compute_interview_score(body.ratings)
    try:
        summary = ai.summarize_interview(
            candidate.name, candidate.job.title, body.ratings, body.interviewer_notes, score
        )
    except ai.AIServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    if candidate.evaluation:
        db.delete(candidate.evaluation)
        db.flush()
    db.add(InterviewEvaluation(
        candidate_id=candidate.id,
        ratings=body.ratings,
        interviewer_notes=body.interviewer_notes,
        score=score,
        ai_summary=summary,
    ))
    if candidate.status in ("New", "Shortlisted", "Interview Scheduled"):
        candidate.status = "Interviewed"
    db.commit()
    db.refresh(candidate)
    return candidate_detail_dict(candidate)


@router.post("/{candidate_id}/report")
def generate_report(candidate_id: int, db: Session = Depends(get_db)):
    """Generate the final recruitment report (requires CV analysis + interview)."""
    candidate = _get_candidate(candidate_id, db)
    if not candidate.analysis:
        raise HTTPException(status_code=409, detail="Run the CV analysis first.")
    if not candidate.evaluation:
        raise HTTPException(status_code=409, detail="Submit the interview evaluation first.")

    try:
        content = ai.generate_final_report(
            candidate_name=candidate.name,
            job_title=candidate.job.title,
            analysis_result=candidate.analysis.result,
            cv_score=candidate.analysis.total_score,
            interview_score=candidate.evaluation.score,
            ratings=candidate.evaluation.ratings,
            notes=candidate.evaluation.interviewer_notes,
            interview_summary=candidate.evaluation.ai_summary,
        )
    except ai.AIServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    existing = candidate.final_report
    if existing:
        # Preserve HR-entered fields across regenerations.
        salary_range, hr_notes = existing.salary_range, existing.hr_notes
        db.delete(existing)
        db.flush()
    else:
        salary_range, hr_notes = "", ""
    db.add(FinalReport(
        candidate_id=candidate.id,
        content=content,
        recommendation=content["recommendation"],
        salary_range=salary_range,
        hr_notes=hr_notes,
    ))
    db.commit()
    db.refresh(candidate)
    return candidate_detail_dict(candidate)


@router.patch("/{candidate_id}/report")
def update_report(candidate_id: int, body: ReportUpdateRequest, db: Session = Depends(get_db)):
    """Update HR-owned report fields: suggested salary range and final notes."""
    candidate = _get_candidate(candidate_id, db)
    if not candidate.final_report:
        raise HTTPException(status_code=404, detail="No report generated yet.")
    if body.salary_range is not None:
        candidate.final_report.salary_range = body.salary_range
    if body.hr_notes is not None:
        candidate.final_report.hr_notes = body.hr_notes
    db.commit()
    db.refresh(candidate)
    return candidate_detail_dict(candidate)


@router.get("/{candidate_id}/report/pdf")
def export_report_pdf(candidate_id: int, db: Session = Depends(get_db)):
    candidate = _get_candidate(candidate_id, db)
    if not candidate.final_report:
        raise HTTPException(status_code=404, detail="No report generated yet.")
    pdf = build_report_pdf(
        candidate, candidate.job, candidate.analysis, candidate.evaluation, candidate.final_report
    )
    safe_name = "".join(ch if ch.isalnum() else "_" for ch in candidate.name) or "candidate"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="report_{safe_name}.pdf"'},
    )
