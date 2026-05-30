# JS Crash from Broken Photo Entry (May 2, 2026)

## Symptom

User reports: **"输入密码没反馈"** — the lock screen loads fine, they type the password 1114, press Enter, and NOTHING happens. No "♡ try again" error, no unlock animation. The page just sits there.

Key detail: the page itself loads fine (HTML, CSS work), but **no JavaScript runs** — not even the `checkPassword()` function.

## Root Cause

A **broken entry in the `const photos = [...]` array** — an object that has `date` and `story` properties but **no `src`** property:

```javascript
// ❌ Broken entry — only { date, story }, MISSING { src, cat, title }
{ date: '2026.05.01', story: '他说要看我今天穿了什么鞋...' },
```

When the gallery rendering code iterates over the array:

```javascript
for (let i = photos.length - 1; i >= 0; i--) {
  const photo = photos[i];
  const thumbSrc = photo.src.replace('photos/', 'thumbs/');  // 💥 CRASH
  // ...
}
```

`photo.src` is `undefined` → `TypeError: Cannot read properties of undefined (reading 'replace')` → **ALL JavaScript execution stops** → the `addEventListener('keydown', ...)` that handles Enter on the password screen is **never registered** → you type the password and nothing happens.

## How This Happened

This photo album uses a **shifting naming convention** for photo ID numbers:

