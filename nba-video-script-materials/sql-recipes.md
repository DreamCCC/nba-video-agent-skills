# SQL Recipes

Use these as starting points. Adapt filters to the user topic. Keep queries read-only and within the SQL proxy restrictions.

## Inspect Available Tables

```sql
SELECT TABLE_SCHEMA, TABLE_NAME
FROM information_schema.TABLES
WHERE TABLE_SCHEMA IN ('nba_game_prod', 'nba_cms_prod')
ORDER BY TABLE_SCHEMA, TABLE_NAME
```

## Inspect Columns

```sql
SELECT COLUMN_NAME, DATA_TYPE
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'nba_game_prod'
  AND TABLE_NAME = 'kb_pbs'
ORDER BY ORDINAL_POSITION
```

## Resolve A Team By Name Or Abbreviation

```sql
SELECT season, team_id, name, abbr, city, conference
FROM nba_game_prod.kb_team
WHERE season = '2025-26'
  AND (name LIKE '%Spurs%' OR abbr = 'SAS' OR city LIKE '%San Antonio%')
LIMIT 20
```

## Resolve A Player

```sql
SELECT PLAYER_ID, PLAYER_NAME, TEAM_ID, TEAM_ABBREVIATION, GAME_DATE
FROM nba_game_prod.kb_pbs
WHERE PLAYER_NAME LIKE '%Wembanyama%'
ORDER BY GAME_DATE DESC
LIMIT 20
```

## Team Game Results

```sql
SELECT SEASON, SEASON_TYPE, GAME_ID, GAME_DATE, TEAM_ID, TEAM_ABBREVIATION,
       MATCHUP, WL, PTS, FG_PCT, FG3M, FG3A, TOV, REB, AST, PLUS_MINUS
FROM nba_game_prod.kb_tbs
WHERE SEASON = '2025-26'
  AND TEAM_ABBREVIATION = 'SAS'
  AND SEASON_TYPE = 'Playoffs'
ORDER BY GAME_DATE
LIMIT 100
```

## Player Game Logs

```sql
SELECT SEASON, SEASON_TYPE, PLAYER_ID, PLAYER_NAME, TEAM_ABBREVIATION,
       GAME_ID, GAME_DATE, MATCHUP, WL, MIN, PTS, REB, AST, STL, BLK,
       TOV, FG_PCT, FG3M, FG3A, PLUS_MINUS
FROM nba_game_prod.kb_pbs
WHERE SEASON = '2025-26'
  AND SEASON_TYPE = 'Playoffs'
  AND PLAYER_NAME LIKE '%Wembanyama%'
ORDER BY GAME_DATE
LIMIT 100
```

## Quarter-Level Team Collapse

```sql
SELECT GAME_ID, GAME_DATE, TEAM_ABBREVIATION, MATCHUP, PERIOD,
       PTS, FG_PCT, FG3M, FG3A, TOV, REB, AST, PLUS_MINUS
FROM nba_game_prod.kb_tbs_period
WHERE SEASON = '2025-26'
  AND SEASON_TYPE = 'Playoffs'
  AND TEAM_ABBREVIATION = 'SAS'
ORDER BY GAME_DATE, CAST(PERIOD AS UNSIGNED)
LIMIT 200
```

## PBP Key Plays For One Game

```sql
SELECT action_number, period, clock, team_tricode, action_type, sub_type,
       person_id, player_name_i, description, score_home, score_away,
       assist_person_id, assist_player_name_i,
       block_person_id, block_player_name_i,
       steal_person_id, steal_player_name_i
FROM nba_game_prod.kb_pbp
WHERE game_id = '0042500403'
  AND period = '4'
ORDER BY CAST(action_number AS UNSIGNED)
LIMIT 200
```

## Find Materials By Player And Action

```sql
SELECT vm.id, vm.news_id, vm.title, vm.duration, vm.game_id, vm.game_date,
       vm.period, vm.event, vm.players, vm.teams, vm.tags, vm.new_tags,
       vm.cover_file, vm.video_file, ii.star
FROM nba_cms_prod.video_material vm
LEFT JOIN nba_cms_prod.item_info ii
  ON CAST(ii.id AS CHAR) = CAST(vm.news_id AS CHAR)
WHERE vm.type = 1
  AND vm.duration <= 90
  AND vm.news_id IS NOT NULL AND vm.news_id <> ''
  AND vm.players LIKE '%"201939"%'
  AND (vm.new_tags LIKE '%3004%' OR vm.title LIKE '%超远三分%')
ORDER BY ii.star DESC, vm.update_at DESC
LIMIT 20
```

## Find Materials For A Specific Game

```sql
SELECT vm.id, vm.news_id, vm.title, vm.duration, vm.game_id, vm.game_date,
       vm.period, vm.event, vm.players, vm.teams, vm.tags, vm.new_tags,
       vm.cover_file, ii.star
FROM nba_cms_prod.video_material vm
LEFT JOIN nba_cms_prod.item_info ii
  ON CAST(ii.id AS CHAR) = CAST(vm.news_id AS CHAR)
WHERE vm.type = 1
  AND vm.duration <= 90
  AND vm.news_id IS NOT NULL AND vm.news_id <> ''
  AND vm.game_id = '0042500403'
ORDER BY ii.star DESC, vm.period, vm.update_at DESC
LIMIT 80
```

## Join Material To PBP For Time And Description

```sql
SELECT vm.id, vm.news_id, vm.title, vm.duration,
       vm.game_id, vm.period, vm.event,
       p.clock, p.description, p.score_home, p.score_away,
       p.person_id, p.player_name_i, p.action_type, p.sub_type,
       p.assist_person_id, p.assist_player_name_i,
       p.block_person_id, p.block_player_name_i,
       p.steal_person_id, p.steal_player_name_i
FROM nba_cms_prod.video_material vm
JOIN nba_game_prod.kb_pbp p
  ON p.game_id = vm.game_id
 AND CAST(p.action_number AS CHAR) = CAST(vm.event AS CHAR)
WHERE vm.type = 1
  AND vm.news_id IS NOT NULL AND vm.news_id <> ''
  AND vm.game_id = '0042500403'
LIMIT 50
```

## Clip Selection Heuristics

Prefer clips in this order:

1. Exact `game_id` + exact player/action intent.
2. Same series/opponent + exact player/action.
3. Same player/team + same action type.
4. Context/highlight clip that visually supports the segment.

Avoid:

- Long clips over 90 seconds.
- `type <> 1` unless explicitly asked for full-game footage.
- Empty `news_id`.
- Materials with only generic titles when better exact clips exist.

