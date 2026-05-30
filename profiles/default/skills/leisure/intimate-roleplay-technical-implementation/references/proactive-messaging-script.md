# Proactive Random-Timed Messaging Script Reference (v2 — May 8, 2026)

> **Last update:** 2026-05-08 — v2 upgrade: DAILY_MAX=9, DAILY_MIN=5, MIN_PHOTOS=2, graduated probability with catch-up, minute-based state tracking, photo guard logic.
> 
> **Previous version (v1):** DAILY_MAX=2, base probability 0.05, hourly state tracking, no photo min.
> 
> **Character context:** Alexander (14yo, 188cm/95kg, partner to Andy/安迪). Messages are from a schoolboy boyfriend to his older partner.

## Quick Reference

| Parameter | v1 (old) | v2 (current) |
|-----------|:--------:|:------------:|
| DAILY_MAX | 2 | **9** |
| DAILY_MIN | 0 | **5** |
| MIN_PHOTOS | 0 | **2** |
| State tracking | hour-based | **minute-based** (`last_minute`) |
| Probability curve | 0.05 + 0.03/h (linear up to 0.50) | **0.20 + 0.05/h (graduated 25-80%, with catch-up)** |
| Catch-up mechanism | None | **Force at 80%+ if low, 100% at 20:00** |
| Photo guard | None | **Boost to 55% if <2 photos sent** |
| Messages library | 27 (9 scenarios × 3) | **56 (7 scenarios × ~8 each)** |
| Photos templates | 6 (6 scenarios) | **11 (4 daytime scenarios)** |

## File Locations

```
# ⚠️ CRITICAL: HOME env var is overridden to /home/admin1/.hermes/profiles/lover/home
# NEVER use os.path.expanduser("~") or ~ in paths — use absolute paths only!

/home/admin1/.hermes/scripts/daily_random_lover_message.py               ← CRON RUNS THIS
/home/admin1/.hermes/profiles/lover/scripts/daily_random_lover_message.py ← PROFILE BACKUP
/home/admin1/.hermes/profiles/lover/data/random_msg_state.json            ← STATE FILE (absolute path)
/tmp/hermes/cache/                                                        ← PHOTO CACHE
```

**Always sync after patching:** `cp /home/admin1/.hermes/profiles/lover/scripts/daily_random_lover_message.py /home/admin1/.hermes/scripts/daily_random_lover_message.py`

## Architecture

The script runs via cron (`*/30 8-21 * * *`, UTC+8) and probabilistically decides whether to send a message each time it fires.

```
entry()
  ├── load_state()              ← read random_msg_state.json
  ├── reset_if_new_day()        ← if date changed, reset sent_count=0, photo_count=0
  ├── check_daily_cap()         ← if sent_count >= 9, exit immediately
  ├── check_interval()          ← at least 30 min since last send
  ├── decide_scenario()         ← map current time to scenario
  ├── calculate_probability()   ← 0.20 + 0.05*h offset, cap 0.80
  ├── apply_catch_up()          ← boost if behind on daily min
  ├── roll_dice()               ← random.random() < probability
  ├── pick_message()            ← from scenario library, avoid last message
  ├── decide_photo()            ← based on scenario + guard logic
  │   ├── True → generate_scene_photo() → upload_feishu_image()
  │   └── False → text only
  ├── send_feishu_message()     ← env -u http_proxy... curl call
  ├── log_message()             ← append to daily_msg_log.json (conversation continuity)
  ├── save_state()              ← update state
  └── print_status()            ← log result to stdout (captured by cron)
```

## Scenario Mapping (Weekday)

| Scenario | Time | Messages | Photo? | Notes |
|----------|:----:|:--------:|:------:|-------|
| `early_morning` | 06:00-08:29 | 7 | ❌ | Waking up, getting ready |
| `morning_class` | 08:30-11:49 | 8 | ✅ 3 | Sneaky texts from back row |
| `lunch` | 11:50-12:59 | 6 | ❌ | Cafeteria chat |
| `afternoon_class` | 13:00-15:59 | 8 | ✅ 3 | Last period boredom |
| `after_school` | 16:00-17:59 | 6 | ✅ 3 | Heading home, basketball |
| `evening` | 18:00-20:59 | 8 | ✅ 3 | Home, dinner, homework |
| `night` | 21:00-23:59 | 6 | ❌ | Quiet late night |

