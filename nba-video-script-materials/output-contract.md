# Output Contract

Return one JSON object. Do not wrap it in markdown fences unless the caller explicitly requests markdown.

## Success Shape

```json
{
  "success": true,
  "topic": "用户原始主题",
  "title": "视频标题",
  "summary": "一句话概括视频主线",
  "target_duration_s": 150,
  "language": "zh-CN",
  "segments": [
    {
      "segment_id": "s1",
      "role": "hook",
      "estimated_duration_s": 18,
      "voiceover": "中文解说词。",
      "visual_intent": "这一段需要什么画面",
      "evidence_points": [
        {
          "type": "stat",
          "text": "真实数据依据",
          "source": "nba_game_prod.kb_pbs"
        },
        {
          "type": "web_verification",
          "text": "交易、签约、伤病、阵容或球衣变化等非数据库事实的核验结论",
          "source": "WebSearch"
        }
      ],
      "material_ids": [123456],
      "news_ids": ["987654321"],
      "material_duration_s": 24.6,
      "duration_coverage_ratio": 1.37
    }
  ],
  "materials": [
    {
      "id": 123456,
      "news_id": "987654321",
      "title": "素材标题",
      "duration_s": 12.3,
      "game_id": "0042500403",
      "game_date": "2026-06-10",
      "period": "4",
      "event": "582",
      "players": ["201939"],
      "teams": ["1610612744"],
      "star": 5,
      "pbp": {
        "clock": "PT01M38.00S",
        "description": "PBP 描述",
        "score_home": "101",
        "score_away": "99"
      },
      "used_in_segments": ["s1"],
      "selection_reason": "为什么这条素材适合该段"
    }
  ],
  "queries": [
    {
      "purpose": "查询球员比赛数据",
      "tables": ["nba_game_prod.kb_pbs"],
      "query_hash": "90ca954a9febd2d8",
      "row_count": 12,
      "truncated": false
    },
    {
      "purpose": "WebSearch 核验交易/签约/伤病/阵容/球衣变化",
      "source_type": "websearch",
      "sources": [
        {
          "title": "可靠来源标题",
          "url": "https://example.com/source",
          "claim": "被核验的事实",
          "status": "verified"
        }
      ],
      "row_count": 0,
      "truncated": false
    }
  ],
  "assumptions": [],
  "warnings": [],
  "quality_checks": {
    "all_stats_have_sources": true,
    "all_segments_have_materials": true,
    "all_materials_have_news_id": true,
    "no_fabricated_ids": true,
    "all_segments_have_duration_coverage": true,
    "total_material_duration_s": 180.5,
    "total_target_duration_s": 150,
    "total_duration_coverage_ratio": 1.2
  }
}
```

## Failure Shape

Use this when the task cannot be completed with available data.

```json
{
  "success": false,
  "topic": "用户原始主题",
  "blocking_reason": "缺少必要信息或查询失败的原因",
  "partial_findings": [],
  "suggested_next_questions": ["需要用户补充的问题"],
  "queries": [],
  "warnings": []
}
```

## Field Rules

- `segments[].voiceover` must be ready for TTS and should not contain stage directions.
- `segments[].material_ids` must be `video_material.id` values returned by SQL.
- `segments[].news_ids` must be copied from the selected materials. Do not use `id` as `news_id`.
- `segments[].material_duration_s` is the sum of `duration_s` for selected materials in that segment.
- `segments[].duration_coverage_ratio` is `material_duration_s / estimated_duration_s`.
- `materials[].id` and `materials[].news_id` are both required for playable clips.
- `materials[].pbp` is optional, but include it when `event` maps to `kb_pbp.action_number`.
- `queries[].query_hash` should come from the SQL proxy response when available.
- `queries[]` must include a `source_type: "websearch"` entry when WebSearch was required for trades, signings, injuries, jersey changes, roster moves, or non-database facts.
- WebSearch entries should include source title, URL, verified claim, and status, but not long copied excerpts.
- `warnings` should include broad fallback matches, missing PBP mappings, weak evidence, or duration coverage below 115%.
- `warnings` should include conflicting or unverified WebSearch findings and same-surname ambiguity that required fallback material.
- Successful outputs should target `duration_coverage_ratio >= 1.15` for every segment and total coverage. Absolute minimum is `1.0`; below `1.0` is not acceptable for `success=true`.

## Script Guidelines

- Keep the tone suitable for an NBA short-video narrator.
- Use concrete scenes, data, and turning points.
- Avoid bloated intros. The first segment should hook immediately.
- Each 15 seconds of narration is roughly 65-85 Chinese characters.
- One segment should normally map to one visual idea and one main claim.

