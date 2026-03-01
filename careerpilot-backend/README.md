# CareerPilot Backend

Backend service for CareerPilot AI using FastAPI and ADK-compatible agents.

## Project Structure

- `app/main.py` - FastAPI app and API route definitions
- `app/models.py` - request/response schemas
- `app/agents/` - analysis and strategy agents
- `app/services/workflow_runner.py` - orchestration layer
- `run.py` - local entry point

## Setup

From `careerpilot-backend`:

```bash
pip install -r requirements.txt
```

Create `.env`:

```env
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT_SECONDS=45
OPENAI_MAX_RETRIES=1
OPENAI_TOP_P=0.1
```

Run locally:

```bash
python run.py
```

## Run with ADK

From workspace root (`CarrerAI`):

```bash
adk web adk_apps
```

or:

```bash
powershell -ExecutionPolicy Bypass -File .\start_adk_web.ps1
```

ADK discovers `adk_apps/careerpilot_ai/agent.py`, which imports `root_agent` from `careerpilot-backend/app/agents/adk_root_agent.py`.

## API Endpoints

- `GET /api/health`
- `POST /api/analyze`

Sample request:

```json
{
  "resume_text": "...",
  "job_description_text": "..."
}
```
