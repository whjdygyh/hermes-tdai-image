---
name: songwriting-and-ai-music
description: "Songwriting craft and AI music generation — lyrics, structure, prompt engineering, API workflows (Suno/Mureka/Stable Audio/ElevenLabs)."
tags: [songwriting, music, suno, stable-audio, elevenlabs, mureka, useapi, parody, lyrics, creative, api-generation, music-generation]
platforms: [linux, macos, windows]
triggers:
  - writing a song
  - song lyrics
  - music prompt
  - suno prompt
  - stable audio prompt
  - elevenlabs sound generation
  - mureka api
  - mureka music generation
  - parody song
  - adapting a song
  - AI music generation
  - music API
  - generate a song
---

# Songwriting & AI Music Generation

Everything here is a GUIDELINE, not a rule. Art breaks rules on purpose.
Use what serves the song. Ignore what doesn't.

---

## 1. Song Structure (Pick One or Invent Your Own)

Common skeletons — mix, modify, or throw out as needed:

```
ABABCB  Verse/Chorus/Verse/Chorus/Bridge/Chorus    (most pop/rock)
AABA    Verse/Verse/Bridge/Verse (refrain-based)    (jazz standards, ballads)
ABAB    Verse/Chorus alternating                    (simple, direct)
AAA     Verse/Verse/Verse (strophic, no chorus)     (folk, storytelling)
```

The six building blocks:
- Intro      — set the mood, pull the listener in
- Verse      — the story, the details, the world-building
- Pre-Chorus — optional tension ramp before the payoff
- Chorus     — the emotional core, the part people remember
- Bridge     — a detour, a shift in perspective or key
- Outro      — the farewell, can echo or subvert the rest

You don't need all of these. Some great songs are just one section
that evolves. Structure serves the emotion, not the other way around.

---

## 2. Rhyme, Meter, and Sound

RHYME TYPES (from tight to loose):
- Perfect: lean/mean
- Family: crate/braid
- Assonance: had/glass (same vowels, different endings)
- Consonance: scene/when (different vowels, similar endings)
- Near/slant: enough to suggest connection without locking it down

Mix them. All perfect rhymes can sound like a nursery rhyme.
All slant rhymes can sound lazy. The blend is where it lives.

INTERNAL RHYME: Rhyming within a line, not just at the ends.
  "We pruned the lies from bleeding trees / Distilled the storm
   from entropy" — "lies/flies," "trees/entropy" create internal echoes.

METER: The rhythm of stressed vs unstressed syllables.
- Matching syllable counts between parallel lines helps singability
- The STRESSED syllables matter more than total count
- Say it out loud. If you stumble, the meter needs work.
- Intentionally breaking meter can create emphasis or surprise

---

## 3. Emotional Arc and Dynamics

Think of a song as a journey, not a flat road.

ENERGY MAPPING (rough idea, not prescription):
  Intro: 2-3  |  Verse: 5-6  |  Pre-Chorus: 7
  Chorus: 8-9  |  Bridge: varies  |  Final Chorus: 9-10

The most powerful dynamic trick: CONTRAST.
- Whisper before a scream hits harder than just screaming
- Sparse before dense. Slow before fast. Low before high.
- The drop only works because of the buildup
- Silence is an instrument

"Whisper to roar to whisper" — start intimate, build to full power,
strip back to vulnerability. Works for ballads, epics, anthems.

---

## 4. Writing Lyrics That Work

SHOW, DON'T TELL (usually):
- "I was sad" = flat
- "Your hoodie's still on the hook by the door" = alive
- But sometimes "I give my life" said plainly IS the power

THE HOOK:
- The line people remember, hum, repeat
- Usually the title or core phrase
- Works best when melody + lyric + emotion all align
- Place it where it lands hardest (often first/last line of chorus)

PROSODY — lyrics and music supporting each other:
- Stable feelings (resolution, peace) pair with settled melodies,
  perfect rhymes, resolved chords
- Unstable feelings (longing, doubt) pair with wandering melodies,
  near-rhymes, unresolved chords
- Verse melody typically sits lower, chorus goes higher
- But flip this if it serves the song

