# Cursor Agent Skills For NBA Auto Video

This directory contains skills intended for a remote Cursor Agent that replaces the current in-process `unified_agent` planning step.

## Skills

- `nba-video-script-materials`: generate an NBA short-video script and allocate matching `video_material.id` / `news_id` values by querying the NBA SQL Proxy API.

## Required Runtime Secret

The remote Agent runtime must provide:

```text
DB_QUERY_API_KEY
```

Do not commit the real token to this repository.

## Expected Agent Responsibility

The remote Agent should produce a structured plan only:

- Chinese segment script.
- Material IDs and `news_id`s per segment.
- SQL evidence summaries.
- Warnings for fallback/weak material matches.

It should not run TTS, download videos, call `videoPlay`, use FFmpeg, or produce the final media file.

## Smoke Test

Run a one-off Cursor Cloud Agent call against this repository:

```bash
CURSOR_API_KEY="<your_cursor_api_key>" python3 scripts/test_cursor_agent_once.py
```

The test script follows the AskNBA lifecycle:

- `POST /v1/agents` creates a fresh temporary agent.
- `GET /v1/agents/{agent_id}/runs/{run_id}/stream` streams the answer.
- `DELETE /v1/agents/{agent_id}` deletes the temporary agent after the run. If deletion fails, it archives the agent.

The default smoke prompt is read-only. It verifies the skill files and does not call the NBA SQL Proxy API.

