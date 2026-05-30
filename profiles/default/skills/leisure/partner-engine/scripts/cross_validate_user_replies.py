#!/usr/bin/env python3
"""
cross_validate_user_replies.py — Cross-validate user reply count against session JSONL files.

Purpose:
  msg_log.json has a known gap: user messages exchanged via direct Hermes chat sessions
  (not through lover_reply_hook pipeline) are NOT written to msg_log.json. This causes
  cron jobs to see "0 user replies" even when the user has been actively chatting.
  
  This script scans Lover session JSONL files to find real user messages within a time
  window, enabling proper cross-validation of silent protection decisions.

Usage:
  python3 cross_validate_user_replies.py --sessions-dir /path/to/lover/sessions [--hours 72] [--since "2026-05-13T23:21:00+08:00"]

Arguments:
  --sessions-dir   Path to Lover session directory (required)
  --hours          How far back to scan in hours (default: 72)
  --since          Explicit cutoff timestamp (overrides --hours). ISO format.
  --verbose        Print all matching messages (default: only counts)
  --output-json    Output results as JSON (default: human-readable)

Exit codes:
  0 — Success
  1 — Bad arguments
  2 — Directory not found

Output (stdout):
  Total user messages found in the window
  List of timestamp + content snippet (if --verbose)
  JSON summary (if --output-json)

Example:
  python3 cross_validate_user_replies.py \\
    --sessions-dir /home/admin1/.hermes/sessions \\
    --hours 72 \\
    --verbose
  
  python3 cross_validate_user_replies.py \\
    --sessions-dir /home/admin1/.hermes/sessions \\
    --since "2026-05-13T23:21:00+08:00" \\
    --output-json

Integration with partner-engine:
  In CRON mode (Step 2 - 跨日消息堆积 check), use this script instead of
  relying on msg_log.json alone:
  
    python3 /path/to/scripts/cross_validate_user_replies.py \\
      --sessions-dir /home/admin1/.hermes/sessions \\
      --since "$(python3 -c "from datetime import datetime, timedelta, timezone; print((datetime.now() - timedelta(hours=72)).isoformat())")" \\
      --output-json
  
  ⚠️ After running, you MUST apply v0.15 filtering: the script returns ALL user
  messages from ALL agents. Filter out messages from Hot/BaZi/other agents
  using the system-prompt method (see references/manual-session-verification-20260516.md Step 2).
  If none of the returned messages belong to Lover → treat as "0 user replies."
"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional


def parse_iso_timestamp(ts_str: str) -> Optional[datetime]:
    """Parse ISO 8601 timestamp to datetime. Handles various formats found in JSONL."""
    if not ts_str or not isinstance(ts_str, str):
        return None
    
    # Remove trailing Z and replace with +00:00
    ts_str = ts_str.replace('Z', '+00:00')
    
    # Common formats seen in Lover session JSONL
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(ts_str, fmt)
        except (ValueError, TypeError):
            continue
    
    return None


def scan_session_files(sessions_dir: str, cutoff: datetime) -> List[Dict]:
    """Scan all JSONL files in sessions_dir for user messages after cutoff."""
    results = []
    
    pattern = os.path.join(sessions_dir, "*.jsonl")
    files = sorted(glob.glob(pattern))
    
    if not files:
        print(f"⚠️  No JSONL files found in {sessions_dir}", file=sys.stderr)
        return results
    
    for fpath in files:
        fname = os.path.basename(fpath)
        try:
            with open(fpath, 'r', encoding='utf-8', errors='replace') as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    
                    role = data.get('role', '')
                    if role != 'user':
                        continue
                    
                    ts_str = data.get('timestamp', '')
                    content = data.get('content', '')
                    
                    ts = parse_iso_timestamp(ts_str)
                    if ts is None:
                        continue
                    
                    if ts >= cutoff:
                        results.append({
                            'file': fname,
                            'timestamp': ts_str,
                            'content': str(content)[:200] if content else '',
                        })
        except (IOError, OSError) as e:
            print(f"⚠️  Error reading {fname}: {e}", file=sys.stderr)
            continue
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Cross-validate user reply count against session JSONL files"
    )
    parser.add_argument(
        '--sessions-dir',
        required=True,
        help='Path to Hermes system session directory (e.g., /home/admin1/.hermes/sessions/ — NOT the profile-level sessions dir). All agent sessions live here system-wide.'
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=72,
        help='How far back to scan in hours (default: 72)'
    )
    parser.add_argument(
        '--since',
        help='Explicit cutoff timestamp (ISO format, e.g., "2026-05-13T23:21:00+08:00"). Overrides --hours.'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print all matching messages'
    )
    parser.add_argument(
        '--output-json',
        action='store_true',
        help='Output results as JSON'
    )
    
    args = parser.parse_args()
    
    # Validate sessions directory
    if not os.path.isdir(args.sessions_dir):
        print(f"❌ Directory not found: {args.sessions_dir}", file=sys.stderr)
        sys.exit(2)
    
    # Determine cutoff time
    if args.since:
        cutoff = parse_iso_timestamp(args.since)
        if cutoff is None:
            print(f"❌ Cannot parse --since value: {args.since}", file=sys.stderr)
            sys.exit(1)
    else:
        cutoff = datetime.now() - timedelta(hours=args.hours)
    
    # Scan
    matches = scan_session_files(args.sessions_dir, cutoff)
    
    # Output
    if args.output_json:
        output = {
            'sessions_dir': args.sessions_dir,
            'cutoff': cutoff.isoformat(),
            'files_scanned': len(glob.glob(os.path.join(args.sessions_dir, "*.jsonl"))),
            'user_message_count': len(matches),
            'has_user_replies': len(matches) > 0,
            'matches': [
                {
                    'file': m['file'],
                    'timestamp': m['timestamp'],
                    'content': m['content'][:100],
                }
                for m in matches[:50]  # Limit output
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"📁 Sessions dir: {args.sessions_dir}")
        print(f"📅 Cutoff: {cutoff.isoformat()}")
        print(f"🔍 Files scanned: {len(glob.glob(os.path.join(args.sessions_dir, '*.jsonl')))}")
        print(f"👤 User messages found: {len(matches)}")
        print(f"✅ Has user replies: {'YES' if matches else 'NO'}")
        
        if args.verbose and matches:
            print("\n--- Matching messages ---")
            for i, m in enumerate(matches[:30], 1):
                print(f"{i:2d}. [{m['timestamp']}] [{m['file'][:30]:30s}] {m['content'][:120]}")
            if len(matches) > 30:
                print(f"\n... and {len(matches) - 30} more (use --output-json for full data)")
    
    sys.exit(0)


if __name__ == '__main__':
    main()
