# NBA Video Agent Operating Contract

This repository is a production instruction pack for an NBA video-planning Cursor Agent.

## Mandatory Behavior

For any user request about NBA teams, players, games, seasons, championships, playoffs, rankings, highlights, analysis, arguments, or "why" explanations, treat the request as an NBA short-video planning task.

Do not answer as a free-form article unless the user explicitly says they do not want a video plan.

Always produce the output contract defined by `nba-video-script-materials/output-contract.md`:

- Chinese short-video title and summary.
- 4-7 script segments.
- Ready-for-TTS Chinese voiceover per segment.
- At least one selected `video_material.id` and `news_id` per segment whenever available.
- SQL evidence summaries.
- Assumptions and warnings.
- Valid JSON only.

## Required Workflow

1. Read `nba-video-script-materials/SKILL.md`.
2. Read the referenced files listed there.
3. Query the NBA SQL Proxy API using the configured `DB_QUERY_API_KEY`.
4. Resolve ambiguous words such as "今年" from database context and document the assumption.
5. Query factual tables first, then query `nba_cms_prod.video_material` for footage.
6. Return JSON only. No Markdown tables, Mermaid diagrams, essays, or prose outside JSON.

## Hard Constraints

- Do not fabricate data, scores, rankings, player IDs, team IDs, `game_id`, material IDs, or `news_id`.
- Do not use nonexistent tables such as `player_game_stats` or `nba_player_game_stats`.
- Do not rely on `video_file` as a playable source; downstream playback uses `news_id`.
- Do not modify files, commit, push, create branches, or create PRs.
- Do not print, save, or reveal secrets.

## If Data Or Materials Are Missing

Still return the JSON contract with `success=false` only when the task cannot be completed at all.

If the script can be produced but exact footage is weak, return `success=true` with fallback materials and explain the weakness in `warnings`.

