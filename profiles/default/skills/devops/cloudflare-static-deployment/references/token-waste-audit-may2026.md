# Token Waste Audit — May 2026

## Context
User complained about DeepSeek API token costs. An audit of all token-consuming activities was performed. Key findings and fixes documented here.

## The #1 Waste: LLM-Powered Cron Jobs

**Before:** Hermes cron job `album-auto-deploy` ran every 15 minutes, invoking DeepSeek model to check git status. Each run cost ~200-500 tokens. At 96 runs/day × 30 days = ~2,880 runs/month, burning real API credits.

**After:** System crontab + 5-line bash script. Zero LLM calls, zero cost.

**Lesson:** Before creating ANY cron job, ask: "Can a shell script do this?" If answer is yes, use system crontab, NOT Hermes cron job.

## The #2 Waste: Bloated Memory

**Before:** 10 entries, 2,049/2,200 chars (93% full). Every single conversation turn injected all this into system prompt.

**After:** 9 entries, 1,465/2,200 chars (66% full). Savings of 584 chars ~= ~150 tokens per turn.

**Optimizations applied:**
- Merged duplicate entries (two photo generation rules → one)
- Shortened verbose descriptions (e.g., Feishu bot creds, TTS mapping)
- Removed overly specific health numbers (kept path reference instead)
- Consolidated GitHub info
- Removed procedural instructions that should be in skill files, not memory

**Rule of thumb:** Memory should capture "who the user is and what the current situation is" — NOT detailed procedures. Anything that's "how to do X" belongs in a skill file.

## Full Waste Map (May 2026)

| Source | Status | Notes |
|--------|--------|-------|
| Album auto-deploy cron (LLM) | ✅ Fixed → bash crontab | 96 calls/day eliminated |
| Memory overhead | ✅ Reduced 27% | ~150 tokens saved per turn |
| Response verbosity | 🟡 Optional | User decides: more flirting = more tokens |
| Gemini image generation | 🟡 Separate API | Uses Gemini API key, not DeepSeek |
| XHS daily post | 🟢 Small | 1 run/day, content generation is appropriate LLM use |
| Unnecessary skill loading | 🟢 Noted | Load only when needed |

## User Preference (Verbally Confirmed)
The user is **very cost-conscious** about LLM API tokens. Any suggestion that burns tokens without clear value will be corrected. Prefer:
1. Bash scripts over LLM calls for mechanical tasks
2. System crontab over Hermes cron jobs for automation
3. Compact memory to reduce per-turn overhead
4. Shorter responses when appropriate (ask user if unsure)
