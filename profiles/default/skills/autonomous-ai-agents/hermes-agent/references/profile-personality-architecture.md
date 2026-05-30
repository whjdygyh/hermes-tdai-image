# Profile Personality Architecture (Lover Profile)

## How the System Prompt is Composed

The Lover profile's system prompt (what the agent sees at the start of every conversation) is assembled from **three independent layers**:

### Layer 1: SOUL.md (Personality / Character)
**Path:** `~/.hermes/profiles/lover/SOUL.md`

This is the **character definition** — who the agent is, how it talks, what it believes. In the Lover profile, this contains the "Lover - 你的私人伴侣" personality: role setting, core principles, communication style, capabilities, rules, and trigger phrases.

**What goes here:** The agent's identity, tone, ethical boundaries, communication style. Not facts, not paths, not credentials.

### Layer 2: Memory (Facts, Paths, Preferences)
**Stored via:** `memory(action='add'|'replace'|'remove')` tool
**Injected:** Automatically at the start of every new conversation

Memory has two targets:
- `memory` (system notes) — environment facts, project conventions, tool quirks, lesson learned
- `user` (user profile) — who the user is, their preferences, communication style, pet peeves

**What goes here:** File paths (`~/.hermes/profiles/lover/notes/重要记事.md`), API endpoints, user preferences, environment details — anything that should be there every session.

**Capacity:** 2,200 chars total. Entries must be compact. When full, consolidate or remove stale entries.

### Layer 3: Skills (Procedural Knowledge)
**Location:** `~/.hermes/profiles/lover/skills/`

Skills are procedural — "how to do X." Each skill has a SKILL.md (instructions) and optionally references/ (detail), templates/ (boilerplate), scripts/ (runnable code).

**What goes here:** Reusable workflows, step-by-step procedures, API call patterns, tool configurations.

### Config.yaml (Technical configuration)
**Path:** `~/.hermes/profiles/lover/config.yaml`

Controls model provider, toolsets, TTS, cron, memory settings, etc. Not injected into the system prompt directly — sets technical behavior.

**Key personality-related fields:**
- `personality: lover` — selects the character/personality
- `memory.memory_enabled: true` — enables memory injection
- `skills.external_dirs: []` — custom skill paths
- `prefill_messages_file: ''` — additional system context (currently unused)

## Which Layer to Use for What

| You want to... | Use... |
|---|---|
| Define who the agent is | SOUL.md |
| Save a path, credential note, or fact | Memory (memory target) |
| Save a user preference or pet peeve | Memory (user target) |
| Document a reusable workflow | Skill (SKILL.md) |
| Store detailed reference material | Skill → references/ |
| Add a template or starter file | Skill → templates/ |
| Add a runnable script | Skill → scripts/ |
| Change provider, model, TTS | config.yaml |

## Pitfalls

- **Memory is NOT for workflows.** Don't save step-by-step procedures to memory — it hits the 2,200 char limit and is the wrong abstraction. Use skills.
- **SOUL.md is NOT for facts.** Don't put file paths or API details in SOUL.md. It's for identity and tone only.
- **Memory is not archived.** Old entries don't auto-expire. Manually prune stale entries when approaching the limit.
- **System prompt composition order:** SOUL.md is loaded first, then memory is injected, then skills are listed. Later layers don't override earlier ones — they add context.
- **Config changes need restart.** Changing `personality` in config.yaml or editing SOUL.md takes effect on next session (`/reset` or new conversation). Memory and skills update mid-conversation via their respective tools.
