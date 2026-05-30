# Proxy Configuration for This WSL Environment

## Overview

This WSL environment has a dual-proxy situation that affects all API calls:
1. **Env proxy** — `https_proxy=socks5h://localhost:1080` (globally set, **does not work** for most external APIs)
2. **Working proxy** — `socks5://172.20.128.1:10808` (actual Windows-side proxy that reaches the internet)

## Rules by API

| API | Proxy | Method | Notes |
|-----|-------|--------|-------|
| **Gemini** (`generativelanguage.googleapis.com`) | `socks5://172.20.128.1:10808` | `session.trust_env=False` + explicit proxy param | Env proxy `localhost:1080` doesn't connect; use the `trust_env=False` trick |
| **Feishu API** (`open.feishu.cn`) | **None** (direct) | `session.trust_env=False` | Must bypass all proxy settings; the env proxy breaks Feishu connections |
| **worldtimeapi / ntp times** | **None** (direct) | `unset https_proxy; unset http_proxy; curl --noproxy '*'` | Must clear env vars before calling |

## Python Code Pattern

```python
import requests

# For Gemini API (via working proxy):
proxies = {
    "http": "socks5://172.20.128.1:10808",
    "https": "socks5://172.20.128.1:10808",
}
session = requests.Session()
session.trust_env = False  # ⚠️ CRITICAL: ignore the broken env proxy
session.proxies.update(proxies)

# For Feishu API (no proxy):
session = requests.Session()
session.trust_env = False  # ⚠️ CRITICAL: bypass env proxy
# Do NOT set session.proxies — direct connection

# For curl commands that need proxy:
curl -x socks5://172.20.128.1:10808 https://generativelanguage.googleapis.com/...

# For curl that must NOT use proxy:
unset https_proxy; unset http_proxy; curl --noproxy '*' https://open.feishu.cn/...
```

## Key Traps

- ❌ **`socks5h://localhost:1080`** — The env has this but it's a different proxy that doesn't route to the internet. Never use it for external APIs.
- ❌ **Using `requests.post()` without `trust_env=False`** — It will pick up the broken env proxy and hang/refuse connection.
- ✅ **Always create a new `requests.Session()`** with `trust_env=False` for both Gemini and Feishu API calls.
- ✅ **The `sudo pip3 install ...` trick** doesn't help; this is a proxy routing issue, not a proxy presence issue.
- ⚠️ **`socks5://` vs `socks5h://`**: `socks5h://localhost:1080` tries to resolve DNS via the SOCKS server (which fails). `socks5://172.20.128.1:10808` resolves DNS locally (which works). The `h` suffix matters.

## Verifying Connectivity

```bash
# Test proxy connectivity to Gemini:
curl -x socks5://172.20.128.1:10808 -s --max-time 10 \
  "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_KEY" \
  | head -c 200

# Test direct Feishu connectivity (no proxy):
unset https_proxy; unset http_proxy
curl -s --noproxy '*' --max-time 10 "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$FEISHU_APP_ID\",\"app_secret\":\"$FEISHU_APP_SECRET\"}" \
  | head -c 200
```

## Reference: Scripts That Already Handle This

- `daily_random_lover_message.py` — uses `PROXY = "socks5://172.20.128.1:10808"` with `session.trust_env = False`
- `miss_you_pipeline.sh` — may need manual proxy handling