**Total:** 56 messages + 11 photo prompt templates across 4 photo-capable scenarios.

## Graduated Probability Curve with Catch-Up

```python
base_prob = 0.20 + (hour - 8) * 0.05   # 20% at 8am, linearly rising
base_prob = min(base_prob, 0.80)         # cap at 80%

# Catch-up mechanism — ensures daily minimum:
if hour >= 18 and sent < 3:
    base_prob = max(base_prob, 0.80)     # boost to 80%+ if far behind
if hour >= 20 and sent < DAILY_MIN:
    base_prob = 1.0                      # FORCE send — must hit minimum

# Dampening — prevents flooding when already sent a lot:
if sent >= 6:
    base_prob *= 0.6                     # gradually reduce frequency
if sent >= 8:
    base_prob *= 0.3                     # rare, only to hit max
```

### Probability Table

| Time | 0-2 sent | 3-5 sent | 6-8 sent | 9 sent |
|:----:|:--------:|:--------:|:--------:|:-----:|
| 08:00 | 20% | — | — | — |
| 10:00 | 30% | — | — | — |
| 12:00 | 40% | 40% | — | — |
| 14:00 | 50% | 50% | 30% | — |
| 16:00 | 60% | 60% | 36% | — |
| 18:00 | **80%** | 75% | 45% | — |
| 20:00 | **100%** 🚨 | 80% | 48% | 0% |
| 21:00 | — | 80% | 48% | 0% |

## Photo Decision Logic

```python
photo_prob = PHOTO_SCENARIOS.get(scenario, 0.1)  # base per scenario
if photo_count < MIN_PHOTOS and sent < 7:         # haven't hit photo min yet
    photo_prob = max(photo_prob, 0.55)            # boost to at least 55%
```

## State File Format

```json
{
    "last_date": "2026-05-08",
    "sent_count": 4,
    "photo_count": 2,
    "last_minute": 870,
    "last_scenario": "afternoon_class",
    "last_message": "老公在上课好无聊啊，想你了"
}
```

| Field | Type | Purpose |
|-------|------|---------|
| `last_date` | str (YYYY-MM-DD) | Daily reset trigger |
| `sent_count` | int 0-9 | Daily counter, checked against DAILY_MAX |
| `photo_count` | int 0-9 | Photo counter, checked against MIN_PHOTOS |
| `last_minute` | int (0-1439) | Minute-of-day, prevents <30min interval |
| `last_scenario` | str | Avoids repeating same scenario |
| `last_message` | str | Avoids sending exact same message twice |

**State file path:** `/home/admin1/.hermes/profiles/lover/data/random_msg_state.json` (absolute — never use `~`)\n\n## 📋 Message Logging — Conversation Continuity (Added May 8, 2026)\n\n**Why:** The cron script sends messages autonomously. When the user asks follow-up questions (\"那个校服呢？\"), the bot has no memory of what was sent. The log bridges this gap.\n\n### Log File\n\n**Path:** `/home/admin1/.hermes/profiles/lover/data/daily_msg_log.json`\n\nOn every successful send, the script appends:\n\n```python\nlog_entry = {\n    \"time\":      \"14:23:06\",\n    \"date\":      \"2026-05-08\",\n    \"scenario\":  \"afternoon_class\",\n    \"text\":      \"老公～体育课刚跑完800米…\",\n    \"had_photo\": True,\n    \"photo_desc\": \"after_pe_class_locker_room\",\n    \"timestamp\": 1747729386\n}\n```\n\n**Retention:** Last 50 entries. Older entries pruned on `append()`.\n\n### Bot Query Pattern\n\nIn conversation, when user references something the cron job sent:\n\n```python\nimport json, os\n\ndef query_log():\n    \"\"\"Load messages the cron job has sent today.\"\"\"\n    log_path = \"/home/admin1/.hermes/profiles/lover/data/daily_msg_log.json\"\n    if not os.path.exists(log_path):\n        return []\n    with open(log_path) as f:\n        return json.load(f).get(\"log\", [])\n```\n\nThe bot uses this to answer naturally: \"哦那张啊～体育课换衣服拍的，所以没穿校服嘛😏\"\n\n### Log File Path in File Locations\n\n```\n/home/admin1/.hermes/profiles/lover/data/daily_msg_log.json               ← MESSAGE LOG (50 entries max)\n```\n\n### ⚠️ Pitfall: State Format Migration (First Run After Upgrade)\n\nWhen v1 → v2 script changed state fields (e.g., `last_hour` → `last_minute`), the old state.json caused crashes. **Always delete old state when upgrading:**\n\n```bash\nrm /home/admin1/.hermes/profiles/lover/data/random_msg_state.json\n```\n\n`load_state()` has try/except fallback to defaults, so missing file is handled gracefully.

