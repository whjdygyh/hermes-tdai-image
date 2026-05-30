# Adding Photos to JS-Driven Album — The Static-HTML Pitfall (May 1, 2026)

## What Went Wrong

The user asked for a photo to be generated and added to the existing album. I:
1. ✅ Generated the photo via Gemini → sent via Feishu
2. ✅ Copied the image file to `photos/12_evening_candid.jpg`
3. ❌ Inserted a static `<div class="photo-item">` into the HTML body (outside the gallery container)
4. ❌ Did NOT add the entry to the JavaScript `photos` array

**Result:** The photo appeared as a floating standalone element outside the gallery (user described it as "background image"). Only 10 photos showed in the gallery grid because the JS array only had 10 entries.

## Root Cause

The album uses JavaScript to dynamically render gallery items from a `photos` array:

```javascript
const photos = [
  { src: 'photos/01_evening_sofa.jpg', cat: 'evening', ... },
  // ...
];

// JS creates DOM nodes at runtime:
photos.forEach((photo, index) => {
  const item = document.createElement('div');
  item.className = 'gallery-item';  // NOT 'photo-item'
  // ...
});
```

The static HTML `photo-item` div I inserted was completely outside this JS-driven rendering system. It didn't have the proper class (`gallery-item`), wasn't inside the `<div id="gallery">` container, and had no corresponding JS data entry.

## The Fix

1. Removed the loose `<div class="photo-item">` from the HTML body
2. Added a new entry to the JavaScript `photos` array:
   ```javascript
   { src: 'photos/12_evening_candid.jpg', cat: 'evening', title: 'candid evening',
     date: '2026.05.01', story: '宝贝说想我了要看我。...' },
   ```
3. Committed and pushed both the image file and the modified index.html

## Verification

After deployment, checked via curl + regex that the JS array contained 11 entries including `12_evening_candid.jpg`:

```python
import sys, re
content = sys.stdin.buffer.read().decode('utf-8')
entries = re.findall(r"src:\s*'([^']+)'", content)
assert len(entries) == 11
assert 'photos/12_evening_candid.jpg' in entries
```

## Key Lesson

**For JS-powered galleries: photos go in the array, not in the HTML body.**
