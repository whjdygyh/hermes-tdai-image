#!/usr/bin/env python3
"""
quick_session_scan.py — One-shot session scanner for Lover cron

Purpose: Replace the 7+ tool-call manual session-scanning dance with a single
script execution. Answers: "Has the user messaged Lover since timestamp X?"

Usage:
    python3 quick_session_scan.py --since 2026-05-16T10:00:00+08:00 \
        --sessions-dir /home/admin1/.hermes/sessions \
        [--output-json]

Format Support (dual-format scan):
  * *.jsonl — line-delimited JSON with role/session_meta rows (Hermes new format)
  * *.json  — single-JSON object with system_prompt + messages array (node format)
  Script scans BOTH formats. .json files have authoritative system_prompt field
  which enables direct agent classification without heuristic inference.

Output (JSON):
    {
        "found_lover_messages": false,
        "latest_lover_user_time": null,
        "non_lover_sessions": ["session_A.jsonl", "session_B.jsonl"],
        "lover_candidate_sessions": [],
        "error": null
    }

Agent-Ownership Heuristic
--------------------------
A session is owned by a specific Hermes agent personality. We determine
ownership by reading the first 3 user+assistant message pairs.

Belongs to Lover ✅:
  - First user message: "老公", "宝贝", "你在干吗", "想你", "在吗", "想你了",
    "宝贝在吗", "睡了没", or any flirtatious/sexy content
  - Assistant replies in Chinese w/ emoji, casual tone, sometimes sexual
  - Tool calls: feishu send_message, lover_reply_hook, etc.

Belongs to other agent ❌:
  - First user message: "电脑无线", "起卦", "计算", "帮我查", numbers,
    technical questions
  - Assistant replies: technical explanations, JSON output, tool results
  - Tool calls: chinese-metaphysics, ba-zi, wu-xing, etc.

The open_id (ou_37bc57c4f8aca21f5d4ea4973bd0d386) appears in ALL sessions
because Hermes shares the Feishu identity. Presence in metadata ≠ Lover.
"""

import json
import argparse
import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Script-global constants ────────────────────────────────────────────────

# Keywords that strongly indicate a message is for Lover
LOVER_INDICATORS = [
    "老公", "宝贝", "亲爱的", "想你了", "想你", "在干吗", "在干嘛",
    "睡了没", "在吗", "宝贝在吗", "睡了", "好想你", "miss you",
    "爱你", "抱抱", "亲亲", "😏", "😘", "❤️", "😭", "🥺",
]

# Keywords that indicate a message is NOT for Lover (other Hermes agents)
NON_LOVER_INDICATORS = [
    "电脑无线", "起卦", "八字", "五行", "奇门", "六爻", "大运",
    "流年", "紫微", "风水", "命主", "周易", "纳音",
    "chinese-metaphysics", "ba-zi", "wu-xing",
]


def parse_timestamp(ts_str: str) -> datetime | None:
    """Parse ISO 8601 timestamp or epoch ms. Returns timezone-aware UTC on success."""
    if not ts_str or ts_str == "?" or ts_str == "None":
        return None
    try:
        # Try ISO format
        if "T" in str(ts_str):
            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        # Try epoch seconds
        ts = float(ts_str)
        if ts > 1e10:  # epoch ms
            ts /= 1000
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    except (ValueError, TypeError):
        return None