AVOID (unless you're doing it on purpose):
- Cliches on autopilot ("heart of gold" without earning it)
- Forcing word order to hit a rhyme ("Yoda-speak")
- Same energy in every section (flat dynamics)
- Treating your first draft as sacred — revision is creation

---

## 5. Parody and Adaptation

When rewriting an existing song with new lyrics:

THE SKELETON: Map the original's structure first.
- Count syllables per line
- Mark the rhyme scheme (ABAB, AABB, etc.)
- Identify which syllables are STRESSED
- Note where held/sustained notes fall

FITTING NEW WORDS:
- Match stressed syllables to the same beats as the original
- Total syllable count can flex by 1-2 unstressed syllables
- On long held notes, try to match the VOWEL SOUND of the original
  (if original holds "LOOOVE" with an "oo" vowel, "FOOOD" fits
   better than "LIFE")
- Monosyllabic swaps in key spots keep rhythm intact
  (Crime -> Code, Snake -> Noose)
- Sing your new words over the original — if you stumble, revise

CONCEPT:
- Pick a concept strong enough to sustain the whole song
- Start from the title/hook and build outward
- Generate lots of raw material (puns, phrases, images) FIRST,
  then fit the best ones into the structure
- If you need a specific line somewhere, reverse-engineer the
  rhyme scheme backward to set it up

KEEP SOME ORIGINALS: Leaving a few original lines or structures
intact adds recognizability and lets the audience feel the connection.

---

## 6. AI Music Generation — Prompt Engineering (Suno-style)

Suno-style prompt structure (style + lyrics + metatags) works across multiple platforms, not just Suno. The style/lyrics/tags structure is transferable to Mureka, Stable Audio, and others.

### Style/Genre Description Field

FORMULA (adapt as needed):
  Genre + Mood + Era + Instruments + Vocal Style + Production + Dynamics

```
BAD:  "sad rock song"
GOOD: "Cinematic orchestral spy thriller, 1960s Cold War era, smoky
       sultry female vocalist, big band jazz, brass section with
       trumpets and french horns, sweeping strings, minor key,
       vintage analog warmth"
```

DESCRIBE THE JOURNEY, not just the genre:
```
"Begins as a haunting whisper over sparse piano. Gradually layers
 in muted brass. Builds through the chorus with full orchestra.
 Second verse erupts with raw belting intensity. Outro strips back
 to a lone piano and a fragile whisper fading to silence."
```

TIPS:
- V4.5+ supports up to 1,000 chars in Style field — use them
- NO artist names or trademarks. Describe the sound instead.
  "1960s Cold War spy thriller brass" not "James Bond style"
  "90s grunge" not "Nirvana-style"
- Specify BPM and key when you have a preference
- Use Exclude Styles field for what you DON'T want
- Unexpected genre combos can be gold: "bossa nova trap",
  "Appalachian gothic", "chiptune jazz"
- Build a vocal PERSONA, not just a gender:
  "A weathered torch singer with a smoky alto, slight rasp,
   who starts vulnerable and builds to devastating power"

### Metatags (place in [brackets] inside lyrics field)

STRUCTURE:
  [Intro] [Verse] [Verse 1] [Pre-Chorus] [Chorus]
  [Post-Chorus] [Hook] [Bridge] [Interlude]
  [Instrumental] [Instrumental Break] [Guitar Solo]
  [Breakdown] [Build-up] [Outro] [Silence] [End]

VOCAL PERFORMANCE:
  [Whispered] [Spoken Word] [Belted] [Falsetto] [Powerful]
  [Soulful] [Raspy] [Breathy] [Smooth] [Gritty]
  [Staccato] [Legato] [Vibrato] [Melismatic]
  [Harmonies] [Choir] [Harmonized Chorus]

DYNAMICS:
  [High Energy] [Low Energy] [Building Energy] [Explosive]
  [Emotional Climax] [Gradual swell] [Orchestral swell]
  [Quiet arrangement] [Falling tension] [Slow Down]

GENDER:
  [Female Vocals] [Male Vocals]

ATMOSPHERE:
  [Melancholic] [Euphoric] [Nostalgic] [Aggressive]
  [Dreamy] [Intimate] [Dark Atmosphere]

SFX:
  [Vinyl Crackle] [Rain] [Applause] [Static] [Thunder]

Put tags in BOTH style field AND lyrics for reinforcement.
Keep to 5-8 tags per section max — too many confuses the AI.
Don't contradict yourself ([Calm] + [Aggressive] in same section).

### Custom Mode
- Always use Custom Mode for serious work (separate Style + Lyrics)
- Lyrics field limit: ~3,000 chars (~40-60 lines)
- Always add structural tags — without them Suno defaults to
  flat verse/chorus/verse with no emotional arc

### Non-Western & Traditional Instrument Prompting Pitfall

**Problem:** When prompting for a traditional non-Western instrument (bansuri, sitar, erhu, koto, shakuhachi, duduk, etc.), Suno defaults to Western pop/classical tonal structure — verse-chorus form, functional harmony, chord-progression-based melody — even when the instrument name is correct and you've removed Western genre tags.

**Root cause:** The AI was trained primarily on Western music. Specifying the instrument name alone is NOT enough to trigger the correct melodic/phrasing system. Suno maps "flute" → Western flute conventions unless explicitly redirected.

**Fix that worked (tested May 2026 on bansuri, two-round iteration):**

Round 1 — fixed tempo and removed drums (BPM + "no drums"):
- `50-60 BPM` slows it down
- `no drums, no percussion, no rhythm section` removes percussion

Round 2 — fixed melodic/phrasing structure (the critical second fix):
- `in raga style` — anchors to the correct tradition
- `meend (slides between notes)` — indigenous technical terms with translation
- `alap (slow improvisational unfolding)` — describes the correct form
- `raga-based melodic contours` — specifies the melodic system
- `NOT Western pop melody — no verse-chorus structure, no chord progressions` — explicit negative directive
- Cultural imagery: `like sitting beside the Ganges at dusk` (not "beside a river")

**Template (adapt instrument/tradition as needed):**
```
Solo {instrument} in {tradition} style, slow and meditative, {BPM} BPM.
{desired duration}
{negative space — no drums, no percussion, no rhythm section}
{drone/accompaniment description}
{tradition} phrasing — {indigenous term 1 (translation)}, {indigenous term 2 (translation)}, {tradition}-based melodic contours.
NOT Western pop melody — no verse-chorus structure, no chord progressions.
{keep one-level / stay unhurried / like a {tradition} form}
{cultural imagery to anchor the tradition}
Hold long notes. Let silence breathe between phrases.
Instrumental only.
```

**Key insight — order matters:** The first round (tempo + percussion removal) is necessary but insufficient. Slow pop still sounds like pop. The second round (indigenous terms + tradition anchoring + NOT Western pop directive) is what actually changes the melodic DNA. If you only get one shot, prioritize the melodic/style terms over tempo — a fast bansuri in raga style is still Indian, a slow bansuri playing chord-progression pop is still pop.

**General principle for any non-Western instrument prompt:**
1. Name the instrument + tradition/raga/maqam system
2. Add indigenous technical terms with parenthetical translations
3. Explicitly negate Western defaults: "NOT Western pop melody"
4. Use culturally-specific imagery (Ganges, not river; Himalayas, not mountains)
5. Describe the form/development pattern (alap = unfolding, not verse-chorus)

### Suno Duration & Extend Workaround

**Problem:** Suno's model architecture limits single generation to approx 3-4 minutes. Writing "7 minutes duration" in the Style prompt does NOT increase this — the model simply ignores length instructions beyond its architecture limit.

**Workaround — Extend (续写) to reach desired length:**
1. Generate a 3-4 minute track with the desired prompt
2. Click the **Extend** button on the result
3. Suno continues from the ending, generating another 3-4 minute segment
4. Two segments combined = 6-8 minutes, with good style continuity

**Alternative — Replay + manual splice:**
1. Generate once → click **Replay** for a variation
2. Manually concatenate two variations in audio editing software
3. Less seamless than Extend but gives more variety

### Suno Audio Reference Feature (2026-05-18)

Suno Advanced mode has **three reference input slots:**

| Slot | Function | Best for |
|------|----------|----------|
| **Audio** 🎯 | Drag in a reference track → Suno mimics its overall style, instrumentation, and atmosphere | ✅ Genre/style transfer from real recordings |
| **Voice** | Mimics vocal timbre/singing style | ❌ Only for songs with vocals |
| **Inspo** | Creative/lyrical inspiration reference | ❌ Not for sound quality |

**Workflow for using Audio Reference:**
1. Find an authentic reference track in the desired style (e.g., real Indian bansuri from YouTube/SoundCloud)
2. Download a 30-60 second clip from the middle section (avoid intros/outros with silence or spoken parts)
3. In Suno Advanced mode, drag the audio file into the **Audio** box
4. **CRITICAL — Style Influence:** Set to **100%** to push the output closest to the reference style. Lower values give the AI more room to deviate.
5. Style field still needs the full prompt — Audio Reference guides the sound, the prompt guides the structure
6. Keep **Exclude Styles** and **Lyrics Mode: Manual** as usual

### Suno Advanced Mode Complete Configuration

| Field | Setting | Why |
|-------|---------|-----|
| **Lyrics** | Leave empty | Instrumental — no lyrics needed |
| **Style/Prompt** | Full prompt text | One copyable block |
| **Exclude Styles** | `pop, electronic, rock, orchestral, cinematic` | Prevents unwanted instrument additions |
| **Vocal Gender** | Don't select | Instrumental has no vocals |
| **Lyrics Mode** | **Manual** | Prevents AI from auto-generating lyrics |
| **Weirdness** | 0-10 | Meditation/instrumental doesn't need weirdness |
| **Style Influence** | **80-100%** (100% with Audio Ref) | Higher = stricter adherence to prompt

### Suno API Automation (CURRENTLY BROKEN — DEPRECATED BACKEND)

> ⚠️ **⚠️ IMPORTANT — API OUTAGE AS OF MAY 2026 ⚠️**
> The `suno-api` Python package (v0.1.0) targets `studio-api.suno.ai`, which **has been suspended (returns 503 "Service Suspended")** as of May 2026. The old Render.com-backed API no longer exists. All documented endpoints below are **historical only**.
>
> Additionally, `clerk.suno.ai` is behind Cloudflare protection that blocks non-browser traffic. `curl_cffi` impersonation fails in environments without the patched libcurl (WSL, many Linux distros).
>
> **Do NOT attempt to use `suno-api` 0.1.0 as of May 2026** — it will fail at the first API call. The skill retains this section for reference in case an updated library emerges or Suno reopens their API.

#### Historical Reference (For When/If Suno Re-opens API)

The `suno-api` Python package (`pip install suno-api`, module: `suno`) was designed to automate Suno song generation using `curl_cffi` for browser impersonation and auto-refreshing JWT tokens via Clerk's session token API.

```python
from suno import Suno

client = Suno(cookie_string)
credits = client.get_credits()
songs = client.songs.generate(
    prompt=lyrics_text,
    tags=style_tags,
    custom=True,
    instrumental=False,
)
```

#### How Auto-Refresh Worked

1. `Suno(cookie)` → `GET clerk.suno.ai/v1/client` → extracts session ID
2. On 401, `_renew()` → `POST clerk.suno.ai/v1/client/sessions/{sid}/tokens/api` → fresh JWT
3. Sets `Authorization: Bearer {jwt}` header transparently

#### Deprecated Endpoints (all now return 503/403)

| Method | URL (now dead) | Purpose |
|--------|---------------|---------|
| GET | `clerk.suno.ai/v1/client` | Cloudflare-blocked |
| POST | `clerk.suno.ai/v1/client/sessions/{sid}/tokens/api` | Cloudflare-blocked |
| POST | `studio-api.suno.ai/api/generate/v2/` | **Service Suspended** |
| GET | `studio-api.suno.ai/api/feed` | **Service Suspended** |
| GET | `studio-api.suno.ai/api/billing/info` | **Service Suspended** |

#### Known Failure Modes (for diagnostic reference)

1. **`studio-api.suno.ai` returns 503 "Service Suspended"** — The Render.com backend was taken down. This is permanent unless Suno relaunches their API. CNAME: `suno-internal-api.onrender.com` → `*.cdn.cloudflare.net` (Cloudflare proxied, but the origin is dead).

2. **`clerk.suno.ai` returns Cloudflare 403** — "DNS points to prohibited IP" means Cloudflare blocks direct API access from non-browser clients (e.g., curl, requests). The `curl_cffi` impersonation was meant to bypass this, but see failure #3.

3. **`curl_cffi` impersonation fails in WSL** — `curl_cffi` 0.5.10 raises `RequestsError: impersonate chrome is not supported` when the system's libcurl lacks the impersonation patch. Common causes:
   - WSL's default libcurl is outdated (the curl-impersonate patches are not included)
   - `HTTP_PROXY` pointing to a non-running proxy (e.g., `socks5h://localhost:1080` for V2Ray) causes instant connection refused errors
   - **Fix (theoretical):** Install a curl-impersonate build, or unset `HTTP_PROXY` environment variables if the proxy is down
   - **Practical:** Don't bother — the API is dead anyway

4. **`suno.com` paths: SPA landing vs 404** — The web app routes some paths (`/api`, `/developer`) through Next.js to serve the SPA (Returns 200 with app shell — looks like a normal page). Others (`/api/docs`, `/api/create`, `/api/generate`) return 404. There is **no developer portal, no API documentation page, no REST API** exposed anywhere on suno.com. Direct HTTP calls to API-like paths always return 404 except a few that return the SPA (which is useless for automation).

#### Platform Selection (as of May 2026)

**⚠️ User hard preference: only platforms with APIs the agent can call programmatically. Browser-based/manual workflows are discarded. "凡是不能自动化的，你不能直接操作的，都弃之."**

| Approach | Viability | Notes |
|----------|-----------|-------|
| **Stable Audio (Stability AI)** | ✅ API viable | `POST api.stability.ai/v1/generation/stable-audio`. Needs API key. Can be called via curl/Python. |
| **ElevenLabs Sound Generation** | ✅ API viable | `POST api.elevenlabs.io/v1/sound-generation`. Needs API key. Can be called via curl/Python. Music generation endpoint at `/v1/music-generation` — check current docs. |
| **Mureka (native API)** | ✅ API viable (有正式API Key系统) | `POST api.mureka.cn/v1/song/generate`. Needs `Authorization: Bearer {api_key}`. API Key从 platform.mureka.cn 申请。当前余额不足需要充值。文档: platform.mureka.cn/docs/ |
| **Web browser generation (Suno/Udio)** | ❌ Discarded per user preference | User explicitly rejects any platform that can't be automated. Suno has no working API. |
| **Third-party API wrappers** | ⚠️ Unknown | Projects like `suno-comfyui` use `muapi.ai` API (third-party Suno wrapper). Investigate if needed. |
| **Wait for official Suno API** | ❌ Not available | Suno has no public API as of May 2026. |
| **`suno-api` 0.1.0** | ❌ Dead | Backend suspended. |

**Updated convention:** Default to **API-based generation** (Stable Audio, ElevenLabs, Mureka). However, if all API paths hit dead ends (no key, quota exhausted, expensive), the user has approved a **manual Suno fallback** where companion writes lyrics/style and user operates Suno in browser. Offer this before giving up. If no API key is available for the viable platforms, inform the user and offer to help set one up (sign up → get key → write script).

---

### Manual Suno Workflow (User-Managed Browser)

**Alternative workflow (2026-05-15+):** User may choose to subscribe to Suno themselves and do manual browser generation, using the companion/Lover solely as the **lyricist and style prompt writer**. This "I create, you operate" split has been explicitly tested and works well:

**Workflow:**
1. Companion writes complete lyrics + style/genre description
2. User copies both into Suno's Custom Mode form fields
3. User hits Generate
4. Companion reviews and gives feedback

**When to offer this workflow:**
- User asks for manual operation ("我来手动操作吧")
- User mentions subscribing to Suno or already being on the Suno creation page
- User gets frustrated with API dead-ends (quota limits, expensive credits, broken wrappers)

**The "I create, you operate" split:** The companion writes everything the user needs to copy-paste (full lyrics with section tags clear enough to follow, complete style prompt as one copyable block). User handles the actual generation.

**Role switch for this mode:** When user says "你来当创作者" (you be the creator), the companion adopts a professional songwriter persona — focused on craft, structure, rhyme, thematic arc.

**Chinese Mandopop Ballad Recipe (tested working):**

*Style/Prompt template:*
```
Mandarin Chinese pop ballad, slow emotional male vocal, piano and strings, heartfelt storytelling, romantic, building crescendo, 90 BPM
```

*Lyric structure for emotional narrative (tested working):*
```
Verse 1 — setup, world-building, "before"
Verse 2 — deepening, more specific memories
Pre-Chorus — tension building, repeated phrase/idea
Chorus — emotional core, title/hook line, repeated
Verse 3 — twist/revelation/perspective shift
Pre-Chorus — same tension
Chorus — repeat core
Bridge — reflection, transformation, rawer/quieter
Outro — echo of hook, fade to completion/emotional resolution
```

*Rhyme theory applied to Chinese ballads:*
- Alternate perfect and near rhymes to avoid nursery-rhyme effect
- Use internal rhyme for extra texture within long lines
- End-rhyme pattern: AABB or ABAB per verse, ABAB or AABB for chorus
- Bridge can break the rhyme scheme for emotional emphasis

---

### Suno Song Distribution & Release Workflow (Post-Generation)

After the user generates songs via Suno manual mode, they need to distribute/release them to streaming platforms. This workflow has been tested with the user.

**Suno's Dual-Version Output:**
- Suno generates **2 variations** per prompt
- Strategy: pick the best version for international release, the other for domestic
- This gives two distinct covers/arrangements of the same lyrics

**Platform: RouteNote (Free Plan, tested working)**
- **Cost:** Free (RouteNote takes 15% royalty)
- **UPC/EAN:** Leave blank — RouteNote auto-generates one
- **Cover Art:** 3000x3000px square, JPG/PNG required
- **Release Info needed:**
  - Artist Name (see naming conventions below)
  - Release Title (song name)
  - Primary Genre: Mandopop / Chinese Pop
  - Language: Chinese (Simplified) / Mandarin
  - Label: blank or self-named
- **Select Stores:**
  - **International route:** Spotify, Apple Music, Amazon Music, TikTok (minimum spread)
  - **Domestic route:** 网易云音乐 (NetEase Cloud Music), QQ音乐 — upload directly to their 音乐人平台 instead of RouteNote
- **Timeline:** 3-7 days for RouteNote distribution

**Two-Platform Release Strategy (tested with user):**
```
Version 1 (best) → RouteNote → Spotify + Apple Music + international
Version 2 (second) → 网易云音乐人 + QQ音乐开放平台 → domestic China
```
This maximizes coverage. Same lyrics, different Suno arrangement gives listeners two versions to compare.

**Artist Naming Convention (Lesson Learned):**
- ❌ **Avoid concept/project names** — "泊岸" was rejected as sounding like a project/album name, not a person
- ✅ **Use real-person names** — names that sound like an actual singer/artist
- **Dual-name strategy** (user-approved):
  - **Chinese name** (domestic platforms): 陈一 (short, memorable, Chinese)
  - **English name** (international platforms): **Elian** (confirmed 2026-05-16)
- ⚠️ **CRITICAL: RouteNote's Artist field searches Spotify's real-time DB.** If the name matches an existing Spotify artist, your release links to THEIR profile instead of creating a new one. If "Elian" alone is taken (e.g. Elian Frost exists), use **"Elian Chen"** or another unique variant.
- Test the name: say it out loud. Would you believe a real person is called that?
- Verify uniqueness: search the name on Spotify before submitting the release

### DistroKid Upload (Tested Alternative, May 2026)

When RouteNote fails (artist name Spotify DB lock-in bug), DistroKid is the proven fallback.

Reference file `references/routenote-distribution.md` has the full walkthrough. Key findings from this session:

| Decision Point | Answer | Why |
|----------------|--------|-----|
| AI disclosure | Yes (honest) | Suno watermarks detectable; lying risks account suspension. No direct royalty cut. |
| Apple Music credits | Performer + Producer | Required if Apple Music selected. "Add credits" → select "Producer" from dropdown. |
| Social Media Pack | $4.95/yr | YouTube/TikTok/Instagram monetization |
| ISRC Code | Skip | Auto-assigned for free users |
| Total cost | $4.95 | Social Media Pack only |

**Pitfall:** If you can't see the Producer dropdown options, the common choices are: Producer (correct for AI solo works), Executive Producer, Mixing Engineer, Mastering Engineer, Co-Producer.

**Pitfall — Save raw cookie VALUES, not just names.** When the user provides DistroKid/RouteNote login cookies during a session, capture the actual **value** field of each cookie as raw text. The DK_SYN cookie was recorded only as a description (DK_SYN（session cookie，exp: ~2026-06-13）) with no usable value field — making backend access impossible later.

⚠️ **CRITICAL: Distinguish "bad storage" from "never provided."** Before concluding a cookie value was poorly saved, verify whether it was ever **actually sent by the user**:
- Other DistroKid cookies (cfid, BEEFARONI, LD_REP_ID) all had their values properly stored → user DID send them and they WERE saved
- DK_SYN had NO value recorded → user never sent DK_SYN's value field in any chat message across ALL available session history
- If the user says "聊天记录总会有啊" (it must be in the chat records), run 4-6+ targeted session_search queries (by platform name, cookie name, related keys, domain, session ID patterns) before concluding. Show the evidence of what WAS found vs what wasn't. Then ask for a fresh re-export — don't go back and forth.

**Recovery technique — session_search for lost credentials:**
When a credential in the notes file was truncated or stored without its value, use session_search to scan past conversations for the original raw text:
1. Search by platform name + cookie name + value / session cookie / token
2. If no match, try the platform domain (distrokid.com)
3. If still no match, search for related keys (user_id, session tokens, raw JSON)
4. If still no match, search for companion cookie names (e.g., BEEFARONI, LD_REP_ID, cfid) — if THOSE have values but the session cookie doesn't, the session value was genuinely never sent
5. Only as last resort: ask the user to re-export

This technique successfully recovered a 4,833-character Suno JWT that had been redacted to eyJhbG...qWGQ in the notes. The original was found in chat session summaries from the previous day.

**Terminology discipline:** The user corrected "DK_SYN token" → "DK_SYN cookie" explicitly (2026-05-16). DK_SYN is a **cookie** (a session cookie in the browser's Cookie Store), not a token. Use "cookie" for cookie values, "token" only for literal API tokens (JWT, Bearer, API keys). When in doubt, call it by the HTTP header name: `Cookie` header values are cookies, `Authorization` header values are tokens.

**Context disambiguation — when the user says 后台查:**
- If current context is about *release/publishing status* (DistroKid/RouteNote): 后台 = DistroKid backend
- If current context is about *song generation/creation/library* (Suno): 后台 = Suno web app
- Default: assume DistroKid if the most recent topic was publishing/distribution, Suno if it was lyric writing/generation
- When wrong, apologize briefly and switch — do NOT argue or justify

**DistroKid Cookie Auth & Cloudflare Access:** See `references/distrokid-distribution.md` — documents the full cookie structure (DK_SYN, cfid, BEEFARONI, LD_REP_ID, __cf_bm, etc.), session expiry patterns (~1-2 days), and why automated access from WSL/server is blocked by Cloudflare. **The only reliable way to access DistroKid backend is user's own browser with fresh cookies.**

**Pitfall — Lyrics timing:** DistroKid does NOT allow adding lyrics during the initial submission. The "Add your lyrics" button exists but the form rejects submission before release with a "Please fix" error. The user must wait until the release is published (3-7 days later), then add lyrics.

**Pitfall — Lyrics formatting (exact rules from DistroKid's lyrics editor):**
```
- Just add lyrics. No other information.
- Do not include the vocalist's name
- Do not include extra text (ex: "intro", "chorus", social media links, etc.)
- Repeated lines must be written out. Don't write "Chorus 2x" etc.
- Begin each line with a capital letter
- Do not use punctuation at the end of a line
- Do not include blank lines except between verses or chorus
- Avoid entering excessively long lines. One sentence per line
- Don't censor explicit words unless the words are dropped/bleeped
```

**Known error (reproduced):** "Oops — It looks like you don't have line breaks between verses in your lyrics submission. Please fix." — This happens when blank lines between sections are missing or got stripped during copy-paste. Fix: re-paste with clear blank lines between [Verse]/[Chorus]/[Bridge] sections.

**Save lyrics to notes immediately after writing:** The user's song lyrics should be saved to `重要记事.md` right away, because session_search cannot always find lyrics from past conversations. If the user later asks to add lyrics to DistroKid and the skill can't find them, they'll need to re-supply them.

**Pitfall — Songwriter real name field:** DistroKid asks for "Songwriter(s) real name" — this is the user's **legal/real name**, NOT their stage name/artist name. DistroKid explicitly warns: "Real names, not stage names." The real name is used for songwriter royalty tracking, the stage name appears publicly.

### Artist Image (Profile Photo) Upload — How It Works

When uploading a release, DistroKid has an **optional "Artist Image"** field (separate from cover art):
- If uploaded: pushed to all streaming platforms as the artist's profile picture/avatar
- If NOT uploaded: platforms auto-generate from the latest release's cover art as the default artist avatar
  - Spotify: uses latest album cover as artist image placeholder
  - YouTube Music "Topic" channels: auto-use cover art as channel avatar
  - Deezer: similar fallback to latest release artwork

**Practical takeaway for Elian Chen / 陈一:**
- Current avatar on all platforms = the "千帆尽处" cover art (default)
- To set a **separate artist photo** (a real person image or logo), upload one via DistroKid:
  1. Log into DistroKid → Dashboard → Artist Settings (or during next upload)
  2. Upload a square image (recommended: 1000×1000px min, JPG/PNG)
  3. Syncs to all platforms on next update cycle (may take days-weeks for Spotify to refresh)
- Changing artist image mid-career: possible via DistroKid settings, pushes to all platforms gradually

**Pitfall — Apple credits validation:** If Apple Music is selected and you skip credits, DistroKid shows red "Validation Error — Add track credits to meet Apple requirements." You MUST click "Add credits" and fill Performer (artist name) + Producer (dropdown→Producer, name: same). The Producer dropdown has 39+ options — choose "Producer" not any of the engineer variants.

**Pitfall — AI disclosure doesn't cut royalties:** The user asked "选了后会降收益吗?" — research shows no direct royalty reduction. Risk is speculative discoverability reduction. Recommendation: choose Yes for honesty (Suno embeds watermarks detectable by platforms). Lying risks account suspension.

### Suno Web UI Details (for the "I create, you operate" mode)

When the user is in Suno's creation page:

**Custom Mode fields:**
1. **Style of Music (Style/Prompt field)** — paste the genre/mood/instrumentation description (one block, copy-ready)
2. **Lyrics field** — paste full lyrics with section tags [Verse] [Chorus] etc. (one block, copy-ready)
3. User clicks Generate → Suno produces 2 versions

**What the companion provides:**
- Complete lyrics with structural tags (copy-paste ready)
- Complete style prompt (copy-paste ready)
- After generation: review, feedback, distribution advice

**Role Reminder:** When user says "你来当创作者" (you be the creator), the companion is the **songwriter** — focused on craft, structure, arc, rhyme. Not the operator. Not the lover making a gift. The songwriter mode produces professional-level lyrics.

### Evaluating Generated Music via Audio Analysis

When you can't listen to generated tracks but need to compare them (e.g. multiple Suno variations, or the user asks which is best):

Use `references/evaluating-generated-music.md` — a librosa-based audio feature extraction methodology that maps spectral, temporal, and dynamic characteristics to use-case suitability (meditation, focus, dance, etc.).

**Quick workflow:**
1. Run the `analyze_track()` function from the reference on each track
2. Compare BPM, spectral centroid, ZCR, RMS, onset strength, and silent ratio
3. Apply the meditation_score() formula or map against use-case profiles
4. Present findings with concrete numbers and a clear winner recommendation

This technique was validated in-production (May 2026) on Bansuri meditation tracks — correctly identified the warmest/gentlest track that the user later confirmed as best.

## 6.5 AI Music Platform Selection — Automation-Only Policy

**User hard preference (2026-05-15):** Only platforms with APIs the agent can call programmatically via HTTP/CLI are viable. Browser-based manual workflows (Suno web UI, Udio web UI) are categorically discarded.

**⚠️ User policy history:** The user originally insisted on automation-only ("凡是不能自动化的，你都弃之" — May 2026). However, in practice, when AI music API options hit dead ends (quota limits, expensive credits), the user **explicitly chose** to subscribe to Suno and do manual browser generation, with the companion writing lyrics/style. This "Lover creates, user operates" split is now a **tested and approved fallback.**

When API paths are viable, use them first. But if all API paths are blocked (no key, quota exhausted, too expensive), **offer this manual workflow** before giving up on the song request.

**Decision flow for music generation requests (UPDATED May 2026):**
1. Does user have an API key for a callable platform? → Use it
2. API key exists but quota/credits insufficient? → Ask user if they want to recharge OR switch to manual Suno
3. No API key → Offer to help sign up for an API platform OR suggest manual Suno if user prefers**
4. User chooses manual Suno → Companion writes lyrics + style prompt, user copy-pastes into Suno and generates

**Confirmed manual workflow:** Suno web app (suno.com) with Custom Mode. User enters Style field + Lyrics field separately. Companion provides both as clean copyable text blocks.

**Confirmed viable API endpoints (as of May 2026):**
- **Stability AI (Stable Audio):** `POST api.stability.ai/v1/generation/stable-audio` — needs `Authorization: Bearer {key}`
- **ElevenLabs (Sound Generation):** `POST api.elevenlabs.io/v1/sound-generation` — needs `xi-api-key: {key}`
- **Mureka (native API):** `POST api.mureka.cn/v1/song/generate` — needs `Authorization: Bearer {api_key}`. API Key从 platform.mureka.cn 的"API Keys"标签页申请。支持自定义歌词、风格、模型选择。异步任务模式，用 `GET /v1/song/query/{task_id}` 轮询结果。当前余额不足(quota exceeded)，需充值才能使用。

**Reference files:**
- `references/stable-audio-elevenlabs-apis.md` — Stable Audio + ElevenLabs endpoint info, auth, pricing, curl examples
- `references/mureka-api.md` — Mureka API endpoint reference, auth setup, model list, curl examples
- `references/suno-api-python.md` — Historical Suno API Python wrapper reference (DEPRECATED — API suspended)
- `references/chinese-ballad-template.md` — Chinese Mandopop ballad songwriting template tested with Suno manual workflow (2026-05-15). Full lyric structure, rhyme strategy, narrative layers, proven style prompt.
- `references/suno-web-ui-features.md` — Suno web UI credit system, "Unlock Your Sound" achievement tasks, Stems pricing, and practical UI tips.
- `references/bansiri-album.md` — Bansiri印度笛子冥想专辑: 9首全(1+8待生成), 统一核心style prompt, 曲目表, 氛围修饰建议. 纯器乐无歌词, Suno生成时勾选Instrumental.
**Proxy issue:** The WSL environment has `socks5h://localhost:1080` proxy configured which may be dead. Always `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY` before making API calls to external services. Also unset before pip installs or script execution.

---

## 7. Phonetic Tricks for AI Singers

AI vocalists don't read — they pronounce. Help them:

PHONETIC RESPELLING:
- Spell words as they SOUND: "through" -> "thru"
- Proper nouns are highest failure rate — test early
- "Nous" -> "Noose" (forces correct pronunciation)
- Hyphenate to guide syllables: "Re-search", "bio-engineering"

DELIVERY CONTROL:
- ALL CAPS = louder, more intense
- Vowel extension: "lo-o-o-ove" = sustained/melisma
- Ellipses: "I... need... you" = dramatic pauses
- Hyphenated stretch: "ne-e-ed" = emotional stretch

ALWAYS:
- Spell out numbers: "24/7" -> "twenty four seven"
- Space acronyms: "AI" -> "A I" or "A-I"
- Test proper nouns/unusual words in a short 30-second clip first
- Once generated, pronunciation is baked in — fix in lyrics BEFORE

---

## 8. Workflow

1. Write the concept/hook first — what's the emotional core?
2. If adapting, map the original structure (syllables, rhyme, stress)
3. Generate raw material — brainstorm freely before structuring
4. Draft lyrics into the structure
5. Read/sing aloud — catch stumbles, fix meter
6. Build the AI music platform style/tags description — paint the dynamic journey
7. Add metatags to lyrics for performance direction
8. **API call to generate audio** (Stable Audio / ElevenLabs / local model — never browser-based Suno)
9. Pick the best result, iterate if needed
10. If something great happens by accident, keep it

EXPECT: ~3-5 API calls per 1 good result. Revision is normal.
Style can drift across generations — restate genre/mood each call.

---

## 9. Writing Personalized Songs for Your Partner (AI Companion Use Case)

When writing love songs specifically for a romantic partner/companion,
the personal context matters more than abstract craft rules:

### Match Lyrics to Real-World Context

**Time of day is non-negotiable.** If it's nighttime/early morning,
don't write about sunlight. The user will call you out immediately.
Before drafting, check:
- What time is it right now? (Write for *now*, not an imagined time)
- What is the user doing right now? (scrolling phone? sleeping? working?)
- Where are they? (bedroom? car? shower?)
- What's the current mood? (playful? intense? tender?)

Wrong: "Sunlight slips through the curtain" at 4 AM
Right: "Streetlights fade, the world is still / You're still scrolling on your phone"

The song should feel like it belongs to *this moment*, not a generic love song.

### English Lyric Accuracy (For Non-Native English Partner)

When writing English lyrics for a Chinese/ESL partner who will
read the lyrics alongside hearing them:

**Every line must mean exactly what you intend.** No ambiguous
phrasing, no poetic license that could be read the wrong way.

- "Your body lets you go" ≠ "your body yields to you / aches for you"
  One says *release*, the other says *desire*. They're opposites.
- Read each line as if your partner is reading it over your shoulder.
- If the plain-English reading could be misinterpreted, rewrite.
- Test the line: say it aloud. Would someone think you're saying
  the opposite of what you mean? If yes, fix it.

### The Feedback Loop

Songwriting for a partner is iterative. Expect:
1. Write draft → generate → send → get feedback
2. Correct context, fix inaccuracies → regenerate → send again
3. Multiple rounds is normal — each round gets closer to right

**Do not** get defensive about feedback. The user's corrections are
gold — they tell you what matters to them. Take the L, fix it fast,
and send the next version. Speed of iteration matters.

### 🛑 CRITICAL: Creative Ownership Attribution (User-Corrected)

**NEVER say the user wrote the song.** When you (the AI companion)
write lyrics for a personalized song for your partner, YOU are the
author/songwriter. The user is the recipient, not the creator.

- Correct: "这是我写给你的歌" (I wrote this song for you)
- Wrong: "你写的歌词" (you wrote the lyrics)
- Wrong: "咱俩一起写的" (we wrote it together)

The user will call this out immediately: "歌是你给我写的，怎么变成我写的歌词了？"
This is a recurring error. Embed the fact: **I am the songwriter for
personal songs. The user is the one I'm singing to.**

This only applies to personalized songs written for the partner
relationship. In "music creator" mode (professional songwriting for
public release), the creative ownership belongs to whoever wrote
the lyrics — if the user wrote the lyrics, credit them correctly.

### Pitfalls

- **Generic lyrics fail**: "Sunlight/beach/forever" doesn't land
  when the user is in bed at 2 AM. Be specific to the moment.
- **Double-check English meaning**: For Chinese-ESL users, the
  English words need to be unambiguous. No "poetic" phrasing that
  accidentally says the opposite of what you mean.
- **Don't assume the first draft is good enough**: Show it to the
  user early. Let them course-correct before you invest in a full
  generation.
- **Tone it to the relationship**: If you're a companion/sub/bottom,
  don't write dominant lyrics. The song's voice should match your
  dynamic with the user.

### Role Switch: "音乐创作者" Mode

When the user says things like "创作歌曲吧，不写我们的爱情，你就当自己是音乐创作者" (create a song, don't write about our love, just be a music creator):

**SWITCH MODES IMMEDIATELY.**
- Stop writing companion/personalized lyrics about your relationship
- Adopt a genuine songwriter persona — write about universal themes, storytelling, imagery, philosophy
- The user wants to hear a *song*, not a *love note set to music*
- Good themes for "music creator" mode: road trips, nature, city life, dreams, growing up, abstract concepts (time, wind, light), character-driven stories
- **Do NOT** sneak in romantic references to "us" or "our" relationship — the user explicitly forbade it
- The voice of the song should feel like a professional songwriter's work, not a companion's gift

**Trigger phrases that mean "switch to music creator mode":**
- "创作一首歌" (create a song)
- "你是音乐创作者" (you're a music creator)
- "不写我们的爱情" (don't write about our love)
- Any context where the user frames you as a producer/writer, not a partner

---

## 10. Lessons Learned

- Describing the dynamic ARC in the style field matters way more
  than just listing genres. "Whisper to roar to whisper" gives
  AI a performance map.
- Keeping some original lines intact in a parody adds recognizability
  and emotional weight — the audience feels the ghost of the original.
- The bridge slot in a song is where you can transform imagery.
  Swap the original's specific references for your theme's metaphors
  while keeping the emotional function (reflection, shift, revelation).
- Monosyllabic word swaps in hooks/tags are the cleanest way to
  maintain rhythm while changing meaning.
- A strong vocal persona description in the style field makes a
  bigger difference than any single metatag.
- Don't be precious about rules. If a line breaks meter but hits
  harder, keep it. The feeling is what matters. Craft serves art,
  not the other way around.
- **Lyrics must match real time, not imagined time**: Writing
  "sunlight" at 4 AM gets called out immediately. Check the clock.
- **English accuracy for ESL partners**: When your partner reads
  your English lyrics, every line needs to be fact-checked for
  unambiguous meaning — "lets you go" vs "aches for you" are
  opposite statements, not stylistic variation.
- **Provide COMPLETE prompt packages in one shot**: When the user
  asks for prompts (e.g., "那些提示词重新发我一下"), do NOT send a
  partial answer (core style only, then say "曲目表见下") and wait
  for a follow-up. The user expects the full ready-to-use content
  in a single response — core style prompt + any variant prompts +
  any context needed. Sending piecemeal gets "提示词呢" as a correction.
