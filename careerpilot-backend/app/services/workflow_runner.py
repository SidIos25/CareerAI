from __future__ import annotations

from app.agents.parallel_layer import ParallelAnalysisLayer
from app.agents.strategy.confidence_agent import ConfidenceAgent
from app.agents.strategy.gap_agent import GapAgent
from app.agents.strategy.prioritizer_agent import PrioritizerAgent
from app.agents.strategy.roadmap_agent import RoadmapAgent
from app.models import WorkflowInput, WorkflowOutput


class WorkflowRunner:
    def __init__(self) -> None:
        self.parallel_layer = ParallelAnalysisLayer()
        self.gap_agent = GapAgent()
        self.prioritizer_agent = PrioritizerAgent()
        self.roadmap_agent = RoadmapAgent()
        self.confidence_agent = ConfidenceAgent()

    async def run(self, payload: WorkflowInput) -> WorkflowOutput:
        resume_analysis, job_analysis = await self.parallel_layer.run(
            payload.resume_text,
            payload.job_description_text,
        )
        gap_analysis = await self.gap_agent.analyze(resume_analysis, job_analysis)
        prioritized_gaps = await self.prioritizer_agent.prioritize(gap_analysis, job_analysis)
        roadmap = await self.roadmap_agent.build(prioritized_gaps)
        confidence = await self.confidence_agent.score(resume_analysis, gap_analysis, prioritized_gaps)

        return WorkflowOutput(
            resume_analysis=resume_analysis,
            job_analysis=job_analysis,
            gap_analysis=gap_analysis,
            prioritized_gaps=prioritized_gaps,
            roadmap=roadmap,
            confidence=confidence,
        )
