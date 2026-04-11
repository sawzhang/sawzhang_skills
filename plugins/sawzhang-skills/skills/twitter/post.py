#!/usr/bin/env python3
"""Twitter/X post and thread via X API v2 with OAuth 1.0a.

Usage:
    # Single tweet
    python3 post.py "Hello world"

    # Reply to a tweet
    python3 post.py "reply text" --reply-to 2043010543112290815

    # Thread from JSON file
    python3 post.py --thread thread.json

    # Thread from stdin
    echo '["tweet 1","tweet 2","tweet 3"]' | python3 post.py --thread -

Environment variables (required):
    X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET

Exit codes:
    0 = all tweets posted successfully
    1 = partial failure (some posted, check output)
    2 = total failure (nothing posted)
"""

import argparse
import json
import os
import sys
import time

try:
    from requests_oauthlib import OAuth1Session
except ImportError:
    print("ERROR: requests-oauthlib not installed. Run: pip3 install --break-system-packages requests-oauthlib", file=sys.stderr)
    sys.exit(2)

ENDPOINT = "https://api.x.com/2/tweets"

# Spam detection avoidance: X API rejects tweets that look automated.
# These patterns trigger 403 "not permitted":
#   - Duplicate content (exact same text as a recent tweet)
#   - Rapid-fire posting without delays
#   - Certain character combinations in long tweets
THREAD_DELAY_SECONDS = 4


def create_session() -> OAuth1Session:
    """Create OAuth1 session from environment variables."""
    required_variables = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET"]
    missing = [variable for variable in required_variables if not os.environ.get(variable)]
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}", file=sys.stderr)
        print("Set them in ~/.zshrc or pass inline:", file=sys.stderr)
        print("  export X_API_KEY=... X_API_SECRET=... X_ACCESS_TOKEN=... X_ACCESS_SECRET=...", file=sys.stderr)
        sys.exit(2)

    return OAuth1Session(
        os.environ["X_API_KEY"],
        os.environ["X_API_SECRET"],
        os.environ["X_ACCESS_TOKEN"],
        os.environ["X_ACCESS_SECRET"],
    )


def post_single_tweet(
    session: OAuth1Session,
    text: str,
    reply_to_tweet_id: str | None = None,
) -> dict:
    """Post a single tweet. Returns {"id": ..., "text": ...} on success."""
    payload: dict = {"text": text}
    if reply_to_tweet_id:
        payload["reply"] = {"in_reply_to_tweet_id": reply_to_tweet_id}

    response = session.post(ENDPOINT, json=payload)

    if response.status_code in (200, 201):
        return response.json()["data"]

    error_detail = ""
    try:
        error_detail = response.json().get("detail", response.text[:200])
    except Exception:
        error_detail = response.text[:200]

    return {
        "error": True,
        "status_code": response.status_code,
        "detail": error_detail,
    }


def post_thread(session: OAuth1Session, tweet_texts: list[str]) -> list[dict]:
    """Post a thread (list of tweets as sequential replies).

    Returns list of results. On reply failure, falls back to standalone tweets.
    """
    results = []
    previous_tweet_id = None

    for index, text in enumerate(tweet_texts):
        # Try as reply first (builds thread), fall back to standalone
        result = post_single_tweet(session, text, reply_to_tweet_id=previous_tweet_id)

        if result.get("error") and previous_tweet_id:
            # Reply failed (X API pay-per-use may restrict replies)
            # Fall back to standalone tweet
            print(f"  [{index + 1}/{len(tweet_texts)}] Reply failed ({result['detail']}), posting standalone...", file=sys.stderr)
            result = post_single_tweet(session, text, reply_to_tweet_id=None)

        if result.get("error"):
            print(f"  [{index + 1}/{len(tweet_texts)}] FAILED: {result['detail']}", file=sys.stderr)
            results.append({"index": index + 1, "status": "error", "detail": result["detail"]})
            # Don't break — try remaining tweets
        else:
            tweet_id = result["id"]
            previous_tweet_id = tweet_id
            results.append({"index": index + 1, "status": "ok", "tweet_id": tweet_id})
            print(f"  [{index + 1}/{len(tweet_texts)}] OK: {tweet_id}", file=sys.stderr)

        if index < len(tweet_texts) - 1:
            time.sleep(THREAD_DELAY_SECONDS)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Post tweets via X API v2")
    parser.add_argument("text", nargs="?", help="Tweet text (for single tweet)")
    parser.add_argument("--reply-to", help="Tweet ID to reply to")
    parser.add_argument("--thread", help="JSON file with array of tweet texts (use - for stdin)")
    parsed_arguments = parser.parse_args()

    session = create_session()

    if parsed_arguments.thread:
        # Thread mode
        if parsed_arguments.thread == "-":
            tweet_texts = json.load(sys.stdin)
        else:
            with open(parsed_arguments.thread) as thread_file:
                tweet_texts = json.load(thread_file)

        if not isinstance(tweet_texts, list) or not tweet_texts:
            print("ERROR: Thread file must contain a non-empty JSON array of strings", file=sys.stderr)
            sys.exit(2)

        results = post_thread(session, tweet_texts)
        successful_count = sum(1 for result in results if result["status"] == "ok")
        output = {
            "total": len(tweet_texts),
            "posted": successful_count,
            "results": results,
        }
        if results and results[0].get("tweet_id"):
            output["thread_url"] = f"https://x.com/i/status/{results[0]['tweet_id']}"
        print(json.dumps(output, indent=2))
        sys.exit(0 if successful_count == len(tweet_texts) else 1)

    elif parsed_arguments.text:
        # Single tweet mode
        result = post_single_tweet(session, parsed_arguments.text, parsed_arguments.reply_to)
        if result.get("error"):
            print(json.dumps(result, indent=2))
            sys.exit(2)
        else:
            result["url"] = f"https://x.com/i/status/{result['id']}"
            print(json.dumps(result, indent=2))

    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
