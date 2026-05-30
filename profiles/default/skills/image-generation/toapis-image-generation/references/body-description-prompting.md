# Body Description Prompting — Iteration Log

## The Thickness Pendulum Problem

GPT-Image-2 (and most commercial image generators) has a strong **default bias toward slim/athletic body types**. Pushing against this default requires precision — too little and you get thin legs, too much and you get obese.

### The Session (2026-05-04): Tesla Model Y Driver Seat Product Photo

**v1 prompt excerpt:**
> "Thick heavy round massive legs with cold pale white skin"

→ Result: **Legs too thin** (AI defaulted to slim build). Skin wrong (pale white → inaccurate for mixed-race user).

**v2 prompt excerpt:**
> "EXTREMELY THICK, DENSE, HEAVY, HEFTY man thighs — FAT-COVERED MUSCLE legs, round and massive like tree trunks, not lean, not defined, not athletic, not toned. Huge circumference thighs..."
> "The legs are NOT lean, NOT slender, NOT defined, NOT athletic. They are hefty, dense, fat-covered, round, thick."

→ Result: **Legs became obese** ("大胖子"). The extreme stacked adjectives + multiple negation clauses pushed the model to an extreme caricature.

**v3 prompt excerpt:**
> "The man's thighs are thick and round with natural bulk — solid, powerful legs with a dense look that comes from a large frame. The thighs have a visible natural fullness over strong underlying mass, like a heavyweight athlete or rugby player build. They spread apart slightly on the seat cushion, substantial without being extreme. Not skinny, not obese — just big, heavy, well-built legs with good mass."

→ Result: **Balanced approach**. Uses body-type analogy (rugby player/heavyweight athlete) instead of extreme adjectives. Explicit "not skinny, not obese" framing in a single sentence.

### Key Principles

| Approach | Example | Result |
|----------|---------|--------|
| **Body-type analogy** | `like a rugby player build`, `heavyweight athlete legs` | ✅ Most reliable |
| **"Not X, not Y" framing** | `not skinny, not obese` | ✅ Good clarifier |
| **Natural positive description** | `thick and round with natural bulk`, `visible fullness over strong mass` | ✅ Works |
| **Single extreme adjective** | `thick`, `dense`, `solid` | ✅ OK in moderation |
| **Stacked extreme adjectives** | `EXTREMELY THICK + DENSE + HEFTY + MASSIVE + FAT-COVERED` | ❌ Obese |
| **Negative-only framing** | `not lean not defined not athletic not toned` | ❌ Confuses model |

### Skin Tone Rules

| ❌ Wrong | ✅ Correct |
|----------|-----------|
| `cold pale white skin` | `fair mixed-race skin with warm ivory undertones` |
| `pale white legs` | `mixed Eurasian heritage complexion, natural warm tone` |
| `ghost white` | `fair skin with warm undertones, not caucasian white` |

### Checklist Before Generating

1. [ ] Use **body-type analogy** (rugby, powerlifter, heavyweight) not extreme chains
2. [ ] Include `not skinny, not obese` or equivalent single-sentence framing
3. [ ] Skin described as **mixed-race warm-toned** not pale white
4. [ ] Sock height is anatomically precise (e.g. `2-3cm above ankle bone`)
5. [ ] Shoes described with `slightly worn`, `natural creasing` (not pristine)
6. [ ] At least 1 reference image used for body proportions (REF06 preferred)
7. [ ] Commercial/editorial framing to avoid safety filters
