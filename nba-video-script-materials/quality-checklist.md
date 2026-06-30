# Quality Checklist

Run this checklist before returning the final JSON.

## Data Correctness

- Every stat, score, ranking, game date, player name, and team name comes from SQL result rows.
- No IDs are invented.
- `GAME_ID`/`game_id` values are copied exactly from database rows.
- Season and spring date logic is correct.
- No nonexistent tables were used.

## Material Correctness

- Every material exists in `nba_cms_prod.video_material`.
- Every selected material has a non-empty `news_id`.
- `segments[].material_ids` are `video_material.id`, not `news_id`.
- `segments[].news_ids` are copied from `video_material.news_id`.
- `video_file` is not treated as the final playback source.
- Long/full-game materials are not used unless the user explicitly requested them.

## Relevance

- Each segment has at least one relevant material.
- Exact `game_id` and exact player/action matches are preferred over generic highlights.
- If a segment uses fallback material, the fallback is explained in `warnings` or `selection_reason`.
- Avoid duplicate clips unless the same play is intentionally reused.

## Script Quality

- The hook is immediate and specific.
- Each segment has one clear point.
- Claims are grounded in evidence.
- The script is natural Chinese and ready for TTS.
- Total estimated duration is within the requested range.

## Output Validity

- Return valid JSON.
- `success` is true only if the script and material allocation are complete.
- Include `queries` with table names and proxy `query_hash` values when available.
- Do not include Bearer tokens, environment variable values, raw secrets, or full authentication headers.

