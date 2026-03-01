from __future__ import annotations

import os

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm

from app.agents.guardrails import with_guardrails


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _adk_openai_model() -> LiteLlm:
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    litellm_model_name = model_name if "/" in model_name else f"openai/{model_name}"
    timeout_seconds = _env_float("OPENAI_TIMEOUT_SECONDS", 45.0)
    max_retries = _env_int("OPENAI_MAX_RETRIES", 1)
    top_p = _env_float("OPENAI_TOP_P", 0.1)
    return LiteLlm(
        model=litellm_model_name,
        timeout=timeout_seconds,
        num_retries=max_retries,
        top_p=top_p,
    )


resume_agent = LlmAgent(
    name="ResumeAnalyzer",
    model=_adk_openai_model(),
    description="Analyzes resume data into a structured JSON summary.",
    instruction=with_guardrails(
        task_instruction=(
            "Analyze the provided resume text into a factual profile. Only extract what is present; do not infer role, seniority, or impact. "
            "If a field is unclear, leave arrays empty or set scalar values to 'unknown'."
        ),
        output_contract=(
            "Return JSON object with keys: summary (string), skills (string[]), experiences (string[]), strengths (string[])."
        ),
    ),
    output_key="resume_analysis_json",
)

job_agent = LlmAgent(
    name="JobAnalyzer",
    model=_adk_openai_model(),
    description="Analyzes job descriptions into structured hiring requirements.",
    instruction=with_guardrails(
        task_instruction=(
            "Extract hiring requirements directly from the job description text. Only include items explicitly present; do not backfill from industry patterns. "
            "If role or seniority is ambiguous, set to 'unknown'."
        ),
        output_contract=(
            "Return JSON object with keys: role (string), required_skills (string[]), preferred_skills (string[]), responsibilities (string[]), seniority (string)."
        ),
    ),
    output_key="job_analysis_json",
)

parallel_analysis_agent = ParallelAgent(
    name="ParallelAnalysis",
    description="Runs resume and job analysis in parallel.",
    sub_agents=[resume_agent, job_agent],
)

gap_agent = LlmAgent(
    name="GapAnalyzer",
    model=_adk_openai_model(),
    description="Performs structured skill gap analysis from resume and job analysis.",
    instruction=with_guardrails(
        task_instruction=(
            "Perform a strict resume-to-job gap analysis using only the provided structured inputs. "
            "Mark a skill as matched only when there is direct overlap or clearly equivalent phrasing; if uncertain, treat as missing. "
            "List transferable_experiences only when resume evidence explicitly supports the job requirement. "
            "List risks as concrete hiring risks caused by missing/weak evidence, not generic advice."
        ),
        output_contract=(
            "Return JSON object with keys: matched_skills (string[]), missing_skills (string[]), transferable_experiences (string[]), risks (string[])."
        ),
    ),
    output_key="gap_analysis_json",
)

prioritizer_agent = LlmAgent(
    name="GapPrioritizer",
    model=_adk_openai_model(),
    description="Prioritizes missing skills by impact, urgency, and effort.",
    instruction=with_guardrails(
        task_instruction=(
            "Prioritize only the missing_skills from gap analysis. Use a conservative rubric: impact=importance for role success, urgency=likelihood screened early, effort=time/complexity to close. "
            "Use 1-5 integers only; when evidence is weak, choose mid-to-low values. "
            "Reason must reference job/resume evidence and be one concise sentence without speculation."
        ),
        output_contract=(
            "Return JSON object with key items (array). Each item includes skill (string), impact (1-5 int), urgency (1-5 int), effort (1-5 int), reason (string)."
        ),
    ),
    output_key="prioritized_gaps_json",
)

roadmap_agent = LlmAgent(
    name="RoadmapBuilder",
    model=_adk_openai_model(),
    description="Builds a practical weekly roadmap from prioritized gaps.",
    instruction=with_guardrails(
        task_instruction=(
            "Create a practical weekly upskilling roadmap from prioritized gaps only. Sequence from foundational to advanced; avoid parallel overload. "
            "Each week must have one clear goal, 2-4 concrete actions, and one verifiable deliverable. "
            "Do not invent certifications/tools/experience not present in prior analysis. If input is sparse, return a short conservative roadmap instead of guessing."
        ),
        output_contract=(
            "Return JSON object with key steps (array). Each step includes week (int), goal (string), actions (string[]), deliverable (string)."
        ),
    ),
    output_key="roadmap_json",
)

confidence_agent = LlmAgent(
    name="ConfidenceExplainer",
    model=_adk_openai_model(),
    description="Produces confidence scoring and explainability for the generated plan.",
    instruction=with_guardrails(
        task_instruction="Score confidence and provide explainability for this career plan.",
        output_contract=(
            "Return JSON object with keys: score (float 0..1), rationale (string), "
            "assumptions (string[]), explainability (object)."
        ),
    ),
    output_key="confidence_json",
)

result_formatter_agent = LlmAgent(
    name="ResultFormatter",
    model=_adk_openai_model(),
    description="Formats the final pipeline output into a readable markdown report for ADK Web UI.",
    instruction=(
        "You are a response formatter for ADK Web UI. "
        "Using prior agent outputs from this run, generate a clean markdown report for the user. "
        "Do not invent data; if a section has insufficient evidence, say 'Not enough information'. "
        "Use exactly these sections in order: "
        "1) Career Fit Snapshot, 2) Matched Skills, 3) Missing Skills (Top Gaps), "
        "4) Priority Actions, 5) Weekly Roadmap, 6) Confidence. "
        "Use short bullets, keep it concise, and avoid raw JSON in the final answer."
    ),
)

root_agent = SequentialAgent(
    name="CareerPilotPipeline",
    description="Parallel analysis followed by gap analysis, prioritization, roadmap, confidence scoring, and final UI formatting.",
    sub_agents=[
        parallel_analysis_agent,
        gap_agent,
        prioritizer_agent,
        roadmap_agent,
        confidence_agent,
        result_formatter_agent,
    ],
)
