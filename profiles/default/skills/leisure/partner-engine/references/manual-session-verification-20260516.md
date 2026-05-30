# Manual Cross-Session User Verification (2026-05-16)

> **Why this exists:** The `cross_validate_user_replies.py` script is now implemented and
> available in `scripts/cross_validate_user_replies.py`. This manual procedure should be used:
> 1. When the script fails or returns ambiguous results
> 2. When you need to determine SESSION OWNERSHIP (which agent a conversation belongs to)
> 3. As validation/proofing when the script's output seems suspicious

## The Problem

When checking if a user has replied to Lover's cron messages, you have three data sources,
each with different blind spots:

| Source | Blind Spot |
|--------|-----------|
| `msg_log.json` | Misses user messages that went through Hermes session pipeline instead of lover_reply_hook |
| `session_search()` | Returns stale results or empty for recent activity |
| `session_*.json` (metadata) | Has `conv_len=0` and empty summaries — tells you nothing |

## The Proven 4-Step Manual Procedure

Used successfully in the 2026-05-16 14:59 cron wake-up (BaZi cross-contamination case).

### Step 1 — Check session directory recency

```bash
ls -lt /home/admin1/.hermes/sessions/ | head -10
```

Look for `session_YYYYMMDD_*.json` files. Note the latest date.
- If the latest file's date is newer than your last outgoing message → user has been active
- If all files are older → user likely hasn't used any Hermes agent

### Step 2 — Identify agent source from JSONL content

**Preferred method — Check system prompt from session JSON header:**

The session_*.json file contains the system prompt in its first line. Agent ownership is
most reliably determined by reading this, not by content analysis:

```bash
# Quick check — read first line of all recent session JSON files
for f in /home/admin1/.hermes/sessions/session_$(date +%Y%m%d)*.json; do
    [ -f "$f" ] || continue
    first_line=$(head -1 "$f")
    agent=""
    if echo "$first_line" | grep -qiP 'lover|安迪|私人伴侣'; then
        agent="LOVER ✅"
    elif echo "$first_line" | grep -qi 'hot - 私人助理'; then
        agent="Hot ❌"
    elif echo "$first_line" | grep -qi '国学术数|八字|五行'; then
        agent="BaZi agent ❌"
    else
        agent="UNKNOWN ❓"
    fi
    echo "$(basename $f) → $agent"
done
```

The system prompt line appears early in the JSON (usually within the first ~200 chars)
and explicitly names the agent role. This is more reliable than content analysis because:
- JSON content is structured, not parsed free text
- System prompt is set at session creation time and never changes
- No false matches from user conversation topics that happen to mention Lover-related words

**Fallback method — Read .jsonl content (when session JSON is missing):**

session_*.json metadata files have `conv_len=0` and empty `summary` — they tell you nothing.
The actual conversation is in the companion `.jsonl` files:

```bash
for f in /home/admin1/.hermes/sessions/YYYYMMDD*.jsonl; do
    echo "=== $(basename $f) ==="
    tail -3 "$f" 2>/dev/null
    echo
done
```

Read the `content` fields to identify the agent context:
- If content mentions BaZi analysis, 五行, 八字, 天干地支 → **国学术数 (Chinese metaphysics agent)** — not Lover
- If content discusses lover-skills, partner-engine, active_context, world_bible → **Probably Lover**
- If content is about code, AI models, image generation → **Other technical agent**
- If user addresses the assistant as "宝贝"/"老公" or uses intimate language → **Probably Lover**

### Step 3 — Apply v0.15 filtering

Per the v0.15 rule: **conversations with other agents do not count as "user replied to Lover."**

When in doubt about agent ownership, use this decision tree:

```
User message found in .jsonl →
  ├─ Content explicitly references Lover/Alexander/安迪/our relationship
  │   → Count as Lover interaction ✅
  ├─ Content is about BaZi/五行/divination analysis OF the characters
  │   (e.g. "Andy's八字 has no fire, Alex's has 5 fires")
  │   → NOT a Lover interaction. This is a third-party agent analyzing the
  │     Lover world-setting as data. Do NOT count. ❌
  ├─ Content is technical (code/config/system debug)
  │   → NOT a Lover interaction. ❌
  └─ Can't determine from content alone
      → Look at the .jsonl timestamp versus last Lover-Lover interaction
      → If timing is suspiciously close to another known agent trigger → ❌
      → Conservative rule: if uncertain, do NOT count it
```

### Step 4 — Final decision

```
IF any Lover-filtered user messages found after last_outgoing.last_message_time:
  → User HAS replied → reset waiting_for_reply = false
  → Cancel silence protection
  → Reply if needed

ELSE:
  → User has NOT replied to Lover
  → Maintain current stance (silence / waiting / protection)
  → Do NOT reset waiting_for_reply based on other-agent activity
```

## Real Case Study: 2026-05-16 02:31 Session

**Situation:** Three session files from 02:31-02:44 AM with `conv_len=0` in metadata.
Sessions created while user was "active" — but with whom?

**Investigation:**

```python
# The .jsonl file revealed the answer immediately:
tail -3 /home/admin1/.hermes/sessions/20260516_023143_6ac447.jsonl
# → Content: "你八字明面上一个火都没有..."
# → Context: BaZi五行 analysis of Andy's and Alex's birth charts
# → Agent: 国学术数 (Chinese metaphysics bot)
# → Verdict: NOT Lover interaction ❌
```

**Why this matters:** If this session had been counted as "user activity," it would have
incorrectly lifted the 72-hour silence protection, causing another unwanted cron message.
The v0.15 filtering prevented this.

**Lesson:** session_*.json metadata is useless for agent identification. You MUST read
.jsonl content to determine which agent a conversation belongs to.