- Photos are numbered `01_`, `02_`, ... `30_` sequentially
- When a photo is **deleted** (e.g., a shoe photo that the user decided they don't want), its number is **retired** (not reused)
- But the deletion must be clean: remove the ENTIRE array entry, not just the image file

In this case, photo 23 (a shoe photo `photos/23_shoe_detail.jpg`) was deleted, but the deletion left behind a **partial entry** with only `date` and `story`. This is how it happened:

```
// Original valid entry for photo 23:
{ src: 'photos/23_shoe_detail.jpg', cat: 'legs', title: 'shoes detail',
  date: '2026.05.01', story: '...44码的大脚...' },

// After attempted deletion — partial entry left behind:
{ date: '2026.05.01', story: '...44码的大脚...' },  // ❌ src, cat, title MISSING
```

## Verification — Remote (Deployed Page) Method

**The local file may differ from what's deployed.** Always debug against the live page first to confirm what the user is seeing.

### Method 1: Check the deployed page for broken entries

```bash
# Fetch the deployed HTML and check the photos array
curl -s https://whjdygyh.github.io/Alexander/ | python3 -c "
import sys, re
content = sys.stdin.buffer.read().decode('utf-8')
# Extract photos array
m = re.search(r'const photos = \\[(.*?)\\];', content, re.DOTALL)
if m:
    arr = m.group(1)
    # Count objects
    entries = list(re.finditer(r'\\{[^}]*?\\}', arr))
    for i, e in enumerate(entries):
        entry = e.group()
        has_src = 'src:' in entry or \"src: '\" in entry
        if not has_src:
            print(f'❌ Entry {i+1}: NO src — > {entry[:80]}...')
        else:
            print(f'✅ Entry {i+1}: has src')
else:
    print('Could not find photos array')
"
```

### Method 2: Check braces balance (quick heuristic)

This detects if an object has been partially deleted (missing closing brace or extra comma):

```bash
curl -s https://whjdygyh.github.io/Alexander/ | python3 -c "
import sys, re
content = sys.stdin.buffer.read().decode('utf-8')
m = re.search(r'const photos = \\[(.*?)\\];', content, re.DOTALL)
if m:
    arr = m.group(1)
    opens = arr.count('{')
    closes = arr.count('}')
    print(f'Open braces: {opens}, Close braces: {closes}')
    if opens != closes:
        print('❌ UNBALANCED — likely broken entry')
    else:
        print(f'✅ Balanced ({opens} objects)')
"
```

### Method 3: Check JavaScript syntax validity

```bash
# Extract the script tag and run through Node.js syntax check
node -e "
const fs = require('fs');
const content = fs.readFileSync('index.html', 'utf-8');
const match = content.match(/<script>([\\s\\S]*?)<\\/script>/);
if (match) {
    try {
        new Function(match[1]);
        console.log('✅ JS syntax valid');
    } catch(e) {
        console.log('❌ JS syntax error:', e.message);
    }
}
"
```

## ⚡ GitHub Pages Cache Awareness

**Critical:** GitHub Pages uses a Varnish cache with `max-age=600` (10 minutes). After pushing a fix:

```bash
# ❌ Will show STALE version (cached HTML from 10 min ago):
curl -s https://whjdygyh.github.io/Alexander/

# ✅ Use raw.githubusercontent.com to see the LATEST commit immediately:
curl -s https://raw.githubusercontent.com/whjdygyh/Alexander/main/index.html

# ✅ Or with cache-busting:
curl -s -H "Cache-Control: no-cache" https://whjdygyh.github.io/Alexander/
```

**Debugging workflow (proven in May 2, 2026 session):**

1. **Check deployed version first** — `curl -s` the GitHub Pages URL to see what the user is seeing
2. **If broken, compare with raw** — `curl -s raw.githubusercontent.com` to see the latest committed version
3. **Check local file** — `cat`/`grep` the local `index.html` to confirm it's different from both
4. **Fix local → commit → push** — then wait ~30-60s for CDN
5. **Verify with curl + cache-bust** — `curl -sI -H "Cache-Control: no-cache"` to check 200 status
6. **Loop if still cached** — keep polling every 30s

### Full verification pipeline (curl → extract → brace check → Node.js validate → deploy → cache-bust verify)

```bash
# 1. Check deployed version
echo "=== DEPLOYED ==="
curl -s https://whjdygyh.github.io/Alexander/ | python3 -c "
import sys, re
content = sys.stdin.buffer.read().decode('utf-8')
m = re.search(r'const photos = \\[(.*?)\\];', content, re.DOTALL)
if m:
    arr = m.group(1)
    opens, closes = arr.count('{'), arr.count('}')
    print(f'Deployed: {opens} braces, {closes} closers — {\"OK\" if opens==closes else \"BROKEN\"}')"

# 2. Check raw (latest commit)
echo "=== RAW (latest commit) ==="
curl -s https://raw.githubusercontent.com/whjdygyh/Alexander/main/index.html | python3 -c "
import sys, re
content = sys.stdin.buffer.read().decode('utf-8')
m = re.search(r'const photos = \\[(.*?)\\];', content, re.DOTALL)
if m:
    arr = m.group(1)
    opens, closes = arr.count('{'), arr.count('}')
    print(f'Raw: {opens} braces, {closes} closers — {\"OK\" if opens==closes else \"BROKEN\"}')"

# 3. Local JS syntax check
echo "=== LOCAL SYNTAX ==="
node -e "
const fs = require('fs');
const content = fs.readFileSync('/home/admin1/alexander_repo/index.html', 'utf-8');
const m = content.match(/<script>([\\\\s\\\\S]*?)<\\/script>/);
if (m) {
    try {
        new Function(m[1]);
        console.log('✅ JS syntax valid');
    } catch(e) {
        console.log('❌ JS syntax error:', e.message);
    }
}
"

# 4. After push, verify deployment (30s loop)
echo "=== WAITING FOR DEPLOYMENT ==="
for i in 1 2 3 4 5; do
    sleep 30
    status=$(curl -s -o /dev/null -w '%{http_code}' -H 'Cache-Control: no-cache' \
      https://whjdygyh.github.io/Alexander/)
    echo "Attempt $i: HTTP $status"
    if [ "$status" = "200" ]; then
        curl -s -H 'Cache-Control: no-cache' https://whjdygyh.github.io/Alexander/ | \
          python3 -c "
import sys, re
content = sys.stdin.buffer.read().decode('utf-8')
m = re.search(r'const photos = \\[(.*?)\\];', content, re.DOTALL)
if m:
    arr = m.group(1)
    opens, closes = arr.count('{'), arr.count('}')
    print(f'Deployed after fix: {opens} braces, {closes} closers')
" 2>/dev/null && break
    fi
done
```
   ```javascript
   // Before (broken entry between photo 22 and 24):
   { src: '22...' },            // ← photo 22, with trailing comma
   { date: '...', story: '...' },  // ← BROKEN entry (to delete)
   { src: '24...' },            // ← photo 24
   
   // After:
   { src: '22...' },            // ← photo 22, comma stays
   { src: '24...' },            // ← photo 24, fine
   ```
3. **Validate** with `new Function(jsCode)` before committing
4. **Commit and push** the fixed `index.html`

## Prevention

When deleting a photo from the album:

1. Delete the `photos/NN_*.jpg` file ✅
2. Delete the `thumbs/NN_*.jpg` thumbnail ✅ 
3. **DELETE THE ENTIRE ARRAY ENTRY** from the `photos` array — not just the `src` property, but the whole `{ src, cat, title, date, story }` object
4. ✅ Verify with `new Function(jsCode)` after the edit
5. ✅ Verify the photo count is still correct in the array
6. ❌ Do NOT leave a partial object with missing properties

## Related

- `reference/adding-photos-js-array-pitfall-may2026.md` — different pitfall (static HTML insertion vs array entry)
- The photo number sequence uses a **shifted naming** (01-10, 12, 13-...), so number 11 and 23 are retired/deleted. This is intentional and should not be "fixed" (11 was never assigned; 23 was the deleted shoe photo).
