---
name: webhook-subscriptions
description: "Webhook subscriptions: event-driven agent runs."
version: 1.1.0
metadata:
  hermes:
    tags: [webhook, events, automation, integrations, notifications, push]
---

# Webhook Subscriptions

Create dynamic webhook subscriptions so external services (GitHub, GitLab, Stripe, CI/CD, IoT sensors, monitoring tools) can trigger Hermes agent runs by POSTing events to a URL.

## Setup (Required First)

The webhook platform must be enabled before subscriptions can be created. Check with:
```bash
hermes webhook list
```

If it says "Webhook platform is not enabled", set it up:

### Option 1: Setup wizard
```bash
hermes gateway setup
```
Follow the prompts to enable webhooks, set the port, and set a global HMAC secret.
### Option 2: Manual config

Add to `~/.hermes/config.yaml` (⚠️ **profile-level config won't work** — the gateway reads the `platforms:` key only from the main config at `~/.hermes/config.yaml`, not from `<profile>/config.yaml`):

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      host: "0.0.0.0"
      port: 8644
      secret: "generate-a-strong-secret-here"
```

### Option 3: Environment variables
Add to `~/.hermes/.env`:
```bash
WEBHOOK_ENABLED=true
WEBHOOK_PORT=8644
WEBHOOK_SECRET=generate-a-strong-secret-here
```

After configuration, start (or restart) the gateway:
```bash
hermes gateway run
# Or if using systemd:
systemctl --user restart hermes-gateway
```

Verify it's running:
```bash
curl http://localhost:8644/health
```

## Commands

All management is via the `hermes webhook` CLI command:

### Create a subscription
```bash
hermes webhook subscribe <name> \
  --prompt "Prompt template with {payload.fields}" \
  --events "event1,event2" \
  --description "What this does" \
  --skills "skill1,skill2" \
  --deliver telegram \
  --deliver-chat-id "12345" \
  --secret "optional-custom-secret"
```

Returns the webhook URL and HMAC secret. The user configures their service to POST to that URL.

### List subscriptions
```bash
hermes webhook list
```

### Remove a subscription
```bash
hermes webhook remove <name>
```

### Test a subscription
```bash
hermes webhook test <name>
hermes webhook test <name> --payload '{"key": "value"}'
```

## Prompt Templates

Prompts support `{dot.notation}` for accessing nested payload fields:

- `{issue.title}` — GitHub issue title
- `{pull_request.user.login}` — PR author
- `{data.object.amount}` — Stripe payment amount
- `{sensor.temperature}` — IoT sensor reading

If no prompt is specified, the full JSON payload is dumped into the agent prompt.

## Common Patterns

### GitHub: new issues
```bash
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "New GitHub issue #{issue.number}: {issue.title}\n\nAction: {action}\nAuthor: {issue.user.login}\nBody:\n{issue.body}\n\nPlease triage this issue." \
  --deliver telegram \
  --deliver-chat-id "-100123456789"
```

Then in GitHub repo Settings → Webhooks → Add webhook:
- Payload URL: the returned webhook_url
- Content type: application/json
- Secret: the returned secret
- Events: "Issues"

### GitHub: PR reviews
```bash
hermes webhook subscribe github-prs \
  --events "pull_request" \
  --prompt "PR #{pull_request.number} {action}: {pull_request.title}\nBy: {pull_request.user.login}\nBranch: {pull_request.head.ref}\n\n{pull_request.body}" \
  --skills "github-code-review" \
  --deliver github_comment
```

### Stripe: payment events
```bash
hermes webhook subscribe stripe-payments \
  --events "payment_intent.succeeded,payment_intent.payment_failed" \
  --prompt "Payment {data.object.status}: {data.object.amount} cents from {data.object.receipt_email}" \
  --deliver telegram \
  --deliver-chat-id "-100123456789"
```

### CI/CD: build notifications
```bash
hermes webhook subscribe ci-builds \
  --events "pipeline" \
  --prompt "Build {object_attributes.status} on {project.name} branch {object_attributes.ref}\nCommit: {commit.message}" \
  --deliver discord \
  --deliver-chat-id "1234567890"
```

### Generic monitoring alert
```bash
hermes webhook subscribe alerts \
  --prompt "Alert: {alert.name}\nSeverity: {alert.severity}\nMessage: {alert.message}\n\nPlease investigate and suggest remediation." \
  --deliver origin
```

### Feishu / Lark: file comment events

Feishu (飞书) event subscription setup — e.g., monitoring file comments in a cloud drive folder:

1. **In Feishu Developer Console** (`open.feishu.cn`):
   - Go to your app → **事件与回调** → **事件订阅** (NOT 回调订阅 — that's for card card interactions — internal interactions)
   - Click 添加事件 → search for comment-related events
   - ✅ Actual event name (verified May 2026): **`drive.notice.comment_add_v1`** — NOT `drive.file.comment_added`. File comment events live under the `drive.notice` namespace, not `drive.file`
   - If you add an event and publish a new version, the URL field can be left empty initially

2. **Public URL challenge**: Feishu sends a URL verification challenge when you first configure a Request URL. Your endpoint must respond with `{"challenge": "<same_value>"}` (HTTP 200, Content-Type: application/json). See the `references/feishu-webhook-receiver.py` file for a minimal standalone server that handles this.

3. **Getting a public URL** when inbound ports are firewalled:
   - **cloudflared quick tunnel** — `cloudflared tunnel --url http://localhost:<port>` allows a trycloudflare.com subdomain without a Cloudflare account
   - **⚠️ Pitfall: cert.pem missing** — cloudflared expects `~/.cloudflared/cert.pem`. Workaround: `cloudflared tunnel --url http://localhost:<port> --origincert /dev/null` to skip certificate validation. However, trycloudflare quick tunnels have no uptime guarantee and may be unreliable.
   - **Cloudflare Workers** — deploy a Worker at `*.workers.dev` that echoes events back. Requires your API token to have `Workers Scripts:Edit` scope. A token with only `Workers AI:Run` scope will pass `verify` (success: true) but return `Authentication error (10000)` on workers endpoints.
   - **SSH tunnels** (serveo.net, localhost.run) — often blocked by the provider's egress firewall. Test before relying on this path.
   - **ngrok / bore** — alternative tunnels if available

   ⚠️ **Critical verification step**: Before setting up a tunnel, confirm your webhook receiver is listening AND test external accessibility:
   ```bash
   curl http://localhost:<port>/
   # Then from outside:
   curl -m 3 http://<public_ip>:<port>/   # if this fails, all ports are firewalled
   ```

4. **Known Feishu Drive event names** (verified against Feishu event subscription search, May 2026):
   - `drive.notice.comment_add_v1` — new comment or reply on a document (was the one we needed)
   - `drive.file.created_in_folder_v1` — file created in a folder
   - `drive.file.edit_v1` — file edited
   - `drive.file.bitable_record_changed_v1` — bitable record changed
   - `drive.file.bitable_field_changed_v1` — bitable field changed
   - `drive.file.deleted_v1` — file permanently deleted
   - `drive.file.trashed_v1` — file moved to trash
   - `drive.file.read_v1` — file read
   - `drive.file.download_v1` — file downloaded
   - `drive.file.permission_member_added_v1` — collaborator added
   - `drive.file.permission_member_removed_v1` — collaborator removed
   - `drive.file.permission_member_applied_v1` — collaborator access request
   - `drive.file.title_updated_v1` — file title updated
   - `drive.notice.comment_add_v1` lives under **drive.notice** namespace, not drive.file

5. **Token permissions**: If using Cloudflare Workers API, your token needs `Workers Scripts:Edit` permission. A token with only `Workers AI:Run` scope will pass API token verification (`verify` returns success: true with empty policies) but fail on any Workers management endpoint with error 10000. You can test this:
   ```bash
   curl -X GET "https://api.cloudflare.com/client/v4/accounts/<ACID>/workers/scripts" \
     -H "Authorization: Bearer <token>"
   ```

6. **Fallback when no public URL is possible**: Use polling instead of push. A cron job can periodically call the Feishu Drive API to check for new comments on files in a folder. This avoids the need for tunnels, Workers, or any public URL at all. Delay is measured in minutes rather than real-time. See `references/feishu-comment-polling.md` for implementation.

### Direct delivery (no agent, zero LLM cost)

For use cases where you just want to push a notification through to a user's chat — no reasoning, no agent loop — add `--deliver-only`. The rendered `--prompt` template becomes the literal message body and is dispatched directly to the target adapter.

Use this for:
- External service push notifications (Supabase/Firebase webhooks → Telegram)
- Monitoring alerts that should forward verbatim
- Inter-agent pings where one agent is telling another agent's user something
- Any webhook where an LLM round trip would be wasted effort

```bash
hermes webhook subscribe antenna-matches \
  --deliver telegram \
  --deliver-chat-id "123456789" \
  --deliver-only \
  --prompt "🎉 New match: {match.user_name} matched with you!" \
  --description "Antenna match notifications"
```

The POST returns `200 OK` on successful delivery, `502` on target failure — so upstream services can retry intelligently. HMAC auth, rate limits, and idempotency still apply.

Requires `--deliver` to be a real target (telegram, discord, slack, github_comment, etc.) — `--deliver log` is rejected because log-only direct delivery is pointless.

## Security

- Each subscription gets an auto-generated HMAC-SHA256 secret (or provide your own with `--secret`)
- The webhook adapter validates signatures on every incoming POST
- Static routes from config.yaml cannot be overwritten by dynamic subscriptions
- Subscriptions persist to `~/.hermes/webhook_subscriptions.json`

## How It Works

1. `hermes webhook subscribe` writes to `~/.hermes/webhook_subscriptions.json`
2. The webhook adapter hot-reloads this file on each incoming request (mtime-gated, negligible overhead)
3. When a POST arrives matching a route, the adapter formats the prompt and triggers an agent run
4. The agent's response is delivered to the configured target (Telegram, Discord, GitHub comment, etc.)

## Troubleshooting

If webhooks aren't working:

1. **Is the gateway running?** Check with `systemctl --user status hermes-gateway` or `ps aux | grep gateway`
2. **Is the webhook server listening?** `curl http://localhost:8644/health` should return `{"status": "ok"}`
3. **Check gateway logs:** `grep webhook ~/.hermes/logs/gateway.log | tail -20`
4. **Signature mismatch?** Verify the secret in your service matches the one from `hermes webhook list`. GitHub sends `X-Hub-Signature-256`, GitLab sends `X-Gitlab-Token`.
5. **Firewall/NAT?** The webhook URL must be reachable from the service. For local/WSL/homelab setups, use a tunnel:
   - `cloudflared tunnel --url http://localhost:<port>` (requires `cloudflared tunnel login` first — generates a cert.pem)
   - ngrok, bore, or SSH reverse tunnel
   - ⚠️ **Pitfall: cloudflared needs login first** — running a quick tunnel without a prior `cloudflared login` will fail with "Cannot determine default origin certificate path". Run `cloudflared tunnel login` (opens browser) to generate `~/.cloudflared/cert.pem`.
   - **Workaround (no login):** `cloudflared tunnel --url http://localhost:<port> --origincert /dev/null` bypasses the cert check and uses trycloudflare.com. No uptime guarantee.
   - ⚠️ **Pitfall: ports may be firewalled at the provider level** — even if `ss -tlnp` shows your listener on 0.0.0.0:<port>, the hosting provider may block inbound. Always verify external access with `curl -m 3 http://<public_ip>:<port>/`.
   - **Alternative: Cloudflare Workers** — deploy a Worker at `*.workers.dev` as a public-faced proxy. No tunnel needed, but your API token needs `Workers Scripts:Edit` permission (Workers AI-only tokens won't work).

6. **Wrong event type?** The webhook URL must be reachable from the service. For local development, use a tunnel (ngrok, cloudflared).
6. **Wrong event type?** Check `--events` filter matches what the service sends. Use `hermes webhook test <name>` to verify the route works.
