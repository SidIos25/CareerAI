from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ResumeAnalysis(BaseModel):
    summary: str = Field(..., description="High-level summary of candidate profile")
    skills: list[str] = Field(default_factory=list)
    experiences: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)


class JobAnalysis(BaseModel):
    role: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    seniority: str = "unknown"


class GapAnalysis(BaseModel):
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    transferable_experiences: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class PrioritizedGap(BaseModel):
    skill: str
    impact: int = Field(..., ge=1, le=5)
    urgency: int = Field(..., ge=1, le=5)
    effort: int = Field(..., ge=1, le=5)
    reason: str


class RoadmapStep(BaseModel):
    week: int
    goal: str
    actions: list[str] = Field(default_factory=list)
    deliverable: str


class ConfidenceReport(BaseModel):
    score: float = Field(..., ge=0, le=1)
    rationale: str
    assumptions: list[str] = Field(default_factory=list)
    explainability: dict[str, Any] = Field(default_factory=dict)


class WorkflowInput(BaseModel):
    resume_text: str
    job_description_text: str


class WorkflowOutput(BaseModel):
    resume_analysis: ResumeAnalysis
    job_analysis: JobAnalysis
    gap_analysis: GapAnalysis
    prioritized_gaps: list[PrioritizedGap]
    roadmap: list[RoadmapStep]
    confidence: ConfidenceReport