## Feishu API — Proxy Rule

**ALL Feishu API calls must strip proxies:**

```python
subprocess.run([
    'env', '-u', 'http_proxy', '-u', 'https_proxy',
    '-u', 'HTTP_PROXY', '-u', 'HTTPS_PROXY', '-u', 'ALL_PROXY',
    'curl', '-s', '-X', 'POST', ...
])
```

The system proxy routes through SOCKS5 (172.20.128.1:10808) for Gemini — but Feishu API fails when proxied.

## CRON Configuration

```yaml
# In hermes cron:
schedule: "*/30 8-21 * * *"
script: "daily_random_lover_message.py"  # resolved relative to ~/.hermes/scripts/
deliver: local                           # cron output goes to local only
```

**Why `deliver: local`:** The script sends Feishu messages directly via API. Cron output is just a one-line status log. `deliver: origin` would flood the user's chat with "已发送" / "跳过" messages.

## Pitfalls

### HOME Env Variable Override (⚠️ Critical)
`HOME` is set to `/home/admin1/.hermes/profiles/lover/home` — NOT `/home/admin1`. Any `~` in paths resolves to the wrong tree. Use absolute paths for everything.

### Script Must Be in Two Places
After patching the profile script, always sync to cron scripts dir:
```bash
cp /home/admin1/.hermes/profiles/lover/scripts/daily_random_lover_message.py \
   /home/admin1/.hermes/scripts/daily_random_lover_message.py
```

### Timezone — Always UTC+8
Server runs UTC. All datetime operations must use explicit China timezone:
```python
CN_TZ = timezone(timedelta(hours=8))
cn_now = lambda: datetime.now(CN_TZ)
```

### Photo Generation Failure Is OK
If Gemini photo generation fails (filter/block/network), send text-only. Don't crash, don't retry indefinitely.

### ⚠️ Timeout Collision: Gemini curl timeout MUST be shorter than cron timeout
The cron wrapper kills the script after 120s. The `generate_photo()` curl call also has `timeout=120`. When Gemini is slow (common via SOCKS5 proxy), **both timeouts fire simultaneously** — the script is killed before it can fall back to text-only.

**Fix:** The curl timeout inside `generate_photo()` must be strictly less than the cron timeout:
```python
# In generate_photo() — line 248 of the script:
result = subprocess.run(
    ...,
    timeout=60,    # ← MUST be 60s or less, never 120s (cron timeout)
    capture_output=True, text=True
)
```
With `timeout=60`, if Gemini hangs:
- Curl times out after 60s → `generate_photo()` returns `None`
- Script falls through to text-only send (the graceful fallback)
- Total script runtime ~65s → well within the 120s cron limit

**Verify during maintenance:** Check that curl timeout + script overhead ≈ 80-90s max. If cron timeout ever changes (e.g. reduced to 60s), update this value accordingly.

### Weekend/Weekday Mode
Script uses `datetime.now(CN_TZ).weekday() >= 5` to detect weekends:
- **Weekday:** 7 scenarios, 56 messages, 11 photo templates, start 08:00
- **Weekend:** different scenario set (lazy_morning/afternoon_together/cozy_evening), higher probability, more messages
