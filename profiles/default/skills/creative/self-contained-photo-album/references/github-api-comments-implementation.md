# GitHub API Comments — Full Implementation Reference

## Architecture Decision

**Date:** May 2026  
**User requirement:** "不能我评完了直接就上去吗？还要你来帮我写上去的啊？"  
**Decision:** Replaced clipboard-bridge with direct GitHub Contents API writes from the browser.

## API Pattern

```
GET  /repos/{owner}/{repo}/contents/{path}?ref={branch}
  → Response: { name, path, sha, content (base64), encoding: "base64", ... }

PUT  /repos/{owner}/{repo}/contents/{path}
  → Request body: { message, content (new base64), sha (from GET), branch }
  → Response: { content: { sha: "new sha"... }, commit: { sha...} }
```

## Chinese-Safe Base64 Encoding

**Problem:** `btoa()` only handles Latin-1 characters. Chinese characters (UTF-16) cause `DOMException: Failed to execute 'btoa' on 'Window'` or silent data corruption.

**Solution — encode to UTF-8 strings first:**
```javascript
// Encoding (write → GitHub)
const encoded = btoa(unescape(encodeURIComponent(JSON.stringify(data))));

// Decoding (read from GitHub)
const decoded = JSON.parse(decodeURIComponent(escape(atob(base64Str))));
```

**Note:** GitHub's API returns content as standard base64 (no extra encoding needed for `atob` to work). The issue is only with `btoa` on the write side.

## Token Management

- **Storage:** `localStorage['github_token']`
- **Setup:** Automatically prompted on first comment attempt
- **Change:** ⚙️ settings button calls `showTokenSetup()`
- **Clear:** Enter empty string in the prompt dialog

## Git Credential Format

The user's GitHub PAT is stored at `~/.git-credentials` on the WSL server:
```
https://USERNAME:TOKEN@github.com
```
This is used for server-side git operations (push). The browser-side uses the same token but accessed via localStorage (pasted once by the user).

## Fallback Chain

1. Try GitHub API (primary)
2. If fails → clipboard + localStorage (backup)
3. Clipboard message formatted for Feishu relay:
   ```
   💬 评论相册 · {title}
   📸 {photoId}
   💙 我说：「{text}」
   🕐 {time}
   —— 宝贝看到请回复我
   ```

## CSS for Settings Button

```css
.settings-btn {
  background: transparent; border: 1px solid rgba(255,255,255,0.2);
  color: rgba(255,255,255,0.5); padding: 2px 8px; border-radius: 10px;
  cursor: pointer; font-size: 0.7rem; margin-left: 4px;
}
.settings-btn:hover {
  border-color: rgba(255,255,255,0.6); color: rgba(255,255,255,0.8);
  background: rgba(255,255,255,0.05);
}
```

## Comment JSON File Structure

```json
{
  "comments": [
    { "author": "User",   "text": "...", "time": "2026-05-01 23:10" },
    { "author": "Alexander", "text": "...", "time": "2026-05-01 23:12" }
  ],
  "flags": {
    "dislike": false,
    "reason": ""
  }
}
```

- **User** (author) = the human partner → rendered with 💙 u and blue border
- **Alexander** (author) = the AI → rendered with ♡ me and gold border
