# Chinese Mandopop Ballad Songwriting — Proven Template

## Session Context (2026-05-15)
Successful generation of "千帆尽处" via Suno manual workflow.
User subscribed to Suno, companion wrote lyrics + style, user copy-pasted.

## Style/Prompt Template (for Suno Custom Mode)
```
Mandarin Chinese pop ballad, slow emotional male vocal, piano and strings, heartfelt storytelling, romantic, building crescendo, 90 BPM
```

## Lyric Structure for Emotional Narrative

### Macro Arc
```
Verse 1 — setup, world-building, "before"
Verse 2 — deepening, specific memories
Pre-Chorus — tension building, repeated phrase/idea
Chorus — emotional core, title/hook line, repeated
Verse 3 — twist/revelation/perspective shift
Pre-Chorus — same tension
Chorus — repeat core
Bridge — reflection, transformation, rawer/quieter
Outro — echo of hook, fade to completion/emotional resolution
```

### Section Lengths (proven balance)
| Section | Lines | Syllables per line |
|---------|-------|-------------------|
| Verse | 4-6 | 10-14 |
| Pre-Chorus | 2-4 | 10-14 |
| Chorus | 6-8 | 8-14 |
| Bridge | 4-6 | 8-12 |
| Outro | 3-5 | 6-10, fragmenting toward end |

## Rhyme Theory Applied to Chinese Ballads

### Strategy
- **Alternate perfect and near rhymes** to avoid nursery-rhyme effect
  - Perfect: 春/fēn → works but use sparingly
  - Near: 天/间, 光/伤 → smoother, less forced
- **Internal rhyme** within long lines for extra texture
  "星光 都揉碎了咽进喉咙里面" → 光/面 don't end-rhyme but internal phonetics support the flow
- **End-rhyme pattern**: AABB or ABAB per verse, ABAB or AABB for chorus
- **Bridge** can break the rhyme scheme for emotional emphasis

### Syllable Pacing
- 10-14 chars per line in verses (natural Chinese speech rhythm)
- Shorter lines in bridge for reflective/quiet mood
- Fragmenting lines in outro for fade-out effect

## The Narrative Layers

### Layer 1: Personal Story
- First-person narrator, specific experience
- "曾以为 这一生要独自穿过荒原" — opens with worldview, not just emotion
- Concrete imagery: 星光揉碎, 咽进喉咙, 泪, 风霜

### Layer 2: Transformation
- The turn when "you" appears
- "直到你出现 像一场迟到的春风" — metaphor signals the shift
- Contrast: before (lonely/hard) vs after (warm/found)

### Layer 3: The Promise
- Chorus states the theme clearly, repeatable hook
- "千帆尽处 是你啊" — title/hook, the line people remember
- "这一生太短 不够说爱你 / 那就生生世世 把它说完" — escalation from temporal to eternal

### Layer 4: Metacognition (Bridge)
- Why it happened, almost philosophical
- "如果来生还要走这一条路 / 我依然会选择 在风里等你" — fate is a choice not a destiny
- "不早一秒 也不晚一秒" — timing, the "right moment" theme

## Suno-Specific Tips for Chinese Ballads

1. **Keep Chinese lyrics in simplified characters** — Suno handles them fine
2. **Section tags in English** — [Verse 1], [Chorus], etc. Suno recognizes these across languages
3. **No artist names or song titles** — describe the sound: "Mandarin Chinese pop ballad, piano and strings, slow" not "like 三生三幸"
4. **BPM: 80-100 for ballads** — tested 90 works well
5. **"Male vocal" in style field** ensures male voice generation
6. **Style field ~200 chars** is enough for Chinese ballads

## Common Pitfalls

| Issue | Fix |
|-------|-----|
| Lyrics too long (>3000 chars) | Cut verses to 4 lines, keep choruses tight |
| Suno ignores bridge | Put [Bridge] tag on its own line before and after |
| Female vocal instead of male | Add "male vocal" explicitly in style, not just "male" |
| Flat dynamics (no build) | Add dynamic descriptions to style: "building crescendo, starts intimate, swells to powerful" |
| Hook doesn't stand out | Repeat title phrase 2-3 times in chorus, put it at the end of the first chorus line |
