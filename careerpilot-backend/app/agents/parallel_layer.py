from __future__ import annotations

import asyncio

from app.agents.analysis.job_agent import JobAgent
from app.agents.analysis.resume_agent import ResumeAgent
from app.models import JobAnalysis, ResumeAnalysis


class ParallelAnalysisLayer:
    def __init__(self) -> None:
        self.resume_agent = ResumeAgent()
        self.job_agent = JobAgent()

    async def run(self, resume_text: str, job_description_text: str) -> tuple[ResumeAnalysis, JobAnalysis]:
        resume_task = self.resume_agent.analyze(resume_text)
        job_task = self.job_agent.analyze(job_description_text)
        resume_analysis, job_analysis = await asyncio.gather(resume_task, job_task)
        return resume_analysis, job_analysis
