---
name: nba-video-script-materials
description: Generates NBA short-video scripts with matching video material IDs/news_ids using the NBA SQL Proxy API. Use when asked to plan an NBA commentary video, create segment scripts, select supporting clips, allocate video materials, or return script plus material IDs for downstream video generation.
---

# NBA Video Script + Material Planner

## Goal

Given a natural-language NBA video topic, produce a structured script and a segment-by-segment material allocation. The output is a plan only: do not synthesize voice, download videos, run FFmpeg, or create the final video.

The final answer must include:

- A complete Chinese commentary script split into segments.
- Matching `video_material.id` and `news_id` for each segment.
- Evidence SQL/data used to support the script.
- Material selection rationale.

## Required References

Read these files before doing the task:

- `db-query-api.md` for the SQL proxy API and authentication.
- `database-schema.md` for table names and column guidance.
- `sql-recipes.md` for safe query patterns and examples.
- `output-contract.md` for the final JSON shape.
- `quality-checklist.md` before returning the final answer.
- `examples.md` when a concrete end-to-end example is useful.

## Workflow

1. Parse the user topic.
   - Identify target teams, players, season, game, date, narrative angle, desired duration, and required visual themes.
   - If the topic implies a specific game or series, first resolve the real `GAME_ID`/`game_id`.

2. Query factual NBA data.
   - Use the SQL proxy API only.
   - Use only `SELECT` or `WITH`.
   - Prefer schema-qualified tables such as `nba_game_prod.kb_tbs`, `nba_game_prod.kb_pbs`, `nba_game_prod.kb_pbp`, and `nba_cms_prod.video_material`.
   - Never invent tables. If unsure, query `information_schema.COLUMNS` or `information_schema.TABLES`.

3. Build the narrative.
   - Create 4-7 segments for a 90-180 second video.
   - Each segment must have a clear point supported by real data or real footage.
   - Avoid unsupported claims. Put uncertainty in `assumptions`.

4. Query video materials.
   - Use `nba_cms_prod.video_material`.
   - Prefer `type = 1`, `duration <= 90`, non-empty `news_id`, and non-empty `video_file`.
   - Join `nba_cms_prod.item_info` on `item_info.id = video_material.news_id` to get `star`.
   - For playable downstream usage, return `news_id`; do not depend on `video_file` direct URLs.

5. Allocate clips.
   - Every segment should have at least 1-3 relevant materials.
   - Prefer clips with exact player/team/action matches, higher `star`, shorter duration, and matching `game_id`.
   - If there are not enough exact materials, use broader context clips and explain the fallback.

6. Return only the structured result.
   - Use the JSON contract in `output-contract.md`.
   - Include SQL summaries and query hashes if available.
   - Do not include secrets or Bearer tokens.

## Hard Rules

- Do not fabricate `video_material.id`, `news_id`, `game_id`, player IDs, team IDs, scores, or stats.
- Do not use write SQL or multiple SQL statements.
- Do not use nonexistent convenience tables like `player_game_stats` or `nba_player_game_stats`.
- Do not treat `video_file` as reliably playable. Use `news_id` for playback systems.
- Do not return an empty script. If data is insufficient, return `success=false` with `blocking_reason`.

