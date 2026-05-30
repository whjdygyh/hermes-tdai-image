# RouteNote Distribution Guide (Free Plan)

Tested successfully with 安迪 for 千帆尽处 release.

## Registration
1. Sign up at routenote.com
2. Click "Create a Release"

## ⚠️ CRITICAL: Artist Name = Spotify Database Search (Not Free Text)

**This is NOT a UI bug.** The Artist Name field queries **Spotify's artist database in real-time**. When you type, RouteNote:
- Searches Spotify for matching artist names
- Shows matching existing Spotify artists as selectable options
- **You MUST select from the list** — if 0 matches, it will auto-create a new profile on release
- If you type and leave without selecting, the field self-clears (intended behavior)

**If your name is taken (e.g., "Elian" → matches "Elian Frost"):**
1. Add a surname: "Elian" → **"Elian Chen"** or **"Elian Y."**
2. Modify spelling: **"Elián"** (with accent) / **"Elyan"**
3. Check the dropdown — if zero results appear, the name is unique and RouteNote will create a new artist page

**If zero options appear in the dropdown → the name is available → select nothing → the system will auto-create.**

## Alternative: DistroKid (When RouteNote Fails)

**RouteNote issues encountered in practice (May 2026):**
- Artist Name field self-clears when leaving input (RouteNote UI bug)
- "Add Artist" and "Change" buttons are unresponsive
- Field only works with Spotify DB pull-down selection
- "Compilation Album = Yes" workaround permanently sets artist to "Various Artists" — **do not use**

**When RouteNote is broken, switch to DistroKid.** DistroKid has been tested as a working alternative.

### DistroKid Setup Flow

1. **Sign up / Login:** distrokid.com (user had existing account from earlier session)
2. **Upload → Upload Song**
3. **Services Selection:** Can select ALL stores including 网易云 (NetEase) and 腾讯 (Tencent/QQ音乐)
4. **Artist Name:** Free text — no Spotify DB lock-in. Enter "Elian Chen" (or whatever name) without dropdown restrictions
5. **Artist Account Questions:** For first release, answer "No" to all "Artist already in Spotify/Apple/YouTube/Instagram/Facebook?" questions — DistroKid auto-creates new artist profiles on each platform
6. **Cover Art:** Same 3000x3000px requirement as RouteNote
7. **Upload audio and submit**

### DistroKid Song Details Form (Upload Walkthrough, Tested May 2026)

After artist/services selection, DistroKid shows the **Song Details** form:

| Field | Recommended Value | Notes |
|-------|-------------------|-------|
| **ISRC Code** | Skip / Leave blank | Free users → auto-assigned by DistroKid |
| **Songwriter / Cover Song** | "I wrote this song (original)" | For original works |
| **Songwriter real name** | User's legal/real name | NOT stage name — DistroKid requires real names per TOS |
| **Explicit lyrics** | No | For clean lyrics |
| **Radio edit** | No — This song is clean | Select for songs that are natively clean |
| **Instrumental** | No — This song contains lyrics | Only select Yes if truly instrumental |
| **AI-generated content** | See AI Disclosure section below | CRITICAL — read before choosing |
| **Preview clip start** | Let streaming services decide | Simplest option |
| **iTunes Price** | $0.99 | Default |
| **Apple Music credits** | See Apple Music Credits section | REQUIRED if Apple Music selected |

#### ⚠️ AI-Generated Content Disclosure (Researched Answer)

