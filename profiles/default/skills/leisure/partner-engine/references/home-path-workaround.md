# HOME Path Bug & Absolute Path Convention

## Root Cause

Hermes framework sets `HOME=$HERMES_HOME/home`. For this profile:
```
HERMES_HOME = /home/admin1/.hermes/profiles/lover
HOME        = /home/admin1/.hermes/profiles/lover/home
```

This means `~` expands to `/home/admin1/.hermes/profiles/lover/home/`, while the actual data
root is `/home/admin1/.hermes/profiles/lover/`. Using `~/.hermes/profiles/lover/...` produces
a double-nested path:
```
~/.hermes/profiles/lover/state/last_outgoing.json
→ /home/admin1/.hermes/profiles/lover/home/.hermes/profiles/lover/state/last_outgoing.json
```

## Fix: Use Explicit `BASE` Everywhere

Define once and use everywhere:

```bash
BASE=/home/admin1/.hermes/profiles/lover/home/.hermes/profiles/lover
cat $BASE/state/active_context.json
python3 $BASE/scripts/append_msg_log.py --base "$BASE" bot "message" "ctx" "trigger"
```

Directory layout under BASE:
```
BASE/
├── state/          ← 6 state files
├── scripts/        ← helper scripts
├── data/           ← msg_log.json
├── notes/          ← free-form markdown
└── skills/         ← skill definitions (framework-managed)
```

## Testing Note

The test file `partner_test.py` at `scripts/` also uses `os.path.expanduser("~/.hermes/profiles/lover")`
which resolves correctly for Python-level file reads but can hide the bug in bash-level commands.
Always test bash path construction separately.

## What NOT to Do

❌ `cat ~/.hermes/profiles/lover/state/*.json` — expands incorrectly in bash
❌ `os.path.expanduser("~/state/last_outgoing.json")` — subtle wrong path
✅ Always construct paths from `$BASE` or from `HERMES_HOME/home/.hermes/profiles/lover/`
