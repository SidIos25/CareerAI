from __future__ import annotations

from fastapi import FastAPI

from app.models import WorkflowInput, WorkflowOutput
from app.services.workflow_runner import WorkflowRunner

app = FastAPI(title="CareerPilot AI", version="1.0.0")
runner = WorkflowRunner()


@app.get("/api/health", tags=["careerpilot"])
async def health_check() -> dict[str, str]:
	return {"status": "ok"}


@app.post("/api/analyze", response_model=WorkflowOutput, tags=["careerpilot"])
async def analyze_career_fit(payload: WorkflowInput) -> WorkflowOutput:
	return await runner.run(payload)
