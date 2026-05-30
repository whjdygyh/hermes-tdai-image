# Token & Cost Tracking in Hermes Agent

## Config: `display.show_cost`

Set `display.show_cost: true` in config.yaml to show per-response token and/or cost data in the model's reply.

Default: `false`.

Example config:
```yaml
display:
  show_cost: true      # shows token summary per response
  show_reasoning: true # also shows reasoning tokens if available
```

After enabling, each assistant response includes a line like:
```
cost: ~1,234 tokens ($0.00XXX)
```

The exact format depends on the provider's API response. Requires a fresh session (`/reset`) or gateway restart to take effect.

## Slash Command: `/usage`

Already available without config changes:
```
/usage        Show token usage
```
This displays the current session's total token usage (all turns aggregated), not per-response.

## Gateway Log: Session-Level Estimates

The gateway log at `~/.hermes/profiles/<name>/logs/gateway.log` records session hygiene events with token estimates:

```
Session hygiene: 114 messages, ~194,152 tokens (actual) — auto-compressing
Session hygiene: compressed 114 → 20 msgs, ~194,152 → ~1,514 tokens
```

These are **hermes's own tokenizer estimates**, not the provider's actual counts. They trigger when the session approaches a configurable threshold (default: 85% of context window = 55,705 tokens for 65,536 context).

Config knob:
```yaml
compression:
  threshold: 0.50       # fraction of context at which compression triggers
  target_ratio: 0.20    # compress down to this fraction
```

## Provider-Specific Token Data

### DeepSeek API
Returns the following in every `/chat/completions` response:
```json
{
  "usage": {
    "prompt_tokens": 1234,
    "completion_tokens": 567,
    "total_tokens": 1801,
    "prompt_cache_hit_tokens": 800,
    "prompt_cache_miss_tokens": 434
  }
}
```
- `prompt_cache_hit_tokens` / `prompt_cache_miss_tokens` — DeepSeek-specific; indicates how much of the input reused cached context (reduces cost).
- DeepSeek's pricing is per-million-tokens for input (cached vs. uncached) and output.

### Other Providers
Most providers (OpenAI, Anthropic, OpenRouter, Gemini) return `prompt_tokens`, `completion_tokens`, `total_tokens` in their standard API responses. Some also include `prompt_tokens_details` (cached input, audio tokens, etc.).

## What `show_cost` Does NOT Show

- **Subagent delegation costs** — tokens consumed by `delegate_task` subagents are not reflected in the parent session's `/usage` or cost display.
- **Session search queries** — `session_search` tool calls consume tokens silently.
- **Auxiliary model calls** — vision processing, compression summaries, TTS generation.
- **TTS/STT processing** — these are separate from LLM token costs.
- **Tool execution overhead** — tool call schemas and results contribute to prompt tokens but are not itemized.

## How to Monitor Total Usage

For persistent analytics:
```bash
hermes insights [--days N]   # Usage analytics (CLI command)
```
Or browse the gateway log for session hygiene records to estimate cumulative context size over time.
