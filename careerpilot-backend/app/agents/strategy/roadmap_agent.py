from __future__ import annotations

from app.agents.guardrails import with_guardrails
from app.agents.root_agent import RootAgent
from app.models import PrioritizedGap, RoadmapStep


class RoadmapAgent(RootAgent):
    async def build(self, prioritized_gaps: list[PrioritizedGap]) -> list[RoadmapStep]:
        system_prompt = with_guardrails(
            task_instruction=(
                "Create a practical weekly upskilling roadmap from prioritized gaps only. "
                "Sequence steps from foundational to advanced dependencies and avoid parallel overload. "
                "Each week should have a single clear goal, 2-4 concrete actions, and one verifiable deliverable. "
                "Do not invent certifications, tools, or experience requirements not present in prior analysis. "
                "If prioritized input is sparse, return a short conservative roadmap rather than filling with guesses."
            ),
            output_contract=(
                "Return JSON object with key steps (array). "
                "Each step must include: week (int), goal (string), actions (string[]), deliverable (string)."
            ),
        )
        user_prompt = "Prioritized skill gaps:\n" + str([item.model_dump() for item in prioritized_gaps])
        data = await self.ask_json(system_prompt, user_prompt, fallback={"steps": []})
        return [RoadmapStep.model_validate(step) for step in data.get("steps", [])]
