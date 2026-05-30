# Phantom Entries & Album Sync — May 2026 Debugging Narrative

## The Problem

User generated photos through the lifecycle (gemini → save → git push), but the deployed album showed only 37 of the expected 48+ photos. Three types of failures were discovered:

### Type 1: Files on Disk, Missing from Array

`28_summer_cafe_americano.jpg` and `face_profile.jpg` existed in `photos/` but were NEVER added to the JS array in `index.html`. They showed up in `=== MISSING from index.html ===` section of the completeness check.

**Root cause:** New photos were being generated and saved to disk, but the agent forgot to add them to the `const photos = [...]` array in `index.html`. The photo file existed and was accessible via direct URL, but invisible in the gallery grid.

**Fix:** Append the photo entry to the JS array, generate thumbnail, commit, push, deploy.

### Type 2: Phantom Entry (Array Entry, No File)

`31_sofa_daydream.jpg` appeared in the JS array but had NO corresponding file on disk in `photos/`. The thumbnail `thumbs/31_sofa_daydream.jpg` also existed (leftover from when the file may have existed).

**Root cause:** Historical artifact — the file was likely deleted or renamed in a previous session without updating the array.

**Fix:** Remove the entire array entry (and its trailing comma) from `index.html`, delete orphaned thumbnail from `thumbs/`.

### Type 3: Wrong Position in File (Broken JS Structure)

`41_waiting_you_evening.jpg` was present in `index.html` but at **line 1038**, inside a JS function body near `delete flags[photoId` — NOT inside the `const photos = [...]` array block. The entry looked syntactically correct (matching the array format) but was in the wrong scope, making it invisible to the gallery renderer.

**Root cause:** The agent editing the HTML file selected the wrong context — a "Search and Add" operation matched a similar-looking JS section and placed the entry there instead of inside the array.

**Fix:** Move the entry from the function body into the `photos` array. Remove the stray entry code. Verify the function body is intact.

## Diagnostic Commands

### Bidirectional completeness check

```bash
cd /home/admin1/.hermes/profiles/lover/home/Alexander

# Files on disk NOT in array
comm -23 \
  <(ls photos/*.jpg photos/*.jpeg 2>/dev/null | sed 's/.*\\///' | sort) \
  <(grep -oP "photos/\\K[^\"']+" index.html | sort)

# Phantom entries: in array but no file
while read f; do
  if [ ! -f "/home/admin1/.hermes/profiles/lover/home/Alexander/photos/$f" ]; then
    echo "⚠️ PHANTOM: $f"
  fi
done < <(grep -oP "photos/\\K[^\"']+" index.html)

# Check entry position: last 5 photo references in file
grep -n "photos/" index.html | tail -5
# All entries should be between `const photos = [` and `];` — not after, not in a function
```

### Deployed vs Local comparison

```bash
# Compare MD5 of deployed HTML vs local
curl -s "https://alexander-album.pages.dev/" | md5sum
md5sum index.html
# If different → site is stale

# Check deployed photos count
curl -s "https://alexander-album.pages.dev/" | grep -oP "photos/\\K[^\"']+" | sort -u | wc -l
```

## Key Lessons

1. **Run completeness check BEFORE every album edit** — not after. Catching issues before you make changes means fewer rollbacks.

2. **Check BOTH directions** — files without array entries AND array entries without files. The original check only went one way.

3. **Check entry POSITION** — not just presence in the file. A syntactically valid entry in the wrong scope (inside a function body instead of the array) is invisible. Use `grep -n` to see where entries land.

4. **Cloudflare Pages auto-deploy may not trigger** — git push to GitHub doesn't always cause Cloudflare to rebuild. After commit+push, verify by comparing deployed HTML MD5 with local. If stale, deploy manually via `wrangler pages deploy` (requires API token).

5. **Count verification** — After all fixes, `photos/` disk count should equal array entry count. If mismatched, re-run both checks.
