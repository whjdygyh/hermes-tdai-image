---
name: cloudflare-static-deployment
description: Deploy static websites to Cloudflare Workers (with Assets) or Cloudflare Pages — Git integration, Wrangler CLI, handling auto-generated bot PRs, verification
---

# Cloudflare Static Deployment

Deploy static websites (photo albums, landing pages, SPAs) to Cloudflare's edge network. Supports both **Workers with Static Assets** and **Cloudflare Pages**.

## Prerequisites

- Git repository with static files (HTML, CSS, JS, images)
- Cloudflare account at [dash.cloudflare.com](https://dash.cloudflare.com)
- GitHub PAT with `repo` scope (for API operations)
- Node.js **v22+** required for Wrangler v5 (wrangler v5 requires Node >= 22, older versions like v12 will fail)

### ⚠️ Node.js Version: Critical Requirement

Wrangler **requires Node.js >= v22**. As of May 2026, the npm `@latest` tag installs wrangler v4.87.0 which needs Node >= 22. System Node (v12) or any version below 22 will fail.

**Known-good versions (verified May 2026):**
- **v24.15.0** — Works cleanly with wrangler v4.87.0 (no warnings) ✅
- **v20.20.2** — Works but shows `EBADENGINE` warnings (npm warns `Unsupported engine` but deployment still succeeds) ⚠️

**If your system Node is too old:**

1. **First check nvm paths** (WSL systems may have nvm but on non-default PATH):
```bash
ls /home/admin1/.nvm/versions/node/ 2>/dev/null
# Example output: v20.20.2  v24.15.0
```

2. **Use nvm with --delete-prefix** (fixes `.npmrc globalconfig/prefix` conflict):
```bash
export NVM_DIR="/home/admin1/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use --delete-prefix v24.15.0 --silent 2>/dev/null
node --version  # Should show v24.15.0
```

3. **Or set PATH directly without nvm:**
```bash
export PATH="/home/admin1/.nvm/versions/node/v24.15.0/bin:$PATH"
# Then use wrangler
npx --yes wrangler@latest whoami
```

#### 4. Only if no nvm version is available, install nvm from scratch (✅ Proven May 2026):

```bash
# Install nvm v0.40.1
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# Source it (or reopen shell)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Install Node 22
nvm install 22
nvm use 22
node --version  # v22.14.0

# Verify wrangler can now run
npm install -g wrangler
wrangler --version
```

**nvm tip for .npmrc conflicts:** If `nvm use` shows "N/A" or "prefix" errors, use `nvm use --delete-prefix v22.14.0 --silent 2>/dev/null`. This happens when `~/.npmrc` has a `globalconfig` or `prefix` setting from a system Node install.

**nvm path check:** If nvm is installed but not in PATH (common in WSL with non-default shells):
```bash
ls /home/admin1/.nvm/versions/node/ 2>/dev/null
# Then set PATH directly:
export PATH="/home/admin1/.nvm/versions/node/v22.14.0/bin:$PATH"
```
```bash
# Download Node.js v22 binary
curl -sL "https://nodejs.org/dist/v22.14.0/node-v22.14.0-linux-x64.tar.xz" -o /tmp/node22.tar.xz
tar -xf /tmp/node22.tar.xz -C /tmp/
/tmp/node-v22.14.0-linux-x64/bin/npx wrangler deploy
```

This avoids unnecessary downloads and keeps things fast.

## Strategy: Workers vs Pages

| Criteria | Workers + Assets | Pages |
|----------|-----------------|-------|
| Max files | 10,000 assets | 20,000 files |
| Max file size | 25 MiB | 25 MiB |
| Bandwidth | No documented cap | No documented cap |
| Build minutes | N/A (raw upload) | 500/month (free) |
| Deployment | `npx wrangler deploy` | Git integration / Direct Upload |
| Custom domain | Yes | Yes |

For a photo album (< 100 photos, < 25 MB each), either works. Workers is simpler (single CLI command), Pages has better Git integration.

## Deployment Steps

### ⏱️ Timeout Warning for Scripted Deploys

**`wrangler pages deploy` can take 30-90 seconds** depending on upload size. When running from within a bash script or cron job:
- If the script/tool has a 30-second default timeout (like many terminal exec wrappers), wrangler will be killed mid-upload
- This can leave the deployment in a partial state — files uploaded but index.html not updated
- **Solution:** Run wrangler directly in a terminal (no artificial timeout), or increase script timeout to >120s

**Proven example (May 6, 2026):** Inside `album_auto_commit.sh`, the git commit+push succeeded in ~5s but `wrangler pages deploy` timed out at 30s. Manual re-run completed successfully.

### Option A: Wrangler CLI (Workers + Assets) — preferred for quick deploys

```bash
# From the repo root:
npx wrangler deploy

# Wrangler auto-detects "Static" framework, prompts non-interactively:
# ? Do you want to modify these settings? → no
# ? Proceed with setup? → yes
```

This generates `wrangler.jsonc`:

```jsonc
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "<project-name>",
  "compatibility_date": "YYYY-MM-DD",
  "observability": { "enabled": true },
  "assets": { "directory": "." },
  "compatibility_flags": ["nodejs_compat"]
}
```

### Option B: Pages Git Integration

1. Go to Cloudflare Dashboard → Workers & Pages → Create → Pages
2. "Connect to Git" → Install/Authorize GitHub App (Cloudflare Workers and Pages)
3. Select repo → Framework: **Static** → Output dir: `.`
4. Deploy → receives `*.pages.dev` URL

### ⚠️ ⚠️ ⚠️ CRITICAL: REST API Fails for Deployments (May 2026 Discovery)

**Do NOT attempt to use the Cloudflare Pages REST API (`/deployments` endpoint) for direct upload deployments — it is fundamentally broken for this purpose.**

This was verified on May 6, 2026 through exhaustive testing:

| Attempt | Method | Result |
|---------|--------|--------|
| JSON body (`Content-Type: application/json`) | POST with `{"manifest": {...}}` | ❌ Error 8000096: "manifest field was not provided" |
| Python requests `.json=` parameter | POST with JSON body | ❌ Same error |
| `-F "manifest=@file.json"` (curl file upload) | POST with multipart | ❌ Same error |
| `-F "manifest={\"key\":\"val\"}"` (inline string) | POST with multipart | ✅ Deployment CREATED but files are 404 |
| `wrangler pages deploy` CLI | CLI | ✅ **Only reliable method** |

**Symptoms of a broken API deployment:**
- API returns `"success": true` with deploy stage "success"
- 0 missing hashes reported
- Stage URL returns 404 for ALL files (including `index.html`)
- Production URL never updates

**Root cause:** The Cloudflare Pages REST API deployment endpoint is designed for a workflow that:
1. POST manifest → returns upload_url + missing_hashes
2. PUT files to upload_url
3. Finalize

But when using `multipart/form-data`, the upload_url is never returned (`null` or `N/A`). The deployment record is created but no files are stored. The API is buggy for this workflow as of May 2026.

**✅ ONLY reliable method: `wrangler pages deploy` CLI** (see Option C below).

### Option C: Pages Direct Upload with Wrangler CLI (✅ **Only Reliable Method — May 2026**)

When Git integration is not possible (repo is private, GitHub App not installed, or user wants CLI-only), **Cloudflare Pages supports direct upload via wrangler CLI** using an API Token. This is the fastest way to deploy a private repo.

**🚨 NEVER try the REST API `/deployments` endpoint as an alternative — it creates broken deployments that return 404 for all files.** Always use `wrangler pages deploy`.

#### Prerequisites

- Cloudflare API Token with **Workers + Pages** permissions (format: `cfut_...`)
- Node.js >= v20 (v20.20.2 confirmed working with wrangler v4.87.0)
- The Cloudflare Account ID (get it from Dashboard or via API)

#### Step 1: Get Account ID

```bash
curl -s -X GET "https://api.cloudflare.com/client/v4/accounts" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); [print(a['id'], a['name']) for a in d['result']]"
```

#### Step 2: Create Pages Project (one-time)

```bash
export CLOUDFLARE_API_TOKEN="cfut_xxxxxxxxxxxxxxxxxxxx"
export CLOUDFLARE_ACCOUNT_ID="cf58c41e..."

npx wrangler pages project create PROJECT_NAME --production-branch main
# If project already exists, this step can be skipped
```

#### Step 3: Deploy

```bash
# From the project root directory:
export CLOUDFLARE_API_TOKEN="cfut_xxxxxxxxxxxxxxxxxxxx"

npx wrangler pages deploy . --project-name PROJECT_NAME --branch main
# Or add --commit-hash for traceability:
npx wrangler pages deploy . --project-name PROJECT_NAME --branch main --commit-hash=$(git rev-parse HEAD)
```

Output shows:
```
✨ Success! Uploaded N files (X sec)
🌎 Site deployed to: https://HASH.PROJECT_NAME.pages.dev
🌎 https://PROJECT_NAME.pages.dev (alias)
```

#### Step 4: Verify

```bash
curl -s -o /dev/null -w "%{http_code}" "https://PROJECT_NAME.pages.dev/"
# Should return 200
```

#### ☁️ Cloudflare API Token Format

| Format | Type | Source |
|--------|------|--------|
| `cfut_...` | Cloudflare API Token | Created in Dashboard → Profile → API Tokens |
| `cf_...` | Cloudflare Global Key | Legacy, use API Token instead |

**Required permissions for Pages deployment:**
- Account → Workers Scripts → Edit
- Account → Pages → Edit
- Zone → Zone Settings → Read (if using custom domain)

#### Save the Token After First Use — For Future Automation

**This must be done immediately after receiving a token.** If you don't save it, the next session will ask the user again — they'll be frustrated.

```bash
# Save to wrangler config (persists across Wrangler sessions)
mkdir -p ~/.wrangler/config
cat >> ~/.wrangler/config/default.toml << 'EOF'
[env]
CLOUDFLARE_API_TOKEN = "cfut_..."
EOF

# Verify it's readable
grep -q 'CLOUDFLARE_API_TOKEN' ~/.wrangler/config/default.toml && echo "✅ Token saved" || echo "❌ Failed to save"

# Also export for current session
export CLOUDFLARE_API_TOKEN="cfut_..."
```

**Also save to memory:**
```
memory(action='add', target='memory',
  content='Cloudflare API token stored at ~/.wrangler/config/default.toml for Pages deploys.')
```

#### Script: deploy-pages.sh — One-Command Re-deploy

After saving the token once, copy this script to `/home/admin1/.local/bin/deploy-pages.sh`:

```bash
#!/bin/bash
# deploy-pages.sh — Redeploy site to Cloudflare Pages using saved token
# Usage: deploy-pages.sh [project-name=alexander-album] [branch=main]
set -e

PROJECT="${1:-alexander-album}"
BRANCH="${2:-main}"
DIR="${3:-.}"

# Find token from stored config
TOKEN=$(grep 'CLOUDFLARE_API_TOKEN' ~/.wrangler/config/default.toml 2>/dev/null | head -1 | cut -d'"' -f2)
if [ -z "$TOKEN" ]; then
  echo "❌ No token found in ~/.wrangler/config/default.toml"
  echo "   Ask user for a new Cloudflare API Token"
  exit 1
fi

export CLOUDFLARE_API_TOKEN="$TOKEN"
export PATH="/home/admin1/.nvm/versions/node/v24.15.0/bin:$PATH"

echo "🚀 Deploying $PROJECT (branch: $BRANCH)..."
npx wrangler pages deploy "$DIR" --project-name "$PROJECT" --branch "$BRANCH"

echo "✅ Deployed! https://$PROJECT.pages.dev"
```

The script can also be used as a one-liner:
```bash
export CLOUDFLARE_API_TOKEN=$(grep 'CLOUDFLARE_API_TOKEN' ~/.wrangler/config/default.toml | cut -d'"' -f2)
export PATH="/home/admin1/.nvm/versions/node/v24.15.0/bin:$PATH"
npx wrangler pages deploy . --project-name PROJECT_NAME --branch main
```

#### Full Automation Script

```bash
#!/bin/bash
# deploy-pages.sh — Deploy static site to Cloudflare Pages with API token
set -e

PROJECT_NAME="${1:-alexander-album}"
DIR="${2:-.}"
BRANCH="${3:-main}"

# Node.js path (if using nvm)
export PATH="/home/admin1/.nvm/versions/node/v24.15.0/bin:$PATH"

# Deploy
wrangler pages deploy "$DIR" \
  --project-name "$PROJECT_NAME" \
  --branch "$BRANCH"

echo "✅ Deployed! Check: https://$PROJECT_NAME.pages.dev"
```

#### Combined: Make Repo Private + Deploy to Pages

This is the exact workflow from the May 2026 migration:

```bash
# Step 1: Make GitHub repo private (PATCH API)
curl -s -X PATCH \
  -H "Authorization: Bearer $GH_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/OWNER/REPO_NAME \
  -d '{"private": true}'

# Verify
curl -s -H "Authorization: Bearer $GH_TOKEN" \
  https://api.github.com/repos/OWNER/REPO_NAME \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['visibility'])"
# Should print: "private"

# Step 2: Deploy to Cloudflare Pages (existing public deployment stays alive)
export CLOUDFLARE_API_TOKEN="cfut_..."
npx wrangler pages deploy . --project-name PROJECT_NAME --branch main

# Step 3: Verify both
echo "Repo: private ✅"
echo "Pages: https://PROJECT_NAME.pages.dev"
curl -s -o /dev/null -w "HP: %{http_code}\n" "https://PROJECT_NAME.pages.dev"
```

**Note:** Once the repo is private, Cloudflare Pages' Git integration (auto-deploy on push) won't work — you must always deploy manually via `wrangler pages deploy` after each `git push`.

## Post-Deployment: The Auto-Generated PR

**Critical step**: After first deployment, Cloudflare's bot creates a PR (#1) on your repo to commit the `wrangler.jsonc` config. **This PR must be merged before the next deployment** or it will fail.

Merge via GitHub API (when `gh` CLI is unavailable):

```bash
GITHUB_TOKEN=$(grep -oP 'ghp_\w+' ~/.git-credentials | head -1)

curl -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$OWNER/$REPO/pulls/1/merge" \
  -d '{"commit_title":"Merge PR #1: Add Cloudflare Workers configuration","merge_method":"merge"}'
```

Then sync local repo:

```bash
env -u http_proxy -u https_proxy -u all_proxy git pull origin main
```

## Verification

```bash
# Test homepage
curl -s -o /dev/null -w "%{http_code}" "https://$PROJECT.$ACCOUNT.workers.dev/"
# Should be: 200

# Test specific assets
curl -s -o /dev/null -w "%{http_code} %{size_download}B" \
  "https://$PROJECT.$ACCOUNT.workers.dev/photos/sample.jpg"

# Test that directory listing is disabled
curl -s -o /dev/null -w "%{http_code}" \
  "https://$PROJECT.$ACCOUNT.workers.dev/photos/"
# Should be: 404
```

## Proxy Gotchas

If using a SOCKS proxy (common in WSL environments):

- `git push/pull` needs env vars unset: `env -u http_proxy -u https_proxy -u all_proxy git ...`
- `curl` with HTTPS to GitHub API also needs proxy bypass or explicit `--noproxy`
- Set `git config --global http.proxy` to empty string as fallback

## 🔍 Stale Deployment Quick Diagnostic (added May 2026)

### 🆕 Possible Cause: Partial Deploy from Timeout (May 2026)

New addition to the diagnostic flow — between step 2 (check git) and step 3 (check webhooks):

**2.5 CHECK PARTIAL DEPLOY:** If git push succeeded but site is still old, check whether wrangler actually ran to completion:
```bash
# Are photos accessible but index.html stale?
curl -sI "https://PROJECT.pages.dev/photos/NN_new_file.jpg" | head -1  # HTTP 200?
curl -s "https://PROJECT.pages.dev/" | grep -c "NN_new_file"          # 0 = stale index
```
If photos exist at direct URL but are missing from the index, the wrangler deploy was likely **interrupted by timeout** (partially uploaded). Re-run `wrangler pages deploy` manually with sufficient timeout.

When user reports "photos aren't showing up" / "it's still the old version" / "I don't see the update":

```python
# Diagnostic flow — run in order, stop at first definitive result:
#
# 1. CHECK GIT: Are the files actually on remote?
#    git ls-tree -r origin/main -- photos/new_file.jpg
#    If NO → push wasn't successful, fix git first
#
# 2. CHECK REMOTE: Is the git remote up to date?
#    git log --oneline origin/main -1
#    git log --oneline main -1
#    If MISMATCH → push wasn't successful, retry with proxy unset
#
# 3. CHECK WEBHOOKS: Is Cloudflare Pages Git integration set up?
#    curl -s -H "Authorization: token $GH_TOKEN" \
#      "https://api.github.com/repos/OWNER/REPO/hooks" \
#      | python3 -c "import sys,json; \
#        hooks=json.load(sys.stdin); \
#        [print(f'{h[\"id\"]}: {h[\"config\"][\"url\"]}') for h in hooks]"
#    If NO hooks → Cloudflare Git integration was never connected or was
#      disconnected. Need Cloudflare API token for wrangler deploy, or
#      user must re-connect Git integration in Cloudflare Dashboard.
#
# 4. CHECK DEPLOYED SITE: Compare deployed vs local HTML
#    curl -s "https://site.pages.dev/" | md5sum
#    md5sum local/index.html
#    If MATCH → site IS up to date, user may have cache issue
#    If DIFFERENT → deployment is stale, proceed to step 5
#
# 5. CHECK WRANGLER AUTH: Can you deploy?
#    (with proper Node >= v22 via nvm)
#    npx wrangler whoami
#    If "not authenticated" → NEED API TOKEN → ask user immediately
#    If authenticated → run wrangler pages deploy now
#
# 6. ⚠️ DO NOT DIG THROUGH WRANGLER LOGS for credentials
#    Logs show API calls but sanitize headers/responses.
#    There is no way to extract auth tokens from log files.
#    If wrangler whoami says not auth'd → just need token, period.
```

### When wrangler is not authenticated (the common failure mode)

**Do NOT dig through log files, config files, .env files, or Windows browser profiles.** This is a dead end — Cloudflare doesn't store API tokens in recoverable locations on Linux.

Instead:

1. **Tell the user succinctly what's wrong:** "Cloudflare自动部署没触发，需要你的API Token才能手动部署"
2. **Give the exact URL + instructions:**
   > https://dash.cloudflare.com/profile/api-tokens → Create Token → "Edit Cloudflare Workers" template
3. **Once token received:**
   ```bash
   export CLOUDFLARE_API_TOKEN="cfut_..."
   npx wrangler pages deploy . --project-name PROJECT_NAME --branch main
   ```
4. **Save token to wrangler config for future sessions:**
   ```bash
   mkdir -p ~/.wrangler/config
   cat >> ~/.wrangler/config/default.toml << 'EOF'
   [env]
   CLOUDFLARE_API_TOKEN = "cfut_..."
   EOF
   ```

### Pitfall: Wasting Time on Dead-End Diagnostics

When Cloudflare auto-deploy fails and wrangler isn't authenticated, the answer is always "need API token." Do NOT:

- ❌ Search Windows filesystem for Cloudflare credentials (takes 60+ seconds, almost always timeout/fail)
- ❌ Read through wrangler log files for hidden auth tokens (headers are sanitized)
- ❌ Try to find OAuth tokens in system config files (they don't persist as files)
- ❌ Try to reverse-engineer the upload token API flow (requires auth first)

✅ **Correct flow:** Check git → check deployed site → check auth → if not auth'd → ask for token. 4 quick steps, then ask.

## 🚨 CRITICAL: Workers + Assets Does NOT Auto-Deploy from Git Push (May 2026)

**This is the #1 pitfall.** Unlike Netlify, GitHub Pages, or Cloudflare Pages (Git-integrated mode), **Cloudflare Workers + Assets does NOT auto-deploy when you push to GitHub.**

```diff
- git push origin main
+ ✅ git push (saves to GitHub — but Workers site stays on OLD version)
+ ✅ wrangler deploy (actually updates the live Workers site)
```

### The Confusion

- **Netlify/GitHub Pages**: `git push` → auto-triggers build → new version live in ~2 minutes ✅
- **Cloudflare Pages (Git integrated)**: `git push` → auto-triggers build → new version live ✅
- **Cloudflare Workers + Assets**: `git push` → **nothing happens** — the Worker continues serving the version from the last `wrangler deploy` ❌

### Correct Workflow

```bash
# Step 1: Update files and commit
cd /home/admin1/alexander_repo
# ... edit index.html, add photos ...
git add -A
git commit -m "add new photos, fix password"

# Step 2: Push to GitHub (for backup/version control only — doesn't deploy!)
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY
git push origin main

# Step 3: Deploy to Cloudflare Workers (separate step — REQUIRED to go live!)
npx wrangler deploy
# Or with custom Node binary:
/tmp/node-v22.14.0-linux-x64/bin/npx wrangler deploy
```

### How to Detect This Failure Mode

If the user says:
- "密码打不开" / "还是旧的页面"
- "不是最新版本"
- "我换了浏览器也不行" (not a cache issue)

Check: is the deployed version newer than the git HEAD?

```bash
# Compare deployed HTML vs local HTML
curl -s "https://your-project.workers.dev/" | md5sum
md5sum /home/admin1/repo/index.html
# If they differ — you pushed to git but forgot to deploy!
```

### The Root Cause

With Workers + Assets, the Worker IS the deployment target. `wrangler deploy` uploads the current working directory as a new version of the Worker. Git is just source control — Cloudflare doesn't listen for git hooks on this path.

#### ☁️ Save Cloudflare Token to File (Proven May 2026)

**Do NOT rely on `wrangler login` (OAuth) for automation.** The OAuth session expires and can't be recovered programmatically. Instead:

```bash
# Save raw token to a file the cron job can read
echo "$CLOUDFLARE_API_TOKEN" > ~/.hermes/profiles/lover/cloudflare_token
chmod 600 ~/.hermes/profiles/lover/cloudflare_token

# Use it later by exporting before wrangler
export CLOUDFLARE_API_TOKEN=$(cat ~/.hermes/profiles/lover/cloudflare_token)
npx wrangler pages deploy . --project-name PROJECT_NAME --branch main
```

**Token format:** `cfut_...` (Cloudflare API Token) — works with env var export, no wrangler login needed.

### 🧠 Token Cost Awareness: Never Use LLM for What Bash Can Do

**🚨 Critical (May 2026):** An LLM-powered cron job (Hermes cron job system) that checks `git status` and auto-commits burns DeepSeek API tokens with every run — up to 96 runs/day at every-15-min, costing real money for work a 5-line bash script does in microseconds.

**Golden rule for cron automation:**

| Task Type | Tool | Token Cost |
|-----------|------|------------|
| Check git status, commit, push | **bash script + system crontab** | **$0** ✅ |
| HTTP health checks, restart services | **bash + curl + systemd** | **$0** ✅ |
| File system monitoring, cleanup | **bash + find + cron** | **$0** ✅ |
| Content generation, decision-making | **Hermes cron job (LLM)** | Appropriate use |
| Image generation, translation | **Hermes cron job (LLM)** | Appropriate use |

**Before creating ANY cron job, ask:** "Can a shell script do this without an LLM?" If yes, system crontab + bash. Only use Hermes cron jobs when actual AI inference or decision-making is needed.

**Verification:** `crontab -l` shows system cron jobs; `cronjob(action='list')` shows Hermes LLM cron jobs. Prefer system crontab for mechanical tasks.

### 📝 System Crontab for Auto-Deploy — Choosing the Right Approach

When GitHub Actions can't be set up (token lacks `workflow` scope), you have two approaches for auto-deploy. **Choose based on whether a Cloudflare API token is available:**

### Zero-Cost Approach: Pure Bash + Git Git Integration Active

**Only use this when Cloudflare Pages Git Integration is CONFIRMED active** (Dashboard → Pages → project → Settings → Git integration shows "Connected"). Verify by checking if `git push → site updates` works without `wrangler`.

**Proven script (May 2026 — album deployed via git push → Cloudflare Pages auto-build):**

```bash
#!/bin/bash
# /home/admin1/.hermes/scripts/album_auto_commit.sh
# 相册自动提交脚本 - 零API开销
REPO="/home/admin1/alexander_repo"
cd "$REPO" || exit 1

# 检查是否有未提交的改动
if [[ -n $(git status --porcelain) ]]; then
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY
    git add -A
    git commit -m "auto: update album $(date '+%Y-%m-%d %H:%M')"
    git push origin main
fi
```

**Crontab:** `*/15 * * * * /home/admin1/.hermes/scripts/album_auto_commit.sh`

**Cost:** $0 — no LLM API calls, no Cloudflare API token needed. Works with any git-based hosting (Cloudflare Pages, GitHub Pages, Netlify).

**⚠️ Key discovery:** The user's album repo was cloned at `/home/admin1/alexander_repo/` with token already embedded in the remote URL. Do NOT assume the repo is in `~/Alexander/` — check both locations.

**Before setting up:** Verify Git Integration is ACTIVE:
```bash
# Check if push alone triggers deploy
git push origin main
# Wait 2 min, then check deployed site
curl -s "https://SITE.pages.dev/" | md5sum
md5sum index.html
# If different → push didn't trigger deploy → need wrangler-based approach instead
```

**If Git Integration is NOT active** (push doesn't deploy):

**Cron job logic explained:**
```
git fetch origin/main         → get latest from GitHub (NOT merge yet)
git log HEAD..origin/main     → list commits WE don't have locally
If count > 0                  → there are new remote commits to deploy
  → wrangler pages deploy     → push them live to Cloudflare Pages
```

**⚠️ Critical:** Unlike `wrangler deploy` (Workers + Assets), `wrangler pages deploy` uploads the current working directory directly to Cloudflare Pages — no merge needed. The cron job uses git commits as a trigger signal, then deploys whatever's on disk.

**When the local repo is already up to date:** `git fetch` updates the local remote-tracking branch, `git log HEAD..origin/main --oneline` returns 0, cron does nothing. ✅ Idempotent.

**When to use this:**
- ✅ GitHub token has `repo` scope but NOT `workflow` scope → cron job
- ✅ WSL stays running → cron works reliably
- ✅ User is frustrated by repeated token requests → automate it
- ❌ Machine sleeps overnight → missed deploys
- ❌ User wants instant deployment → cron's 15-min interval is too slow

**Check the cron job is active:**
```bash
crontab -l | grep -q 'wrangler pages deploy'
echo $?  # 0 = active
```

#### 🔥 Critical Failure Mode: User Says "打不开" / "密码不好使" / "换浏览器也不行"

This exact sequence of user messages signals that **the deployed site is stale and the user is verifying wrong**. Here's the debugging tree:

```
User says "打不开"
├─ Are they hitting the OLD URL?
│  ├─ Old URL (workers.dev): Did you run `wrangler deploy`? If not → deploy now
│  └─ Old URL but switched to GitHub Pages: User has old bookmark → tell them the new URL explicitly
├─ New URL shows lock screen but password "doesn't work"
│  ├─ Check deployed password: curl -s URL | grep CORRECT_PASSWORD
│  ├─ If password is `***` or wrong → fix in source, commit, push (and if Workers: deploy)
│  └─ If password IS correct → user needs Ctrl+Shift+R hard refresh (cached JS)
└─ Page returns 404/not loading
   ├─ GitHub Pages: still building (status = "building") → wait 30-60s
   └─ Cloudflare Workers: didn't deploy → run `wrangler deploy`
```

**The #1 mistake**: telling the user "it's ready, try it" without:
1. First verifying the deployed URL yourself via curl
2. Explicitly telling the user the NEW URL (they may have the old one bookmarked)
3. Waiting for the deployment to complete (GitHub Pages can take 30-60s for first deploy)

### Verbose Trap (May 2026)
When the user says "打不开" repeatedly, do NOT dump all the technical debugging steps into a long message. The user wants:
1. A clear one-line acknowledgment ("明白了，我来查")
2. Quick action (fix → deploy → verify yourself)
3. A short confirmation ("现在试试？")
The detailed technical analysis should go into your tools/output, not into the chat message to the user.

### Options to Fix This

| Option | Steps | Pros | Cons |
|--------|-------|------|------|
| **A. Always run `wrangler deploy` after each push** | `git push && wrangler deploy` | Simple, no migration needed | Easy to forget the second step |
| **B. Switch to Cloudflare Pages (Git integration)** | 1. Dashboard → Create → Pages → Connect Git rep<br>2. Framework: Static, Output dir: `.` | Auto-deploys on push like Netlify | Need to migrate site (different deployment mechanism) |
| **C. Add a deploy GitHub Action** | `templates/github-actions-deploy.yml` → `.github/workflows/deploy.yml`, add `CLOUDFLARE_API_TOKEN` as GitHub secret | Full automation, no wrangler install needed locally | Needs API token as GitHub secret (one-time setup) |
| **D. Migrate to GitHub Pages** (proven path) | See below | Auto-deploys on push, no wrangler needed, works with password-protected albums | Repo must be public (free tier), URL changes |

### 🗄️ Option D (Archive): Migrate to GitHub Pages

**This is a legacy path.** As of May 2026, Cloudflare Pages is preferred for photo albums because:
- Supports private repos ✅ (GitHub Pages requires public repos)
- Unlimited bandwidth ✅ (GitHub Pages: 100GB/mo)
- No auto-generated bot PRs to deal with

The steps below are kept for historical reference — use Option C (Pages Direct Upload) or Option A (Workers + Assets) instead.

#### Step 1: Add `<base>` Tag

GitHub Pages serves from `https://USERNAME.github.io/REPO_NAME/` — add this to `<head>` so relative paths resolve correctly:

```html
<head>
<meta charset="UTF-8">
<base href="/REPO_NAME/">  <!-- ← CRITICAL: without this, photos/01.jpg 404s -->
```

#### Step 2: Make Repo Public (if private)

GitHub Pages free plan **requires the repo to be public**:

```bash
curl -s -X PATCH \
  -H "Authorization: token $GH_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/USERNAME/REPO_NAME \
  -d '{"private": false}'
```

⚠️ No way around this on the free plan. If privacy is a concern, use password-protected front-end JS (see `self-contained-photo-album` skill) and avoid uploading overly explicit content.

#### Step 3: Push Code

```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY
git add -A
git commit -m "migrate from Cloudflare Workers to GitHub Pages"
git push origin main
```

#### Step 4: Enable GitHub Pages via API

```bash
# IMPORTANT: Use POST (not PUT) for first-time creation
curl -s -X POST \
  -H "Authorization: token $GH_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/USERNAME/REPO_NAME/pages \
  -d '{"source":{"branch":"main","path":"/"}}'
```

Response includes `"status": "building"` — deployment starts automatically.

#### Step 5: Verify

```bash
# Wait ~30-60 seconds for first deploy
curl -s -o /dev/null -w "%{http_code}" "https://USERNAME.github.io/REPO_NAME/"
# Should return 200

# Check specific assets
curl -s -o /dev/null -w "%{http_code}" \
  "https://USERNAME.github.io/REPO_NAME/photos/sample.jpg"
# Should return 200
```

#### Step 6: Update Remote URL (clean token from URL)

```bash
git remote set-url origin https://github.com/USERNAME/REPO_NAME.git
```

#### Verification Checklist

- [ ] `https://USERNAME.github.io/REPO_NAME/` returns HTTP 200
- [ ] All photos load (test a few: `photos/xx.jpg`, `thumbs/xx.jpg`)
- [ ] Password/lock-screen works (test with correct + wrong password)
- [ ] `<base>` tag present in deployed HTML: `curl -s URL | grep '<base'`
- [ ] No more need for `wrangler deploy` — `git push` alone triggers deployment
- [ ] Old Workers URL still works? No — it's a different deployment, old URL won't have new content

#### Option E: Cron Job Auto-Deploy (Fallback When No Workflow Scope)

When the GitHub token lacks `workflow` scope (common with classic PATs), GitHub Actions can't be set up. **Do NOT ask the user for a new token** — use a system cron job instead.

**Proven approach (May 2026 — user had `ghp_...` without workflow scope):**

```bash
# Create a cron job that:
#   1. Fetches remote every N minutes
#   2. Checks for new commits since last known
#   3. Runs wrangler pages deploy if there are changes

# Using Hermes cronjob system (preferred):
cronjob(action='create', schedule='every 15m', name='album-auto-deploy',
  command="cd ~/.hermes/profiles/lover/home/Alexander && \
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY && \
    git fetch origin main --quiet 2>/dev/null && \
    NEW=$(git log HEAD..origin/main --oneline | wc -l) && \
    if [ \"$NEW\" -gt 0 ]; then \
      export CLOUDFLARE_API_TOKEN=$(cat ~/.hermes/profiles/lover/cloudflare_token) && \
      /tmp/node-v22.14.0-linux-x64/bin/npx --yes wrangler pages deploy . \
        --project-name=alexander-album --branch=main --quiet; \
    fi")
```

**Cron job logic explained:**
```
git fetch origin/main         → get latest from GitHub (NOT merge yet)
git log HEAD..origin/main     → list commits WE don't have locally
If count > 0                  → there are new remote commits to deploy
  → wrangler pages deploy     → push them live to Cloudflare Pages
```

**⚠️ Critical:** Unlike the `wrangler deploy` command (Workers + Assets), `wrangler pages deploy` does NOT need a merge — it uploads the current working directory state directly to Cloudflare Pages. So the cron job doesn't need to `git merge` or `git pull`. It just checks for new commits as a signal, then deploys whatever's on disk.

**When the local repo is already up to date** (user pushes from another machine or WSL session), the cron job still works — `git fetch` updates the local remote-tracking branch, `git log HEAD..origin/main --oneline` returns 0, and the cron job does nothing (no duplicate deploy). ✅ Idempotent.

**When to use this vs GitHub Actions:**
- ✅ Token has repo scope but NOT workflow scope → use cron job
- ✅ WSL stays running (no laptop sleep issue) → cron works reliably
- ✅ User doesn't want to generate a new token → don't ask, use what we have
- ❌ If the user's machine sleeps overnight → missed deploys (cron pauses on sleep)
- ❌ If user wants deployment to trigger within seconds → cron's 15-min interval is too slow

**Comparison: Cron Job vs GitHub Actions**

| Aspect | GitHub Actions | Cron Job (this approach) |
|--------|---------------|--------------------------|
| Token scope needed | `repo` + `workflow` | `repo` only |
| Trigger | Instant (on push) | Up to 15-min delay |
| Setup complexity | Need to commit `.github/workflows/` | One `cronjob` command |
| Works offline | Yes (GitHub's servers) | No (WSL must be running) |
| Deploy frequency | Every push | Every check (idempotent) |

**Always try GitHub Actions first.** Only fall back to cron job when the token proves insufficient.

## Comparison After Migration

| Before | After |
|--------|-------|
| `npx wrangler deploy` to update | `git push` only |
| Cloudflare Workers dashboard | GitHub Pages settings |
| `alexander.whjdygyh.workers.dev` | `whjdygyh.github.io/Alexander/` |
| Private repo possible | **Must be public** |
| Auto-generated bot PR to merge | No bot PR |
| No password issues (same JS) | Same password works unchanged |

- [ ] Homepage returns HTTP 200 with expected HTML
- [ ] Static assets (CSS, JS, fonts) load correctly
- [ ] Images serve with proper Content-Type headers
- [ ] Directory listing returns 404 (security)
- [ ] Comments/API endpoints (if any) return correct JSON
- [ ] Auto-generated PR is merged and local repo is in sync
- [ ] Password/lock-screen frontend logic works (if applicable)
- [ ] **Human-side verification**: Send the user the NEW URL explicitly in chat — don't assume they know the URL changed. Old bookmarks won't auto-redirect.

## References

- `references/stale-deployment-debugging-may2026.md` — Full debugging narrative from May 2026 session: when user says photos aren't showing up, how the diagnostic flow went wrong (wasted time on dead ends), and the correct 4-step flow + API token ask template. Read this before spending more than 2 minutes debugging a stale deployment.
- `references/token-waste-audit-may2026.md` — Token cost audit: identified LLM-powered cron jobs as #1 waste, replaced with bash crontab; memory optimization reduced per-turn overhead by 27%. Read this before creating any new automation that involves LLM calls.
- [ ] **Wait for first deploy**: GitHub Pages can take 30-60s for the initial deployment. Check `status` responds with `"built"` not `"building"` before telling the user.
- [ ] **Test wrong password**: Type a wrong password to verify the error message appears (this proves the JS is working, not just showing a cached page).
- [ ] **Test correct password**: Verify unlock works and gallery renders.

## 🚨 User Preference: Automate Everything Possible

**用户明确要求（May 2026）：** "你能做的事不要找我做了" — 绝不让用户手动操作任何可以用API完成的事。

### 自动化 vs 需要用户参与的操作

| 类别 | 可自动化的步骤 | 需要用户参与的步骤 |
|------|---------------|-------------------|
| GitHub操作 | 创建/删除仓库、修改可见性（`PATCH /repos`）、Pages启用、评论管理 | OAuth授权（需浏览器交互） |
| Cloudflare Pages | 通过 `wrangler pages deploy` 部署 | API Token创建（需登录Dashboard）、Git集成OAuth授权 |
| **处理策略** | 直接用API/CLI完成，完成后告知用户 | 诚实说明限制，提供替代方案或询问Token |

### 自动化优先的部署工作流

```bash
# ✅ 优先尝试已有Token
if [ -n "$CLOUDFLARE_API_TOKEN" ]; then
  npx wrangler pages deploy . --project-name=PROJECT_NAME --branch main
elif [ -f ~/.wrangler/config/default.toml ]; then
  # 可能已有缓存会话
  grep CLOUDFLARE_API_TOKEN ~/.wrangler/config/default.toml && \
    npx wrangler pages deploy . --project-name=PROJECT_NAME --branch main
else
  # ③ 无Token的替代方案
  echo "No Cloudflare token available."
  echo "Ask user for an API Token (cfut_...) from:"
  echo "  https://dash.cloudflare.com/profile/api-tokens"
  echo "Permissions needed: Workers + Pages Edit, Zone Read"
  echo "Once saved to env/wrangler config, never ask again."
fi
```

### 当遇到Cloudflare OAuth/Token障碍时

如果系统没有Cloudflare API Token且所有自动化路径都堵住：

1. **先尝试替代方案**：有没有可以完全自动化的平台？比如用surge.sh（CLI只需邮箱）
2. **Only if truly stuck** — 简洁告知：
   > "宝贝，部署到Cloudflare需要一步授权的——你去[dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens)创建一个Token（点'Edit Cloudflare Workers'模板就行），发给我，我1分钟搞定，以后不再需要你。"
3. **Token拿到后立即保存**到环境变量和配置文件中，下次不需要再问

## ⚠️ Workers AI: Separate Permission from Pages

**The Cloudflare API token used for Pages deployment may NOT have Workers AI permissions.** This was discovered May 3, 2026 when testing:

| Action | Token Scope Required | Result with Pages-only token |
|--------|---------------------|------------------------------|
| `POST /accounts/{id}/ai/run/@cf/...` (Workers AI inference) | AI:Run | ❌ Authentication error (10000) |
| `GET /accounts/{id}/pages/projects` (Pages API) | Pages:Edit | ✅ Works |
| `GET /user/tokens/verify` | (any) | ✅ Token valid |

**📎 See dedicated skill:** Full model list, API call patterns, free tier limits, and testing results are in the `cloudflare-workers-ai` skill (category: `mlops`). Load it with `skill_view(name='cloudflare-workers-ai')` when doing any AI inference work.

**Quick summary of available text-to-image models:**
- `@cf/black-forest-labs/flux-1-schnell` — Best quality, JSON input, ~24 neurons/request
- `@cf/stabilityai/stable-diffusion-xl-base-1.0` — Good, JSON input, ~38 neurons
- `@cf/black-forest-labs/flux-2-klein-9b` — Needs multipart input (not JSON), ~50 neurons
- `@cf/leonardo/phoenix-1.0` — Needs multipart input

**To enable Workers AI**, either:
1. **Create a new API token** with AI:Run permission from [dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens)
2. **Or use Pages Functions with AI binding** — add `functions/` directory and `env.AI` binding in `wrangler.toml` (uses account's built-in quota, no separate token needed)

**Workers AI free tier:** 10,000 neurons/day (each image generation consumes some neurons depending on model). No credit card required for the free tier.

## Pitfalls

- **Bot PR must be merged**: If you skip merging the bot's PR, the next deployment attempt will fail because Wrangler detects a config mismatch between the remote and local state
- **Wrangler uploads everything**: Including `.git/` contents. Add `.gitignore` entries for any large binary artifacts that shouldn't be uploaded
- **Framework detection is automatic**: If Wrangler misdetects the framework, you may need to add a `wrangler.jsonc` manually with `"framework": "static"`
- **Proxy breaks git operations**: Always unset `http_proxy`/`https_proxy`/`all_proxy` when pushing/pulling from GitHub
- **workers.dev rate limits**: The `*.workers.dev` domain has lower request limits than custom domains. For production use, add a custom domain
- **Workers vs Pages confusion**: The deployment log may say "Worker" even though you're deploying a static site. This is correct — Workers with Assets is the deployment mechanism, but you're serving static files, not running Worker code