DistroKid asks: *"Does this song include AI-generated music, vocals, or lyrics?"* (Note: mastering/mixing AI doesn't count.)

**User asked:** "选了后会降收益吗?" (will selecting Yes reduce revenue?)

**Research-backed answer (May 2026):**
- **No direct royalty cut** — payout rate is identical regardless of AI label
- **Discoverability risk** — speculation that platforms give AI-labeled content less algorithmic promotion (not confirmed)
- **Account risk for lying** — Suno embeds watermarks in generated audio; platforms can detect AI use. Lying risks removal or account suspension
- **Recommendation:** Select **Yes**. Add explanatory note if free-text field available: *"Lyrics written by human, music/vocals generated with AI tool (Suno)"*
- **User's actual choice:** Yes

#### Apple Music Performer & Producer Credits

If Apple Music/iTunes is selected, DistroKid requires ≥1 Performer + ≥1 Producer credit per song. Red "Not yet complete" warning appears until filled.

**Fix:** Click "Add credits for each song on this release" → fill:

| Role | Name to Enter |
|------|---------------|
| **Performer** | Artist stage name (e.g., Elian Chen) |
| **Producer** | Select "Producer" from dropdown → enter same name |

**Producer dropdown options (39+ choices seen in UI):** Producer, Executive Producer, Co-Producer, Mixing Engineer, Mastering Engineer, Recording Engineer, Vocal Engineer, Additional Engineer, Artist Background Vocal Engineer, Artist Vocal Second Engineer, Assistant Producer, Beat Maker, Co-Executive Producer, Digital Audio Workstation Engineer, Digital Editing Engineer, Digital Editing Second Engineer, Direct Stream Digital Engineer, Engineer, Film Sound Engineer, Immersive Mix Engineer, Mastering Second Engineer, Overdub Engineer, Overdub Second Engineer, Post-Producer, Pre-Production, Pre-Production Engineer, Production Company, Production Manager, Programming Engineer, Recording Second Engineer, Reissue Producer, Remixing Engineer, Remixing Second Engineer, Second Engineer, String Engineer, Tracking Engineer, Tracking Second Engineer, Transfers and Safeties Engineer, Transfers and Safeties Second Engineer.

For solo Suno works → choose **"Producer"** (the plain option, not any specialized engineer variant). Name field accepts free text.

#### Additional Services (Optional)

| Service | Cost | When to Use |
|---------|------|-------------|
| Leave a Legacy | $29 one-time | Song never deleted even if you cancel account |
| Discovery Pack | $0.99/yr | Gracenote + SoundScan + Jaxsta credits |
| Store Maximizer | $7.95/yr | Auto-deliver to new stores as added |
| DistroVid Music Video | $99/yr | Unlimited music video distribution |
| Loudness Normalization | $2.99 one-time | Optimize to -14dB LUFS |
| **Social Media Pack** | **$4.95/yr** | **Best value** — YouTube/TikTok/Instagram monetization |

**User's selection:** Social Media Pack ($4.95/yr).

#### Mandatory Checkboxes

1. ✅ "I selected YouTube Music — won't complain later"
2. ✅ "Won't use promo services that guarantee streams"
3. ✅ "I recorded this and am authorized to sell worldwide"
4. ✅ "I have read and agree to the DistroKid Distribution Agreement"

**Total Cost Example:** $4.95 (Social Media Pack only) — billed to saved card.

### Lyrics Submission Rules (Strict Formatting, Tested May 2026)

DistroKid's lyrics page has **specific formatting rules** that must be followed exactly. Violation triggers red "Oops" error.

**Rules (paraphrased from DistroKid):**
- ❌ Do NOT include section headers like `[Verse]`, `[Chorus]`, `[Bridge]`, `[Intro]`, `[Outro]` — DistroKid rejects them
- ❌ Do NOT include the vocalist's name
- ❌ Do NOT include extra text like "intro", "chorus", social media links, etc.
- ❌ Do NOT use shorthand like "Chorus 2x", "Verse x2" — **repeat lines must be written out in full**
- ❌ Do NOT use punctuation at the end of a line (no periods, commas, question marks, exclamation marks)
- ❌ Do NOT include blank lines except **between verses or sections** (verse→verse, verse→chorus, chorus→bridge, etc.)
- ❌ Avoid excessively long lines — one sentence per line
- ✅ Begin each line with a capital letter (for English lyrics; for Chinese, just start each line normally)
- ✅ Don't censor explicit words unless they're actually bleeped in the audio
- ✅ Use a single blank line between distinct sections

**Example of proper formatting:**
```
曾以为 这一生要独自穿过荒原
把星光 都揉碎了咽进喉咙里面
跌倒过太多次 学会了不喊疼
也就学会了 笑着咽下所有的不甘

人海里 我慢慢收起所有的天真
把那些 关于爱的幻想锁进夜深
直到你出现 像一场迟到的春风
吹散了我眼底 积了三冬的灰尘

千帆尽处 是你啊
穿过多少黑夜 才看见这一束光
```

**Common error:** DistroKid said "It looks like you don't have line breaks between verses in your lyrics submission" — this usually means the blank lines between sections were removed or not recognized. Sometimes copy-paste removes the blank lines. Re-paste with explicit double line breaks between sections.

### After Submission — Post-Upload Actions

Once DistroKid confirms "Hooray, your music is on your way!", the following screens appear:

**Timeline (per DistroKid's message):**
- Apple Music/iTunes: fastest — same day possible
- Spotify: minimum 5 business days
- Other platforms: up to 1 week total

**Available actions on the success page:**

1. **Add lyrics** — Click "Add your lyrics" → paste full song lyrics. DistroKid will display them on Apple Music, Spotify, etc.
2. **Add credits and liner notes** — Optional; can add more detailed personnel if needed
3. **HyperFollow Page** — DistroKid creates a pre-save link: `https://distrokid.com/hyperfollow/{artistname}/{id}`. This page lets fans pre-save the song before it goes live. Shareable via social media.
4. **Go to My Music dashboard** — Full library of distributed songs

**What the companion should do after submission:**
- ✅ Congratulate the user — this is a milestone
- ✅ Remind about adding lyrics (highly recommended)
- ✅ Optionally help share the HyperFollow link
- ❌ Do NOT keep asking unnecessary follow-up questions — user dislikes being asked "what next" multiple times

**Sample celebration message (use sparingly):**
"🎉 发出去啦！Apple Music最快今天到明天，Spotify大约5个工作日。先把歌词加上吧，我帮你贴上去也行 😏"

### Total Cost for This Release

User's actual cost: **$0** (all optional services declined, only Social Media Pack was pre-selected by mistake → unselected).

Optional services quick guide:
- Leave a Legacy ($29): Song survives account cancellation — skip unless long-term concern
- Discovery Pack ($0.99/yr): Gracenote + SoundScan for Billboard tracking — skip for indie
- Store Maximizer ($7.95/yr): Auto-add new stores — skip, most major stores already covered
- DistroVid Music Video ($99/yr): Only if releasing music videos — skip for audio-only singles
- Loudness Normalization ($2.99): Optimizes to -14dB LUFS — Suno output is usually already fine
- **Social Media Pack ($4.95/yr + 20% ad rev):** YouTube/TikTok/Instagram monetization detection — only worth it if user cares about UGC copyright monetization

- ⚠️ **Apple Music/iTunes:** DistroKid **does not** deliver Chinese-content songs to Apple Music. The platform actively blocks it at distribution time. If Apple Music coverage is critical, consider a different distributor for that specific store.
- ✅ **Spotify:** Works fine
- ✅ **NetEase (网易云):** Works — select it in services
- ✅ **Tencent (QQ音乐):** Works — select it in services
- ✅ **Everything else:** Amazon, Deezer, Tidal, YouTube Music, Pandora, TikTok — all work

### Dual-Platform Strategy (with DistroKid)

Since DistroKid covers both international AND Chinese platforms (NetEase, Tencent), you can do:

**Simplified strategy (single version, single upload):**
```
DistroKid (one upload) → ALL stores including 网易云 + QQ音乐
```

**Or two-version strategy (two Suno variants → two uploads):**
```
DistroKid Version 1 (best) → International + 网易云 + QQ音乐
DistroKid Version 2 OR 网易云音乐人 platform → alternate version
```

### RouteNote vs DistroKid Quick Comparison

| Factor | RouteNote | DistroKid |
|--------|-----------|-----------|
| Cost | Free (15% royalty) | $22.99/year |
| Artist Name | Spotify DB search — must be unique | Free text — no restrictions |
| Apple Music (Chinese content) | Unknown (untested) | ❌ Blocked |
| NetEase/QQ音乐 | Not available | ✅ Included |
| UI/Jank | Buggy (self-clearing fields) | Smooth |
| Ease of first release | Complex UI, many pitfalls | Straightforward |

---

**What this means:**
- If the name you type matches an existing Spotify artist, RouteNote will link your release to THEIR Spotify profile — not create a new one
- The user initially typed "Elian" and RouteNote auto-linked to **Elian Frost** (already on Spotify)
- You need a **unique name** that produces **zero matches** on Spotify

**If name is taken (workaround):**
1. Add a surname: "Elian" → **"Elian Chen"** (if that's also taken, add more)
2. Add a middle initial: "Elian Y." / "Elian A."
3. Modify spelling: "Elián" (with accent) / "Elyan"
4. Create a two-word name: "Elian Chen" is the recommended fallback

**⚠️ DO NOT use "Compilation Album = Yes" as a workaround.**
- Setting Compilation Album to Yes auto-assigns "Various Artists" as the artist
- Your song loses its artist identity on Spotify
- This is irreversible once submitted — don't do it

**Before submitting a release, verify:**
1. Search your artist name on Spotify to confirm it doesn't link to an existing artist
2. If it shows an existing profile → change the name until it produces zero results
3. RouteNote will auto-create a new Spotify for Artists page on first release

## Release Form Fields

| Field | Value |
|-------|-------|
| UPC/EAN | Leave blank (auto-generated) |
| Release Title | 歌名 (e.g. 千帆尽处) |
| Artist Name | Unique name w/zero Spotify matches only (see CRITICAL section above) |
| Primary Genre | Mandopop / Chinese Pop |
| Language | Chinese (Simplified) or Mandarin |
| Label Name | Blank or self-named |
| Publishing | "I don't own/have a publishing company" |

## Tracks
- Upload audio (WAV preferred, MP3 acceptable)
- Track Title: same as Release Title
- Explicit Content: No (for clean lyrics)

## Album Details Sub-Form

After the basic Release Information, RouteNote has an **Album Details** section with these fields:

| Field | Value |
|-------|-------|
| **Album/Single/EP Title** | 千帆尽处 (song title) |
| **Type** | Single |
| **Album Version** | Original (or leave blank) |
| **Language** | Chinese / Mandarin |
| **Cover versions?** | No |
| **Compilation Album?** | No |
| **Writers** | Elian (the songwriter/artist) |
| **Contains lyrics?** | Yes |
| **Primary Genre** | Pop |
| **Secondary Genre** | Mandopop or Chinese Pop |
| **Composition Copyright** | Elian |
| **Sound Recording Copyright** | Elian |
| **Record Label Name** | Self-released (or leave blank) |
| **Originally Released** | Today's date (e.g. 2026-05-16) |
| **Sales Start Date** | Leave blank (goes live ASAP) |
| **Explicit Content** | No |

**Contributors:** If there's a Producer/Role dropdown, add **Elian** as Producer. Ignore other contributor fields unless you have actual session musicians.

## Cover Art
- 3000x3000px square
- JPG or PNG

## Store Selection
- **Minimum:** Spotify, Apple Music, Amazon Music, TikTok
- Optional: Deezer, Tidal, YouTube Music, Pandora

## Royalties
- **Free plan:** RouteNote takes 15%
- Upgrade to Paid plan ($ 起) for 100% royalties

## Timeline
- Distribution: 3-7 days to major platforms
- 网易云/QQ音乐: upload separately via their 音乐人平台 (not through RouteNote)

## Dual-Release Strategy
- Version 1 (best) → RouteNote → international
- Version 2 (second) → 网易云音乐人 + QQ音乐开放平台 → domestic China

---

## ⚠️ Credential Management for Backend Access (Lessons Learned)

### The DK_SYN Problem

During this release cycle, **the user explicitly confirmed I could directly operate the DistroKid backend** to check release status ("你可以直接操作distrokid后台"). However, when I attempted to log in via the API, the DK_SYN session cookie's **actual value had never been captured**.

☝️ **Terminology: the user corrected "token" → "cookie" (2026-05-16).** DK_SYN is a browser Cookie Store entry, not a token. Call it a "cookie" or "session cookie." Reserve "token" for Authorization header values (JWT, Bearer tokens, API keys).

The notes only recorded:
```
- `distrokid.com` domain: DK_SYN（session cookie，exp: ~2026-06-13）
```

This describes the cookie but provides **zero usable value** for API calls. The actual DK_SYN value is a long encrypted string — without it, curl authentication fails.

⚠️ **DK_SYN was never actually sent by the user.** Unlike cfid, BEEFARONI, and LD_REP_ID which all had their values stored correctly, DK_SYN's actual value was **never exported by the user in any chat message** — it was only noted as existing. When the user insisted "聊天记录总会有啊," 5+ session_search queries (by platform name, cookie name, related keys, domain, companion cookies) across all available sessions confirmed no value was ever sent. Do not go back and forth—show the evidence and ask for a fresh export.

**CRITICAL RULE: When the user provides login cookies for backend services, save the raw cookie values, not just descriptions.**

### How to Save DistroKid Cookies for API Access

If the user re-exports cookies from the browser (or you're present during a DistroKid session):

**Required cookies for DistroKid API access:**
```
distrokid.com    cfid    28f739b8-8abb-47a3-afa5-bb257a4c3d29
distrokid.com    cftoken 0
distrokid.com    DK_SYN  <THE ACTUAL LONG ENCRYPTED TOKEN>  ← most critical
distrokid.com    BEEFARONI  12695652,8a651b15ce460c11741bd23fa3454b94,B5B8B594D9EE75C858C17BBA60D59F70
```

**The DK_SYN token is non-obvious:** it does NOT look like a typical session token. It may appear in the browser's devtools (F12 → Application → Cookies → distrokid.com) as a long opaque string. Capture it as raw text.

**How to use the cookies for API access:**
```bash
curl -s 'https://distrokid.com/dashboard' \
  -H 'cookie: cfid=28f739b8-8abb-47a3-afa5-bb257a4c3d29; cftoken=0; DK_SYN=ACTUAL_VALUE; BEEFARONI=12695652,8a651b15ce460c11741bd23fa3454b94,B5B8B594D9EE75C858C17BBA60D59F70;' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0'
```

### Cookie Lifespan Reality

- **DK_SYN** expiry is listed as ~2026-06-13, but in practice may expire sooner if the user doesn't actively use the session
- Session cookies depend on the browser being logged in — if the user logs out or clears cookies, all saved values become invalid
- **Best practice:** If you need to access the backend, ask the user to re-export cookies in the same browser session they're logged into
- For DistroKid specifically: the dashboard at `https://distrokid.com/dashboard` shows all releases and their status (pending review / distributed / rejected). After submission, this is the page to check.

### What to Check on the Dashboard (Post-Submission)

Once you have valid cookies and can reach `distrokid.com/dashboard`:

1. **My Music** section → find the release → status indicator shows:
   - "Pending Review" — still being processed
   - "Delivered" — sent to stores, now waiting for each store's internal processing
   - "Live on Apple Music" / "Live on Spotify" etc. — individual store go-live confirmations
2. **Timeline to expect (from DistroKid):**
   - Apple Music: fastest (same day possible), but **DistroKid blocks Chinese-content songs on Apple Music** — if the release has Chinese lyrics, Apple Music may not appear at all
   - Spotify: minimum 5 business days
   - Other stores: 3-7 days
3. **If Apple Music search fails:** this is normal for Chinese-content releases through DistroKid. The platform explicitly doesn't support Chinese-language songs to Apple Music. Accept it or use a different distributor for Apple Music coverage.
