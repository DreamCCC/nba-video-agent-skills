# Database Schema Reference

Always schema-qualify table names.

## Accessible Business Schemas

- `nba_game_prod`: game schedules, box scores, play-by-play, teams, players, season leaders.
- `nba_cms_prod`: video materials, tags, item quality scores.
- `nba_act_prod`, `nba_act_test`: all-star voting/task tables.
- `nba_mkt_prod`, `nba_mkt_test`: marketing/feedback/task tables.
- `nba_trade_prod`: trade/order/payment tables. Avoid unless explicitly asked.

## Core Tables For Video Planning

### `nba_game_prod.kb_tbs`

Team box score by game.

Important columns:

- `SEASON`, `SEASON_TYPE`
- `TEAM_ID`, `TEAM_ABBREVIATION`, `TEAM_NAME`
- `GAME_ID`, `GAME_DATE`, `MATCHUP`, `WL`
- `FGM`, `FGA`, `FG_PCT`, `FG3M`, `FG3A`, `FG3_PCT`
- `FTM`, `FTA`, `REB`, `AST`, `STL`, `BLK`, `TOV`, `PTS`, `PLUS_MINUS`

Use for team-level arguments such as shooting gap, turnovers, rebounding, bench/support, and series game results.

### `nba_game_prod.kb_tbs_period`

Team box score by period.

Use for quarter-by-quarter collapses, fourth-quarter execution, and run analysis.

Important columns mirror `kb_tbs` plus `PERIOD`.

### `nba_game_prod.kb_pbs`

Player box score by game.

Important columns:

- `SEASON`, `SEASON_TYPE`
- `PLAYER_ID`, `PLAYER_NAME`
- `TEAM_ID`, `TEAM_ABBREVIATION`, `TEAM_NAME`
- `GAME_ID`, `GAME_DATE`, `MATCHUP`, `WL`
- `MIN`, `FGM`, `FGA`, `FG_PCT`, `FG3M`, `FG3A`, `FG3_PCT`
- `FTM`, `FTA`, `REB`, `AST`, `STL`, `BLK`, `TOV`, `PTS`, `PLUS_MINUS`

Use this instead of nonexistent tables such as `player_game_stats` or `nba_player_game_stats`.

### `nba_game_prod.kb_pbp`

Play-by-play events.

Important columns:

- `game_id`
- `action_number`
- `period`
- `clock` such as `PT01M38.00S`
- `team_id`, `team_tricode`
- `action_type`, `sub_type`, `descriptor`, `qualifiers`
- `person_id`, `player_name_i`
- `shot_distance`, `shot_result`
- `score_home`, `score_away`
- `description`
- `assist_person_id`, `assist_player_name_i`
- `block_person_id`, `block_player_name_i`
- `steal_person_id`, `steal_player_name_i`

Use for key plays, clutch possessions, turnovers, assists, blocks, steals, and exact game-clock evidence.

### `nba_game_prod.kb_standing`

Regular-season standings only.

Important columns: `season`, `standing_date`, `team_id`, `conference`, `conference_rank`, `wins`, `losses`, `win_pct`.

### `nba_game_prod.kb_team`

Team identity table.

Important columns: `season`, `team_id`, `name`, `abbr`, `city`, `conference`, `division`.

### `nba_game_prod.kb_player`

Player identity table. Use to resolve player IDs.

### `nba_game_prod.kb_pol`

Official player season ranking.

Important columns: `SEASON`, `SEASON_TYPE`, `PER_MODE`, `STAT_CATEGORY`, `PLAYER_ID`, `PLAYER`, `TEAM`, `RANK`, `PTS`, `REB`, `AST`, etc.

Use for league-rank arguments.

### `nba_game_prod.kb_pgt`

Player season totals / per-game stats.

Use for season-level player narratives. This table has `TEAM_ABBREVIATION` but no `TEAM_NAME`; use `kb_pbs`, `kb_tbs`, or `kb_team` if a full team name is required.

## Video Material Tables

### `nba_cms_prod.video_material`

Primary video clip table.

Important columns:

- `id`: material ID. Return this in final output.
- `news_id`: playback/debug ID. Required for signed playable URL downstream.
- `title`
- `type`: `1` is normal single short clip. `10` is usually long/full-game or collection content.
- `duration`
- `game_id`
- `teams`: JSON-like text array of team IDs.
- `players`: JSON-like text array of player IDs.
- `tags`: JSON-like text array of WSC tag IDs.
- `video_file`: original CDN path. Do not rely on it for playback.
- `cover_file`
- `meta_data`: JSON text with event details.
- `game_date`
- `game_clock`: mostly empty at top level; prefer `meta_data` or `kb_pbp.clock`.
- `period`
- `event`: often maps to `kb_pbp.action_number`.
- `new_tags`: comma-separated extended tags.

Preferred clip filter:

```sql
vm.type = 1
AND vm.duration <= 90
AND vm.news_id IS NOT NULL AND vm.news_id <> ''
AND vm.video_file IS NOT NULL AND vm.video_file <> ''
```

### `nba_cms_prod.item_info`

Quality score table.

Join:

```sql
LEFT JOIN nba_cms_prod.item_info ii
  ON CAST(ii.id AS CHAR) = CAST(vm.news_id AS CHAR)
```

Use `ii.star` to prefer higher-quality clips.

## Video Material To PBP Mapping

For `video_material.type = 1` and non-empty `event`, most clips can be mapped:

```text
video_material.game_id = kb_pbp.game_id
video_material.event   = kb_pbp.action_number
```

Use this to get `clock`, `description`, scores, and assist/block/steal fields.

This is high-confidence but not perfect:

- Some block/steal/assist clips are derived events and do not have an independent `action_number`.
- Some `event` values are composite provider IDs rather than numeric action numbers.
- If direct mapping fails, fallback to `game_id + period + meta_data.events[0].gameClock + playerId + actionType`.

## Extended `new_tags`

Common patterns:

- `3001_<foulerId>`: 2+1
- `3002_<foulerId>`: 3+1
- `3003_<runId>_<total_points>_<item_count>_<item_index>_<type>`: player scoring run
- `3004`: deep three over 29.4 feet
- `3005_<teamId>_<runId>_<total_points>_<item_count>_<item_index>_<type>`: team run
- `3006_<period>`: buzzer-beater
- `3007_<period>_<type>`: game winner / game tying shot, `J` for winner, `P` for tie

## Season Date Rule

`SEASON` is like `2025-26`. Spring dates use the season ending year:

- `2025-04-09` belongs to `2024-25`.
- `2026-04-09` belongs to `2025-26`.

Do not combine `SEASON='2025-26'` with `GAME_DATE='2025-04-09'`.

## Known Bad Table Names

Do not use:

- `player_game_stats`
- `nba_player_game_stats`

Use `nba_game_prod.kb_pbs` for player game box scores.

