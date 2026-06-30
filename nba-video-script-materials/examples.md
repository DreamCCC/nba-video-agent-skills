# Examples

## Example User Request

```text
帮我生成一个 2 分钟短视频：为什么勇士这场第四节崩盘？给我脚本和每段对应的素材 ID。
```

## Recommended Process

1. Resolve the game from team/date/opponent clues.
2. Query `kb_tbs_period` for fourth-quarter team stats.
3. Query `kb_pbp` for late turnovers, missed shots, clutch scores, and score swings.
4. Query `video_material` for exact game clips, joining `item_info.star`.
5. Return JSON using `output-contract.md`.

## Material Query Skeleton

```sql
SELECT vm.id, vm.news_id, vm.title, vm.duration, vm.game_id, vm.game_date,
       vm.period, vm.event, vm.players, vm.teams, vm.tags, vm.new_tags,
       ii.star
FROM nba_cms_prod.video_material vm
LEFT JOIN nba_cms_prod.item_info ii
  ON CAST(ii.id AS CHAR) = CAST(vm.news_id AS CHAR)
WHERE vm.type = 1
  AND vm.duration <= 90
  AND vm.news_id IS NOT NULL AND vm.news_id <> ''
  AND vm.game_id = '<GAME_ID>'
ORDER BY ii.star DESC, vm.period, vm.update_at DESC
LIMIT 80
```

## Example Partial Output

```json
{
  "success": true,
  "topic": "为什么勇士这场第四节崩盘？",
  "title": "勇士第四节崩盘的三个瞬间",
  "summary": "从失误、篮板和关键回合解释比赛转折。",
  "target_duration_s": 120,
  "language": "zh-CN",
  "segments": [
    {
      "segment_id": "s1",
      "role": "hook",
      "estimated_duration_s": 15,
      "voiceover": "这不是一场突然输掉的比赛，勇士真正崩掉，是从第四节这三个回合开始的。",
      "visual_intent": "第四节关键失误或对手反击得分",
      "evidence_points": [
        {
          "type": "pbp",
          "text": "第四节连续关键回合导致分差被拉开",
          "source": "nba_game_prod.kb_pbp"
        }
      ],
      "material_ids": [123456],
      "news_ids": ["987654321"]
    }
  ],
  "materials": [
    {
      "id": 123456,
      "news_id": "987654321",
      "title": "示例素材标题",
      "duration_s": 11.2,
      "game_id": "0042500403",
      "game_date": "2026-06-10",
      "period": "4",
      "event": "582",
      "players": [],
      "teams": [],
      "star": 5,
      "pbp": {
        "clock": "PT01M38.00S",
        "description": "示例 PBP 描述",
        "score_home": "101",
        "score_away": "99"
      },
      "used_in_segments": ["s1"],
      "selection_reason": "与第四节转折点直接对应"
    }
  ],
  "queries": [
    {
      "purpose": "查询第四节关键 PBP",
      "tables": ["nba_game_prod.kb_pbp"],
      "query_hash": "examplehash",
      "row_count": 50,
      "truncated": false
    }
  ],
  "assumptions": [],
  "warnings": [],
  "quality_checks": {
    "all_stats_have_sources": true,
    "all_segments_have_materials": true,
    "all_materials_have_news_id": true,
    "no_fabricated_ids": true
  }
}
```

