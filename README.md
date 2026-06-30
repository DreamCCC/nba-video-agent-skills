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

