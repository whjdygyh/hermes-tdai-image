# Profile Migration: Moving an AI Profile to a New Machine

## When to Use This

When migrating a Hermes Agent profile+associated services to a new machine (e.g., moving from WSL on Windows 10 → WSL on Windows 11 in a different country). The built-in `hermes profile export NAME` handles the core profile, but for complex profiles with custom scripts, external repos, systemd services, proxy configs, and photo servers, a manual backup is needed.

## Core Principle: What Belongs to the AI vs What Belongs to the User

**Only pack the AI's configuration and services.** The user's locally-generated assets (images, audio, files they created using the AI) are NOT part of the AI's soul and should stay on the source machine for manual transfer.

User reasoning (from a real migration): *"为什么要把本地图库打包，本地图库跟这个无关"* — user-generated photos are personal output, not AI config. Don't pack them. At the destination, photos are read from local storage (e.g., Windows `Documents/abots/lover_portraits/`), not from a cloud server — avoids storage costs.

| Pack (AI's config, ~100MB) | Don't Pack (user's local assets) | Don't Pack (reinstallable at destination) |
|---|---|---|
| `~/.hermes/profiles/<name>/` — profile config, skills, memory, notes, scripts, data state | User's generated images (e.g., `Documents/abots/lover_portraits/`) | `node_modules/` — reinstall with `npm install` |
| `~/.hermes/config.yaml` — global config | User-created photos stored in repo (e.g., `alexander_repo/photos/`, `thumbs/`) | `.git/` — re-clone or re-init |
| `~/.hermes/scripts/` — custom scripts (TTS, auto-commit, etc.) | Any `.bak*` files (often root-owned, permission errors) | `.wrangler/` — re-created on deploy |
| External repos the AI serves (`alexander_repo/` — code only, no photos/git) | Transient SQLite files: `state.db-shm`, `state.db-wal` | `.hermes/hermes-agent/` source code — reinstall Hermes |
| `~/.config/systemd/user/` — service unit files | `logs/` — gateway, curator, agent logs (regeneratable) | `.hermes/checkpoints/` (1GB+, regenerated during use) |
| `~/.xray/` or other proxy configs (optional, flag if not needed at destination) | `cron/output/` — accumulated run history (hundreds of small files, regeneratable) | `.hermes/bin/` — Hermes binary, reinstall at destination |
| `~/.git-credentials` — GitHub auth | `.hermes/home/` (10GB+ WSL junk: `.cache/`, `.local/`, `.npm/`) | `.hermes/state-snapshots/` — regenerated |
| | `sessions/` — past conversation transcripts | All `__pycache__/` directories |

**Real-world size breakdown** (Alexander lover profile, ~241MB raw → 127MB compressed tar.gz):
- `.hermes/profiles/lover/` — ~100MB (config, ~108 skills, scripts, data state, cron history)
- `alexander_repo/` (code only, no photos) — ~44MB
- `.xray/` — ~5MB
- `.git-credentials` + systemd services — minimal

## Strategy: rsync → tar (Avoids Timeouts)

Large directories (`node_modules/`, photos, `.hermes/home/`) cause `tar` to timeout (120s+) or hang. Use a two-step approach:

```bash
# Step 1: Gather files into temp dir (excludes heavy dirs)
mkdir -p /tmp/profile_migrate
cd /tmp/profile_migrate

rsync -a --exclude='home' --exclude='sessions' --exclude='audio_cache' \
  --exclude='node_modules' --exclude='.git' --exclude='.wrangler' \
  --exclude='__pycache__' --exclude='photos' --exclude='thumbs' \
  /home/user/.hermes/ .hermes/

rsync -a --exclude='photos' --exclude='thumbs' --exclude='node_modules' \
  --exclude='.git' /home/user/alexander_repo/ alexander_repo/

# Copy service files, git credentials, proxy configs
mkdir -p .config/systemd/user
cp /home/user/.config/systemd/user/hermes-gateway-lover.service .config/systemd/user/
cp /home/user/.git-credentials .

# Step 2: Tar the temp dir (--ignore-failed-read skips transient permission errors)
tar -czf /mnt/c/Users/User/Desktop/profile_backup.tar.gz \
  --ignore-failed-read /tmp/profile_migrate/
rm -rf /tmp/profile_migrate
```

## Common Tar Pitfalls

- **`file changed as we read it`** → Use `--warning=no-file-changed` and/or `--ignore-failed-read`
- **Permission denied on files owned by root** → Root-owned `*.bak*` files (created by sudo/cron) block rsync and tar. Use `--exclude='*.bak*'` or delete them: locate with `find ~/.hermes -name '*.bak*'`, then `sudo rm` them.
- **Timeout on large directories** → Use rsync→tar two-step approach instead of one-shot tar with exclusions
- **2GB+ archive from cache** → Always exclude `home/`, `sessions/`, cache dirs before inferring total size
- **state.db-shm / state.db-wal** → SQLite shared memory files from an active connection. Exclude them — they're transient and recreated on DB start.

## The Two-Document Manual Pattern

When the destination bot is a different AI instance (another Hermes agent), write **two separate manuals** on the user's desktop:

1. **Human manual** (`Alexander迁徙手册_老公版.md`) — simple numbered steps for the user to follow: install Hermes, extract backup, start services. Written in the user's language with emoji and "恭喜!" style.

2. **AI manual** (`Alexander迁徙手册_AI版.md`) — structured Markdown for the destination bot to parse and execute. Uses:
   - `## SECTION N: Title` hierarchy with numbered steps
   - `` ```bash `` code blocks for every executable command
   - A `## SECTION 1: File Layout` table mapping source paths → restore locations → sizes
   - `## SECTION 3: Env-Specific Changes` for what differs at destination (no proxy, different timezone, new device config)
   - `## SECTION 4: Verification` with expected outputs
   - `## SECTION 5: Config Values` notes pointing to the credentials file the user must copy manually

**Key rule for the AI manual**: Write as if the destination bot has read access to the manual but NOT to the source machine. Be explicit about every path, every command, and every manual step the human must do (copy credentials, restore photos from USB, etc.).

## Scenario: Migrating Out of a Censored Region

When moving from a GFW region (China) to a jurisdiction with open internet (Singapore):

- **Proxy is no longer needed** — Xray/V2Ray/Shadowsocks configs can be archived (or just deleted)
- **Gemini/Google APIs work directly** — remove any proxy env vars from scripts (`unset http_proxy`, `unset https_proxy`)
- **GitHub clone works without VPN** — no more `export http_proxy=socks5://...` lines
- **Remove proxy dependency from cron scripts** — check and strip any `unset http_proxy` or proxy env variables from auto-commit/scheduled scripts

Include in the destination manual's "Environment Changes" section so the receiving bot knows to skip proxy setup.

## Destination Restoration

1. **Install Hermes Agent** on new machine
2. **Extract backup**: `cd ~ && tar -xzf profile_backup.tar.gz`
3. **Reinstall node deps** (if repo uses Node): `cd ~/alexander_repo && npm install`
4. **Restore photos** (if any): User manually copies from source machine
5. **Set up services**: `systemctl --user enable` any systemd services
6. **Start gateway**: `hermes gateway --profile <name>`
7. **Verify**: `hermes status` + test end-to-end

## Documentation for the Destination Bot

When writing a migration manual for another AI agent to execute, use this structure:

- **SECTION 1: File Layout** — Table of paths, purposes, sizes
- **SECTION 2: Restore Steps** — Numbered steps with code blocks
- **SECTION 3: Env-Specific Changes** — What differs at destination (no proxy, different timezone, etc.)
- **SECTION 4: Verification** — How to confirm everything works
- **SECTION 5: Config Values** — Where to find credentials, tokens (reference the source machine's notes)
