from __future__ import annotations

from statistics import mean

from app.models import ConfidenceReport, GapAnalysis, PrioritizedGap, ResumeAnalysis


class ConfidenceAgent:
    async def score(
        self,
        resume: ResumeAnalysis,
        gap: GapAnalysis,
        prioritized_gaps: list[PrioritizedGap],
    ) -> ConfidenceReport:
        resume_skill_count = len(resume.skills)
        missing_count = len(gap.missing_skills)

        if prioritized_gaps:
            weighted = [max((item.impact + item.urgency - item.effort), 1) for item in prioritized_gaps]
            priority_factor = min(mean(weighted) / 10, 1)
        else:
            priority_factor = 0.3

        base = 0.7 if resume_skill_count else 0.35
        penalty = min(missing_count * 0.06, 0.45)
        score = max(min(base - penalty + (priority_factor * 0.25), 0.98), 0.05)

        explainability = {
            "resume_skill_count": resume_skill_count,
            "missing_skill_count": missing_count,
            "priority_factor": round(priority_factor, 3),
            "formula": "score = clip(base - penalty + priority_factor*0.25, 0.05, 0.98)",
        }

        return ConfidenceReport(
            score=round(score, 3),
            rationale="Confidence increases with stronger overlap and clearer high-impact priorities.",
            assumptions=[
                "Resume text is up-to-date and complete",
                "Job description accurately reflects hiring criteria",
                "Estimated effort reflects realistic learning time",
            ],
            explainability=explainability,
        )
