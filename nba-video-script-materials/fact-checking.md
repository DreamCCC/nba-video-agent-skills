# Fact Checking And Entity Disambiguation

Use this file whenever the user request contains facts that may not exist in the NBA database or may be time-sensitive.

## Mandatory WebSearch Triggers

Run WebSearch before writing the script when the topic involves:

- Trades
- Signings
- Waivers, buyouts, option decisions, extensions
- Injuries, return timelines, availability
- Jersey changes, new team uniforms, number changes
- Roster moves, depth chart changes, team rebuilds
- Draft-night or free-agency news
- Any claim that is not covered by `nba_game_prod` or `nba_cms_prod`

Rule of thumb: if the NBA SQL database cannot be expected to contain it, verify it with WebSearch.

## Fact Ledger

Create a private fact ledger before writing the final JSON. Do not include long web excerpts, but use the verified facts in `assumptions`, `warnings`, `queries`, or `evidence_points`.

For each claim, track:

- `claim`: the user's claim or the fact needed for the script.
- `status`: `verified`, `conflicting`, or `unverified`.
- `source`: reliable URL/title from WebSearch.
- `player_full_name`: full player name, never surname only.
- `from_team` / `to_team`: for trades or signings.
- `transaction_details`: picks, players, exceptions, salary notes when available.
- `confidence`: high / medium / low.

If a claim is conflicting or unverified, do not present it as fact. Either omit it, downgrade the wording, or put the issue in `warnings`.

## Entity Disambiguation

Never use surname-only matching for players, especially names like:

- `Bridges`
- `Ball`
- `Green`
- `Williams`
- `Johnson`
- `Brown`
- `Smith`
- `Murray`

Resolve the exact player before querying materials:

1. Use WebSearch for current transaction context.
2. Identify full name, current/old team, and role.
3. Resolve `PLAYER_ID` from `nba_game_prod.kb_pbs`, `kb_player`, or material `players`.
4. Query video materials by exact player ID whenever possible.
5. Use title keyword matching only as a secondary filter.

## Material Rules For Transactions

- If the target is a player changing teams, old-team footage is acceptable only when labeled as old-team/context footage in `selection_reason`.
- Do not use another same-surname player as a fallback.
- If no target-player footage is available, use team/context/B-roll and explain in `warnings`.
- For "球衣变化" topics, make the script explicitly mention old team to new team, and avoid implying that old footage already shows the new jersey.

