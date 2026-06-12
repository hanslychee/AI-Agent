"""Pydantic request bodies. Responses are serialized as plain dicts in routers."""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class JobCreateRequest(BaseModel):
    description: str = Field(min_length=30, description="Full job description text")


class StatusUpdateRequest(BaseModel):
    status: str


class EvaluationRequest(BaseModel):
    ratings: dict[str, int]
    interviewer_notes: str = ""


class ReportUpdateRequest(BaseModel):
    salary_range: str | None = None
    hr_notes: str | None = None
