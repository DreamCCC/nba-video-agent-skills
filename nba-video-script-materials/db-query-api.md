# NBA SQL Proxy API

Use this API for all database reads.

## Endpoint

```text
POST https://8.152.222.232/api/db/query
```

Health check:

```text
GET https://8.152.222.232/health
```

The service currently uses a self-signed certificate on an IP address. If the runtime has not trusted the cert, disable certificate verification only for this endpoint.

## Authentication

Send a Bearer token from the runtime environment:

```http
Authorization: Bearer <DB_QUERY_API_KEY>
Content-Type: application/json
```

Never print, log, commit, or expose `DB_QUERY_API_KEY`.

## Request Body

```json
{
  "sql": "SELECT 1 AS ok",
  "limit": 1
}
```

- `sql`: required. One read-only SQL statement.
- `limit`: optional. Default 200, maximum 1000.

## SQL Restrictions

Allowed:

- One `SELECT` statement.
- One `WITH ... SELECT` query.

Forbidden:

- Semicolons and multiple statements.
- SQL comments: `--`, `/* */`, `#`.
- Write/admin keywords: `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT`, `CALL`, `EXEC`, `REPLACE`.
- SQL longer than 10000 characters.

## Successful Response

```json
{
  "rows": [{"OK": 1}],
  "row_count": 1,
  "truncated": false,
  "query_hash": "90ca954a9febd2d8",
  "elapsed_ms": 37
}
```

Use `rows` as the result list. Preserve `query_hash` in the final output when it helps trace evidence.

## Python Example

```python
import os
import requests

url = "https://8.152.222.232/api/db/query"
token = os.environ["DB_QUERY_API_KEY"]

response = requests.post(
    url,
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    },
    json={
        "sql": "SELECT 1 AS ok",
        "limit": 1,
    },
    verify=False,
    timeout=100,
)
response.raise_for_status()
data = response.json()
```

## Node.js Example

```javascript
const response = await fetch("https://8.152.222.232/api/db/query", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${process.env.DB_QUERY_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    sql: "SELECT 1 AS ok",
    limit: 1,
  }),
});

if (!response.ok) {
  throw new Error(`DB query failed: ${response.status} ${await response.text()}`);
}

const data = await response.json();
```

