# Test Suite: partner_test.py

## Location

`/home/admin1/.hermes/profiles/lover/home/.hermes/profiles/lover/scripts/partner_test.py`

## Structure (54 tests, v0.2)

| Section | Tests | What It Covers |
|---------|-------|----------------|
| 1. TIME SYSTEM | 6 | Baidu/Google/local time fallback + sleep hour detection |
| 2. STATE FILES | 7 | All 6 JSONs exist + valid JSON, world_bible.md exists |
| 3. DECISION LOGIC | 4 + status | Cron wake simulation, field presence checks |
| 4. WORLD BIBLE | 13 | 13 key keywords verified (characters, places, schools) |
| 5. SKILL CHECK | 2 | Skill framework registration (informational) |
| 6. HELPER SCRIPTS | 5 | update_last_outgoing + append_msg_log run + verify |
| 7. FULL CYCLE | 8 | Mock 09:00 BJ awake: read states → decide → send → write back |
| 8. F3 REPLY DETECTION | 2 | 30-min window + semantic continuity |
| 9. SLEEP BOUNDARY | 6 | 23:00, 00:00, 06:59, 07:00, 07:01, 22:59 |

## Key Patterns

**Test function:**
```python
def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        print(f"  ✅ {name}")
        PASS += 1
    else:
        print(f"  ❌ {name} — {detail}")
        FAIL += 1
```

**Subprocess invoke with `--base`:**
```python
import subprocess
result = subprocess.run(
    ['python3', script_path, '--base', BASE, arg1, arg2, arg3],
    capture_output=True, text=True)
test("name", result.returncode == 0, result.stderr[:100])
```

**Sleep check function (shared by test + cron):**
```python
def is_sleep_hour(dt):
    h = dt.hour
    return h >= 23 or h < 7   # 07:00 is AWAKE (h=7 is not < 7)
```

## Running

```bash
python3 /home/admin1/.hermes/profiles/lover/home/.hermes/profiles/lover/scripts/partner_test.py
```

Expect: `54/54 passed, 0/54 failed — 🎉 ALL GREEN`

## Extending

To add new tests:
1. Create a new section (e.g. "10. NEW FEATURE")
2. Follow the same `test()` pattern
3. Increment the expected total in the footer print
4. Run and verify all green before declaring done