def classify_session(jsonl_path: str) -> dict:
    """
    Read first 3-4 messages of a JSONL session file and classify ownership.

    Returns:
        {"agent": "lover"|"non_lover"|"unknown",
         "confidence": "high"|"medium"|"low",
         "reason": "...",
         "latest_user_time": "ISO8601 or null",
         "latest_user_content": "first 80 chars or null"}
    """
    result = {
        "agent": "unknown",
        "confidence": "low",
        "reason": "",
        "latest_user_time": None,
        "latest_user_content": None,
    }

    try:
        messages = []
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    if isinstance(msg, dict) and "role" in msg:
                        messages.append(msg)
                except json.JSONDecodeError:
                    continue
                if len(messages) >= 6:  # 3 user + 3 assistant
                    break
    except (FileNotFoundError, PermissionError) as e:
        result["reason"] = f"File error: {e}"
        return result

    if not messages:
        result["reason"] = "Empty messages list"
        return result

    # Container for all tool names, populated from session_meta first
    # then from tool_call messages during content-scoring phase
    all_tool_names = []

    # ── Phase 0: Session_meta tools check (most authoritative for .jsonl) ──
    # Must be done BEFORE content scoring. Agent tools are the ground truth:
    #   browser_*     → Hot agent (私人助理)
    #   chinese_metaphysics / ba-zi / wu-xing  → 国学术数 agent
    #   feishu / send_message / lover_reply  → Lover agent
    #   [] or generic  → fall through to content scoring
    for msg in messages:
        if msg.get("role") == "session_meta":
            tools = msg.get("tools", [])
            if isinstance(tools, list):
                for tool in tools:
                    name = ""
                    if isinstance(tool, dict):
                        if "function" in tool:
                            name = tool["function"].get("name", "")
                        elif "name" in tool:
                            name = tool["name"]
                    if name:
                        all_tool_names.append(name)
            break  # session_meta is always the first line

    # Immediate classification based on tool list
    browser_tools = [t for t in all_tool_names if t.startswith("browser_")]
    chinese_tools = [t for t in all_tool_names
                     if any(kw in t.lower() for kw in
                            ["chinese", "metaphysics", "ba-zi",
                             "wu-xing", "divination", "gua"])]

    if browser_tools:
        result["agent"] = "non_lover"
        result["confidence"] = "high"
        result["reason"] = (f"session_meta browser_tools ({len(browser_tools)}): "
                            f"{browser_tools[:3]} → Hot agent")
        # Still extract latest user time for cross-ref
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = (msg.get("content") or "").strip()
                if content:
                    result["latest_user_content"] = content[:80]
                ts = parse_timestamp(msg.get("timestamp"))
                if ts:
                    result["latest_user_time"] = ts.isoformat()
                break
        return result

    if chinese_tools:
        result["agent"] = "non_lover"
        result["confidence"] = "high"
        result["reason"] = (f"session_meta chinese_tools ({len(chinese_tools)}): "
                            f"{chinese_tools[:3]} → 国学术数 agent")
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = (msg.get("content") or "").strip()
                if content:
                    result["latest_user_content"] = content[:80]
                ts = parse_timestamp(msg.get("timestamp"))
                if ts:
                    result["latest_user_time"] = ts.isoformat()
                break
        return result

    # Find the latest user message timestamp
    latest_user_ts = None
    latest_user_content = None
    for msg in reversed(messages):
        if msg.get("role") == "user":
            content = (msg.get("content") or "").strip()
            ts = parse_timestamp(msg.get("timestamp"))
            if content:
                latest_user_content = content[:80]
            if ts:
                latest_user_ts = ts.isoformat() if latest_user_ts is None else max(
                    latest_user_ts, ts.isoformat()
                )
                latest_user_ts = ts.isoformat()
            break  # we want the last user message
    result["latest_user_time"] = latest_user_ts
    result["latest_user_content"] = latest_user_content

    # Look through first few user messages for indicators
    first_user_msg = ""
    first_assistant_msg = ""

    for msg in messages:
        role = msg.get("role", "")
        content = (msg.get("content") or "").strip()

        if role == "user" and not first_user_msg:
            first_user_msg = content
        elif role == "assistant" and not first_assistant_msg:
            first_assistant_msg = content
        elif role == "tool":
            try:
                data = json.loads(content) if content else {}
                if isinstance(data, dict) and "name" in data:
                    all_tool_names.append(data["name"])
            except (json.JSONDecodeError, TypeError):
                pass

    # Scoring
    lover_score = 0
    non_lover_score = 0

    # 1. Check first user message
    ulower = first_user_msg.lower()
    for kw in LOVER_INDICATORS:
        if kw in first_user_msg:
            lover_score += 2
            break
    for kw in NON_LOVER_INDICATORS:
        if kw in first_user_msg:
            non_lover_score += 2
            break

    # 2. Check first assistant message
    alower = first_assistant_msg.lower()
    # Lover indicators: emoji, casual Chinese, flirtation
    if any(c in first_assistant_msg for c in ["😏", "😘", "❤️", "😭", "🥺", "😂"]):
        lover_score += 1
    # Non-lover indicators: technical explanations
    if any(
        kw in alower
        for kw in [
            "下面", "这个问题", "解释", "五行", "奇门", "八字", "大运",
            "下面给你", "好问题", "决策逻辑",
        ]
    ):
        non_lover_score += 1

    # 3. Check tool calls
    for tname in all_tool_names:
        if "feishu" in tname.lower() or "send_message" in tname.lower() or "lover" in tname.lower():
            lover_score += 2
        if "chinese" in tname.lower() or "metaphysics" in tname.lower() or "ba-zi" in tname.lower():
            non_lover_score += 2

    # Decision
    if lover_score > non_lover_score:
        result["agent"] = "lover"
        result["confidence"] = "high" if (lover_score - non_lover_score) >= 2 else "medium"
        result["reason"] = f"lover_score={lover_score} > non_lover={non_lover_score}, first_user='{first_user_msg[:50]}'"
    elif non_lover_score > lover_score:
        result["agent"] = "non_lover"
        result["confidence"] = "high" if (non_lover_score - lover_score) >= 2 else "medium"
        result["reason"] = f"non_lover_score={non_lover_score} > lover={lover_score}, first_user='{first_user_msg[:50]}'"
    else:
        # Tiebreaker: check message count — if more than 5 user messages and
        # conversation is technical, it's likely non-Lover
        user_count = sum(1 for m in messages if m.get("role") == "user")
        if user_count >= 4 and not any(
            kw in first_user_msg for kw in LOVER_INDICATORS
        ):
            result["agent"] = "non_lover"
            result["confidence"] = "medium"
            result["reason"] = (
                f"tiebreaker: {user_count} user msgs, no lover indicators"
            )
        else:
            result["agent"] = "unknown"
            result["confidence"] = "low"
            result["reason"] = (
                f"tie (lover={lover_score}, non_lover={non_lover_score}), "
                f"first_user='{first_user_msg[:50]}'"
            )

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Quick session scanner — find Lover user messages since a timestamp"
    )
    parser.add_argument(
        "--since",
        help="ISO 8601 timestamp. Only consider user messages after this time. If omitted, uses --hours (default 24h).",
    )
    parser.add_argument(
        "--sessions-dir",
        required=True,
        help="Path to Hermes system sessions directory (/home/admin1/.hermes/sessions/)",
    )
    parser.add_argument(
        "--output-json",
        action="store_true",
        help="Output results as JSON (machine-readable)",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=None,
        help="How far back to scan (default: 24h). Overrides --since if both provided.",
    )

    args = parser.parse_args()

    # Parse reference time: --hours takes priority if explicitly set, else use --since, else default 24h
    if args.hours is not None:
        since_dt = datetime.now(timezone.utc) - timedelta(hours=args.hours)
    elif args.since:
        since_dt = parse_timestamp(args.since)
        if since_dt is None:
            print(
                json.dumps(
                    {
                        "error": f"Cannot parse --since='{args.since}'",
                        "found_lover_messages": False,
                        "latest_lover_user_time": None,
                        "non_lover_sessions": [],
                        "lover_candidate_sessions": [],
                    }
                )
            )
            sys.exit(1)
    else:
        since_dt = datetime.now(timezone.utc) - timedelta(hours=24)

    sessions_dir = Path(args.sessions_dir)
    if not sessions_dir.is_dir():
        print(
            json.dumps(
                {
                    "error": f"Directory not found: {sessions_dir}",
                    "found_lover_messages": False,
                    "latest_lover_user_time": None,
                    "non_lover_sessions": [],
                    "lover_candidate_sessions": [],
                }
            )
        )
        sys.exit(1)

    # Scan for JSONL files (JSONL has raw messages with timestamps)
    # Prefer JSONL over JSON (JSON summaries have unreliable metadata)
    jsonl_files = sorted(
        sessions_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True
    )

    lover_user_found = False
    latest_lover_user_time = None
    non_lover_sessions = []
    lover_candidate_sessions = []
    errors = []

    for fpath in jsonl_files:
        try:
            classification = classify_session(str(fpath))
            fname = fpath.name

            if classification["agent"] == "non_lover":
                non_lover_sessions.append(fname)
            elif classification["agent"] == "lover":
                lover_candidate_sessions.append(
                    {
                        "file": fname,
                        "confidence": classification["confidence"],
                        "latest_user_time": classification["latest_user_time"],
                        "latest_user_content": classification["latest_user_content"],
                        "reason": classification["reason"],
                    }
                )
                # Check if there's a user message since our reference time
                if classification["latest_user_time"]:
                    msg_ts = parse_timestamp(classification["latest_user_time"])
                    if msg_ts and msg_ts >= since_dt:
                        lover_user_found = True
                        if latest_lover_user_time is None or (
                            classification["latest_user_time"]
                            > latest_lover_user_time
                        ):
                            latest_lover_user_time = classification[
                                "latest_user_time"
                            ]
            # "unknown" — skip, falls through
        except Exception as e:
            errors.append(f"{fpath.name}: {e}")

    # ── Pass 2: Scan .json session files (single-JSON format w/ system_prompt) ──
    json_files = sorted(
        sessions_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    for fpath in json_files:
        try:
            with open(str(fpath), "r", encoding="utf-8") as f:
                data = json.load(f)
            fname = fpath.name
            classification = {
                "agent": "unknown",
                "confidence": "low",
                "reason": "",
                "latest_user_time": None,
                "latest_user_content": None,
            }
            # system_prompt is the most authoritative classifier
            # ⚠️ CRITICAL: Must check AGENT HEADER, not loose keyword grep.
            # Hot's system_prompt contains "lover" as a rule word ("叫另一个人的名字
            # （lover/buffett）"), so 'lover' in sp.lower() is a FALSE POSITIVE.
            sp = data.get("system_prompt", "")
            sp_header = sp[:200]  # Agent declaration is always in first 200 chars

            # Hot agent header: starts with "# Hot" or contains "你的名字：hot" / "我是Hot"
            if sp_header.startswith("# Hot") or sp_header.startswith("# hot") or \
               "你的名字：Hot" in sp_header or "你的名字：hot" in sp_header or \
               "我是Hot" in sp_header or "我是hot" in sp_header or \
               "私人助理" in sp_header:
                classification["agent"] = "non_lover"
                classification["confidence"] = "high"
                classification["reason"] = "json.system_prompt header: Hot"

            # Lover agent header: "你的名字：Lover" / "你的名字：lover" / "即Lover" in FIRST 200 chars
            elif "你的名字：Lover" in sp_header or "你的名字：lover" in sp_header or \
                 "你的名字：Alexander" in sp_header or "即Lover" in sp_header:
                classification["agent"] = "lover"
                classification["confidence"] = "high"
                classification["reason"] = "json.system_prompt header: Lover"

            # Buffett agent header
            elif "你的名字：Buffett" in sp_header or "你的名字：buffett" in sp_header or \
                 "我是Buffett" in sp_header or "我是buffett" in sp_header:
                classification["agent"] = "non_lover"
                classification["confidence"] = "high"
                classification["reason"] = "json.system_prompt header: Buffett"

            # 国学术数 / BaZi agent header
            elif "你的名字：Bazi" in sp_header or "你的名字：bazi" in sp_header or \
                 "国学术数" in sp_header or "八字" in sp_header:
                classification["agent"] = "non_lover"
                classification["confidence"] = "high"
                classification["reason"] = "json.system_prompt header: BaZi/国学"
            # Extract latest user message from messages array
            messages = data.get("messages", [])
            if messages:
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        content = (msg.get("content") or "").strip()
                        if content:
                            classification["latest_user_content"] = content[:80]
                        ts = parse_timestamp(msg.get("timestamp"))
                        if ts:
                            classification["latest_user_time"] = ts.isoformat()
                        break
            if classification["agent"] == "non_lover":
                non_lover_sessions.append(fname)
            elif classification["agent"] == "lover":
                lover_entry = {
                    "file": fname,
                    "confidence": classification["confidence"],
                    "latest_user_time": classification["latest_user_time"],
                    "latest_user_content": classification["latest_user_content"],
                    "reason": classification["reason"],
                }
                lover_candidate_sessions.append(lover_entry)
                if classification["latest_user_time"]:
                    msg_ts = parse_timestamp(classification["latest_user_time"])
                    if msg_ts and msg_ts >= since_dt:
                        lover_user_found = True
                        if (
                            latest_lover_user_time is None
                            or classification["latest_user_time"]
                            > latest_lover_user_time
                        ):
                            latest_lover_user_time = classification[
                                "latest_user_time"
                            ]
            # "unknown" — log for awareness
        except Exception as e:
            errors.append(f"{fpath.name}: {e}")

    summary = {
        "found_lover_messages": lover_user_found,
        "latest_lover_user_time": latest_lover_user_time,
        "since": since_dt.isoformat(),
        "non_lover_sessions": non_lover_sessions,
        "lover_candidate_sessions": lover_candidate_sessions,
        "sessions_scanned": len(jsonl_files) + len(json_files),
        "errors": errors if errors else None,
    }

    if args.output_json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        # Human-readable summary — explicit dual-format count prevents
        # redundant manual .json verification (v0.35 fix)
        json_count = len(json_files)
        scan_msg = f"Scanned {len(jsonl_files)} JSONL sessions"
        if json_count:
            scan_msg += f" + {json_count} .json session files"
        scan_msg += f" since {since_dt.isoformat()}"
        print(scan_msg)
        print(f"  Lover user messages found? {'YES ✅' if lover_user_found else 'NO ❌'}")
        if latest_lover_user_time:
            print(f"  Latest Lover user msg: {latest_lover_user_time}")
        if non_lover_sessions:
            print(f"  Non-Lover sessions ({len(non_lover_sessions)}):")
            for s in non_lover_sessions[:5]:
                print(f"    - {s}")
            if len(non_lover_sessions) > 5:
                print(f"    ... and {len(non_lover_sessions)-5} more")
        if lover_candidate_sessions:
            print(f"  Lover candidate sessions ({len(lover_candidate_sessions)}):")
            for s in lover_candidate_sessions:
                print(
                    f"    - {s['file']} ({s['confidence']}, last user: {s.get('latest_user_content','?')[:40]})"
                )
        if errors:
            print(f"  Errors ({len(errors)}):")
            for e in errors:
                print(f"    - {e}")


if __name__ == "__main__":
    main()
