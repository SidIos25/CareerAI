from __future__ import annotations

from app.agents.guardrails import with_guardrails
from app.agents.root_agent import RootAgent
from app.models import JobAnalysis


class JobAgent(RootAgent):
    async def analyze(self, job_description_text: str) -> JobAnalysis:
        system_prompt = with_guardrails(
            task_instruction=(
                "Extract hiring requirements directly from the job description text. "
                "Only include items explicitly present; do not backfill missing requirements from common industry patterns. "
                "If role or seniority is ambiguous, set to 'unknown'."
            ),
            output_contract=(
                "Return JSON object with keys: role (string), required_skills (string[]), "
                "preferred_skills (string[]), responsibilities (string[]), seniority (string)."
            ),
        )
        user_prompt = f"Analyze this job description:\n\n{job_description_text}"
        data = await self.ask_json(
            system_prompt,
            user_prompt,
            fallback={
                "role": "Unknown",
                "required_skills": [],
                "preferred_skills": [],
                "responsibilities": [],
                "seniority": "unknown",
            },
        )
        return JobAnalysis.model_validate(data)
