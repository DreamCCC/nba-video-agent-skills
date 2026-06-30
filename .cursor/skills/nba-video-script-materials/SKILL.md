---
name: nba-video-script-materials
description: Automatically plans NBA short videos from natural-language NBA topics. Use for any NBA request involving teams, players, games, seasons, championships, playoffs, highlights, analysis, arguments, or why/how explanations. Produces Chinese script segments with matched video_material.id/news_id values by querying the NBA SQL Proxy API.
---

# NBA Video Script + Material Planner

## Mandatory Trigger

Use this skill for any NBA topic unless the user explicitly says they do not want a video plan.

Examples that must trigger this skill:

- `论证马刺为什么会错失今年的总冠军`
- `为什么勇士第四节崩盘`
- `帮我讲讲库里的三分如何改变比赛`
- `做一个文班亚马防守影响力的视频`

## Required References

Read these repository files before answering:

- `nba-video-script-materials/SKILL.md`
- `nba-video-script-materials/db-query-api.md`
- `nba-video-script-materials/database-schema.md`
- `nba-video-script-materials/sql-recipes.md`
- `nba-video-script-materials/output-contract.md`
- `nba-video-script-materials/quality-checklist.md`

Read `nba-video-script-materials/examples.md` when you need a concrete example.

## Required Output

Return valid JSON only, following `nba-video-script-materials/output-contract.md`.

The JSON must contain:

- `success`
- `topic`
- `title`
- `summary`
- `target_duration_s`
- `segments`
- `materials`
- `queries`
- `assumptions`
- `warnings`
- `quality_checks`

Do not return Markdown tables, Mermaid diagrams, or an essay outside JSON.

## Required Workflow

1. Interpret the raw user prompt as an NBA short-video topic.
2. Resolve ambiguous time words such as "今年" using database context.
3. Query factual tables through the NBA SQL Proxy API.
4. Build a 90-180 second Chinese vertical-video narrative with 4-7 segments.
5. Query `nba_cms_prod.video_material` and select footage for every segment.
6. Select 2-4 clips per segment by default. Use 1 clip only if it alone covers that segment's `estimated_duration_s`.
7. Calculate selected material duration for every segment. Segment coverage must be at least 100%, target 115%.
8. Calculate total material duration. Total coverage must be at least 100%, target 115%.
9. Prefer clips with non-empty `news_id`, exact `game_id`, exact player/team/action matches, higher `item_info.star`, and shorter duration.
10. If exact clips are unavailable or too short, add fallback clips and explain in `warnings`.
11. Return the JSON contract only.

## Hard Rules

- Never fabricate stats, scores, IDs, material IDs, `news_id`, or `game_id`.
- Never use nonexistent tables like `player_game_stats` or `nba_player_game_stats`.
- Never treat `video_file` as the final playable URL. Downstream playback uses `news_id`.
- Never return `success=true` if selected material duration is shorter than narration duration.
- Never reveal or save `DB_QUERY_API_KEY`.
- Never modify repo files, commit, push, create branches, or open PRs.

