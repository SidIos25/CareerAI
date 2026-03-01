from __future__ import annotations

from app.agents.guardrails import with_guardrails
from app.agents.root_agent import RootAgent
from app.models import GapAnalysis, JobAnalysis, PrioritizedGap


class PrioritizerAgent(RootAgent):
    async def prioritize(self, gap: GapAnalysis, job: JobAnalysis) -> list[PrioritizedGap]:
        system_prompt = with_guardrails(
            task_instruction=(
                "Prioritize only the missing_skills from gap analysis. "
                "Score each item conservatively with explicit rubric: impact=importance for role success, "
                "urgency=likelihood it is screened early in hiring, effort=time/complexity to close. "
                "Use 1-5 integers only and avoid inflated scores; when evidence is weak, choose mid-to-low values. "
                "Reason must reference job/resume evidence and be one concise sentence without speculation."
            ),
            output_contract=(
                "Return JSON object with key items (array). "
                "Each item must include: skill (string), impact (1-5 int), urgency (1-5 int), "
                "effort (1-5 int), reason (string)."
            ),
        )
        user_prompt = (
            "Gap Analysis:\n"
            f"{gap.model_dump_json(indent=2)}\n\n"
            "Job Analysis:\n"
            f"{job.model_dump_json(indent=2)}"
        )
        data = await self.ask_json(system_prompt, user_prompt, fallback={"items": []})
        items = data.get("items", [])
        return [PrioritizedGap.model_validate(item) for item in items]
