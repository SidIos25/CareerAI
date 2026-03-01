from __future__ import annotations

from app.agents.guardrails import with_guardrails
from app.agents.root_agent import RootAgent
from app.models import ResumeAnalysis


class ResumeAgent(RootAgent):
    async def analyze(self, resume_text: str) -> ResumeAnalysis:
        system_prompt = with_guardrails(
            task_instruction="Analyze resume content into a factual profile summary.",
            output_contract=(
                "Return JSON object with keys: summary (string), skills (string[]), "
                "experiences (string[]), strengths (string[])."
            ),
        )
        user_prompt = f"Analyze this resume:\n\n{resume_text}"
        data = await self.ask_json(
            system_prompt,
            user_prompt,
            fallback={"summary": "", "skills": [], "experiences": [], "strengths": []},
        )
        return ResumeAnalysis.model_validate(data)
