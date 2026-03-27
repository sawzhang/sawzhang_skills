#!/usr/bin/env python3
"""
Standalone vocab lookup script for the vocab skill.
Auto-downloads gptwords.json on first run (~16MB, one-time).

Usage:
  python3 lookup.py abandon          # exact lookup
  python3 lookup.py --search amb     # prefix search
  python3 lookup.py --random         # random word
"""
import sys
import json
import os
import pickle
import urllib.request

DATA_DIR = os.path.join(os.path.expanduser("~"), ".claude", "vocab_data")
DATA_FILE = os.path.join(DATA_DIR, "gptwords.json")
INDEX_FILE = os.path.join(DATA_DIR, "word_index.pkl")
DATA_URL = "https://raw.githubusercontent.com/Ceelog/DictionaryByGPT4/main/gptwords.json"


def ensure_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        print("首次使用，下载词库 (~16MB)...", flush=True)
        urllib.request.urlretrieve(DATA_URL, DATA_FILE)
        print("词库下载完成。", flush=True)
        if os.path.exists(INDEX_FILE):
            os.remove(INDEX_FILE)


def build_index():
    index = {}
    with open(DATA_FILE, "rb") as f:
        while True:
            offset = f.tell()
            line = f.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                word = entry.get("word", "").lower()
                if word:
                    index[word] = offset
            except json.JSONDecodeError:
                continue
    return index


def get_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "rb") as f:
            return pickle.load(f)
    print("构建索引 (首次约5秒)...", flush=True)
    index = build_index()
    with open(INDEX_FILE, "wb") as f:
        pickle.dump(index, f)
    return index


def lookup(query):
    ensure_data()
    index = get_index()
    key = query.strip().lower()
    offset = index.get(key)
    if offset is None:
        return None
    with open(DATA_FILE, "rb") as f:
        f.seek(offset)
        return json.loads(f.readline())


def search(prefix, limit=6):
    ensure_data()
    index = get_index()
    prefix = prefix.strip().lower()
    return [w for w in index if w.startswith(prefix)][:limit]


def random_word():
    import random
    ensure_data()
    index = get_index()
    word = random.choice(list(index.keys()))
    return lookup(word)


def parse_sections(content):
    sections = {}
    current, buf = None, []
    for line in content.split("\n"):
        if line.startswith("### "):
            if current:
                sections[current] = "\n".join(buf).strip()
            current = line[4:].strip()
            buf = []
        else:
            buf.append(line)
    if current:
        sections[current] = "\n".join(buf).strip()
    return sections


def format_entry(entry, section_names=None):
    if section_names is None:
        section_names = ["分析词义", "列举例句", "记忆辅助", "小故事"]
    word = entry["word"]
    sections = parse_sections(entry.get("content", ""))
    parts = [f"📖 **{word}**\n"]
    for name in section_names:
        text = sections.get(name, "").strip()
        if text:
            parts.append(f"**{name}**\n{text}")
    return "\n\n".join(parts) if len(parts) > 1 else f"**{word}**\n\n{entry.get('content','')}"


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage: lookup.py <word> | --search <prefix> | --random")
        sys.exit(1)

    if args[0] == "--random":
        entry = random_word()
        print(format_entry(entry))
    elif args[0] == "--search" and len(args) > 1:
        results = search(args[1])
        if results:
            print("相关词: " + ", ".join(results))
        else:
            print(f"未找到以 '{args[1]}' 开头的单词")
    else:
        query = " ".join(args)
        entry = lookup(query)
        if entry:
            print(format_entry(entry))
        else:
            suggestions = search(query[:3])
            msg = f"未找到单词: {query}"
            if suggestions:
                msg += "\n相关词: " + ", ".join(suggestions)
            print(msg)
