#!/usr/bin/env python3
"""Create a temporary Cursor Cloud Agent, run one prompt, then delete it.

This mirrors ask_nba_with_cursor_agent's lifecycle:
POST /v1/agents -> stream run -> DELETE /v1/agents/{agent_id}
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


TERMINAL_STATUSES = {"FINISHED", "FAILED", "CANCELLED", "EXPIRED"}


@dataclass
class SseEvent:
    event: str
    data: dict[str, Any]
    event_id: str | None = None


class CursorApiError(RuntimeError):
    pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="https://github.com/DreamCCC/nba-video-agent-skills.git")
    parser.add_argument("--ref", default="main")
    parser.add_argument("--model", default=os.environ.get("CURSOR_MODEL_ID", "composer-2.5"))
    parser.add_argument("--api-base-url", default=os.environ.get("CURSOR_API_BASE_URL", "https://api.cursor.com"))
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("CURSOR_RUN_TIMEOUT_SECONDS", "180")))
    parser.add_argument("--prompt", default=default_prompt())
    parser.add_argument("--db-smoke-test", action="store_true")
    parser.add_argument("--with-db-env", action="store_true")
    parser.add_argument("--db-api-key-env", default="DB_QUERY_API_KEY")
    parser.add_argument("--no-header", action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not api_key:
        print("ERROR: CURSOR_API_KEY is not set.", file=sys.stderr)
        return 1

    client = CursorRestClient(args.api_base_url.rstrip("/"), api_key, args.timeout)
    env_vars: dict[str, str] = {}
    prompt = args.prompt
    if args.db_smoke_test:
        prompt = db_smoke_prompt()
        if args.with_db_env:
            db_api_key = os.environ.get(args.db_api_key_env, "").strip()
            if not db_api_key:
                print(f"ERROR: {args.db_api_key_env} is not set.", file=sys.stderr)
                return 1
            env_vars["DB_QUERY_API_KEY"] = db_api_key

    agent_id: str | None = None
    run_id: str | None = None

    try:
        created = client.create_agent(
            prompt=prompt,
            repo_url=args.repo,
            starting_ref=args.ref,
            model=args.model,
            env_vars=env_vars,
            include_header=not args.no_header,
        )
        agent_id = created["agent_id"]
        run_id = created["run_id"]
        print(f"created agent={agent_id} run={run_id}")

        final_status = "UNKNOWN"
        for event in client.stream_run(agent_id, run_id):
            if event.event == "assistant":
                text = event.data.get("text")
                if isinstance(text, str):
                    print(text, end="", flush=True)
            elif event.event in {"status", "result"}:
                status = event.data.get("status")
                if isinstance(status, str):
                    final_status = status
            elif event.event == "error":
                raise CursorApiError(str(event.data.get("message") or "Cursor stream returned an error."))

        print()
        print(f"final_status={final_status}")
        return 0 if final_status in {"FINISHED", "finished"} else 2
    finally:
        if agent_id:
            try:
                client.delete_agent(agent_id)
                print(f"deleted agent={agent_id}")
            except CursorApiError:
                client.archive_agent(agent_id)
                print(f"archived agent={agent_id}")


def default_prompt() -> str:
    return (
        "这是一次 nba-video-agent-skills 仓库 smoke test。"
        "请只读检查仓库内的 nba-video-script-materials skill："
        "1. 说明这个 skill 的用途；"
        "2. 列出生成脚本和素材 ID 时必须读取的引用文件；"
        "3. 返回一个很小的 JSON，字段包含 success、skill、required_refs、notes。"
        "不要修改文件，不要执行 git 操作，不要创建 PR，不要调用数据库或外部业务接口。"
    )


def db_smoke_prompt() -> str:
    return (
        "这是一次 NBA SQL Proxy 数据库访问 smoke test。"
        "请读取 `nba-video-script-materials/db-query-api.md`，然后在云端 shell 中使用环境变量 `DB_QUERY_API_KEY` "
        "调用 `https://8.152.222.232/api/db/query`。"
        "执行只读 SQL：`SELECT 1 AS ok`，limit=1。"
        "当前服务是 IP 自签 HTTPS 证书，调用时可以只针对这个请求关闭证书校验。"
        "不要打印、回显或保存 `DB_QUERY_API_KEY`，不要把 token 写入文件或日志。"
        "最后只返回一个 JSON，字段包含 success、health_ok、db_query_ok、row、notes。"
    )


class CursorRestClient:
    def __init__(self, base_url: str, api_key: str, timeout: float) -> None:
        self.base_url = base_url
        self.timeout = timeout
        token = base64.b64encode(f"{api_key}:".encode("utf-8")).decode("ascii")
        self.headers = {"Authorization": f"Basic {token}"}

    def create_agent(
        self,
        *,
        prompt: str,
        repo_url: str,
        starting_ref: str,
        model: str,
        env_vars: dict[str, str],
        include_header: bool,
    ) -> dict[str, str]:
        prompt_text = fresh_prompt_header() + "\n\n" + prompt if include_header else prompt
        payload: dict[str, Any] = {
            "prompt": {"text": prompt_text},
            "repos": [{"url": repo_url, "startingRef": starting_ref}],
            "autoCreatePR": False,
        }
        if model:
            payload["model"] = {"id": model}
        if env_vars:
            payload["envVars"] = env_vars

        body = self._request_json("POST", "/v1/agents", payload)
        agent = body.get("agent") if isinstance(body, dict) else None
        run = body.get("run") if isinstance(body, dict) else None
        agent_id = agent.get("id") if isinstance(agent, dict) else None
        run_id = run.get("id") if isinstance(run, dict) else None
        if not isinstance(agent_id, str) or not isinstance(run_id, str):
            raise CursorApiError(f"Unexpected create response: {body}")
        return {"agent_id": agent_id, "run_id": run_id}

    def stream_run(self, agent_id: str, run_id: str):
        req = urllib.request.Request(
            f"{self.base_url}/v1/agents/{agent_id}/runs/{run_id}/stream",
            headers={**self.headers, "Accept": "text/event-stream"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                buffer: list[str] = []
                for raw in response:
                    line = raw.decode("utf-8", errors="replace").rstrip("\n").rstrip("\r")
                    if line == "":
                        event = parse_sse_event(buffer)
                        buffer = []
                        if event:
                            yield event
                        continue
                    buffer.append(line)
                event = parse_sse_event(buffer)
                if event:
                    yield event
        except urllib.error.HTTPError as exc:
            raise CursorApiError(read_http_error(exc)) from exc
        except urllib.error.URLError as exc:
            raise CursorApiError(f"Cursor API network error: {exc}") from exc

    def delete_agent(self, agent_id: str) -> None:
        self._request_no_body("DELETE", f"/v1/agents/{agent_id}")

    def archive_agent(self, agent_id: str) -> None:
        self._request_no_body("POST", f"/v1/agents/{agent_id}/archive")

    def _request_json(self, method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers={**self.headers, "Content-Type": "application/json"},
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise CursorApiError(read_http_error(exc)) from exc
        except urllib.error.URLError as exc:
            raise CursorApiError(f"Cursor API network error: {exc}") from exc

    def _request_no_body(self, method: str, path: str) -> None:
        req = urllib.request.Request(f"{self.base_url}{path}", headers=self.headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout):
                return
        except urllib.error.HTTPError as exc:
            raise CursorApiError(read_http_error(exc)) from exc
        except urllib.error.URLError as exc:
            raise CursorApiError(f"Cursor API network error: {exc}") from exc


def fresh_prompt_header() -> str:
    return (
        "本次运行是 NBA Video Agent Skills 的一次独立 smoke test。"
        "请不要依赖任何旧 agent 对话上下文；只依据本次 prompt 和仓库上下文回答。"
        "本次调用只允许只读分析和按要求返回文本；不要修改文件，不要创建、编辑或删除代码，"
        "不要执行 git commit、branch、push，不要创建 PR，也不要声称已经保存文件或提交推送。"
    )


def parse_sse_event(lines: list[str]) -> SseEvent | None:
    if not lines:
        return None

    event_type = "message"
    event_id: str | None = None
    data_lines: list[str] = []

    for line in lines:
        if line.startswith(":"):
            continue
        field, _, value = line.partition(":")
        value = value[1:] if value.startswith(" ") else value
        if field == "event":
            event_type = value
        elif field == "id":
            event_id = value
        elif field == "data":
            data_lines.append(value)

    data_text = "\n".join(data_lines)
    if not data_text:
        data: dict[str, Any] = {}
    else:
        try:
            parsed = json.loads(data_text)
            data = parsed if isinstance(parsed, dict) else {"value": parsed}
        except json.JSONDecodeError:
            data = {"text": data_text}

    return SseEvent(event=event_type, data=data, event_id=event_id)


def read_http_error(exc: urllib.error.HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8", errors="replace")
    except Exception:
        body = ""
    return f"Cursor API request failed: HTTP {exc.code} {body}"


if __name__ == "__main__":
    raise SystemExit(main())

