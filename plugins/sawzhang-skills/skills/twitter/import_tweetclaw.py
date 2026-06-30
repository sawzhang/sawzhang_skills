#!/usr/bin/env python3
"""Summarize reviewed TweetClaw exports for the Twitter skill."""

from __future__ import annotations

import argparse
import json
import re
from collections import OrderedDict
from pathlib import Path
from typing import Any


ROWS_KEYS = ("items", "tweets", "results", "data", "rows")
HANDLE_KEYS = (
    "authorUsername",
    "author_username",
    "screen_name",
    "username",
    "userName",
    "handle",
)
TEXT_KEYS = ("text", "full_text", "content", "body")
URL_KEYS = ("url", "tweetUrl", "tweet_url")


def load_rows(path: Path) -> list[Any]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        for key in ROWS_KEYS:
            rows = parsed.get(key)
            if isinstance(rows, list):
                return rows
        return [parsed]
    return []


def normalize_handle(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    match = re.search(r"(?:x|twitter)\.com/([A-Za-z0-9_]{1,15})", value)
    if match:
        value = match.group(1)
    value = value.removeprefix("@")
    if re.fullmatch(r"[A-Za-z0-9_]{1,15}", value):
        return value
    return None


def first_text(row: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def extract_handle(row: Any) -> str | None:
    if not isinstance(row, dict):
        return None
    for key in HANDLE_KEYS:
        handle = normalize_handle(row.get(key))
        if handle:
            return handle
    for key in ("author", "user", "profile"):
        nested = row.get(key)
        if isinstance(nested, dict):
            handle = extract_handle(nested)
            if handle:
                return handle
    for key in URL_KEYS:
        handle = normalize_handle(row.get(key))
        if handle:
            return handle
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a markdown source summary from TweetClaw exports.",
    )
    parser.add_argument("export", type=Path, help="TweetClaw JSON or JSONL export")
    args = parser.parse_args()

    grouped: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for row in load_rows(args.export):
        if not isinstance(row, dict):
            continue
        handle = extract_handle(row)
        if not handle:
            continue
        text = first_text(row, TEXT_KEYS)
        url = first_text(row, URL_KEYS)
        grouped.setdefault(handle, []).append({"text": text, "url": url})

    print("# TweetClaw Source Summary")
    print()
    for handle, rows in grouped.items():
        print(f"## @{handle}")
        for item in rows[:5]:
            text = item["text"][:180] or "(no text)"
            suffix = f" - {item['url']}" if item["url"] else ""
            print(f"- {text}{suffix}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
