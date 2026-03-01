from __future__ import annotations

from app.agents.guardrails import with_guardrails
from app.agents.root_agent import RootAgent
from app.models import GapAnalysis, JobAnalysis, ResumeAnalysis


class GapAgent(RootAgent):
    async def analyze(self, resume: ResumeAnalysis, job: JobAnalysis) -> GapAnalysis:
        system_prompt = with_guardrails(
            task_instruction=(
                "Perform a strict resume-to-job gap analysis using only the provided structured inputs. "
                "Mark a skill as matched only when there is direct overlap in wording or a clearly equivalent term. "
                "If equivalence is uncertain, treat it as missing instead of matched. "
                "List transferable_experiences only when resume evidence explicitly supports the job requirement. "
                "List risks as concrete hiring risks caused by missing/weak evidence, not generic advice."
            ),
            output_contract=(
                "Return JSON object with keys: matched_skills (string[]), missing_skills (string[]), "
                "transferable_experiences (string[]), risks (string[])."
            ),
        )
        user_prompt = (
            "Resume Analysis:\n"
            f"{resume.model_dump_json(indent=2)}\n\n"
            "Job Analysis:\n"
            f"{job.model_dump_json(indent=2)}"
        )
        data = await self.ask_json(
            system_prompt,
            user_prompt,
            fallback={
                "matched_skills": [],
                "missing_skills": [],
                "transferable_experiences": [],
                "risks": [],
            },
        )
        return GapAnalysis.model_validate(data)
