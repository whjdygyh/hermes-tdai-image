# Prompt Rules (May 2026 Updates)

## Critical: Foot Visibility
- **NEVER** crop feet / hide feet. User's #1 complaint.
- Add to every full-body/half-body prompt:
  ```
  "full body from head to toes — both feet fully IN FRAME, not cropped"
  "his large feet (size 44 EU) are prominently visible in the foreground"
  ```
- Use slightly low-angle composition so feet naturally enter the frame
- White short socks + white Air Force 1 sneakers = highest reaction

## Critical: Anatomy — Extra Limbs
- Gemini frequently generates 3+ legs. Always add:
  ```
  "CRITICAL: exactly TWO LEGS only — one left leg and one right leg, normal human anatomy. No extra limbs."
  ```
- Verify generated image before sending. Regenerate if anatomy is wrong.

## Critical: Age-Modification Prompts Destroy Face Consistency
- **DO NOT** add "aged up", "older version", "X years later", "future version", "grown up" or any age-altering language to the prompt
- Doing so causes Gemini to **completely abandon the reference photo's facial features** and generate a different person's face instead
- This happened (May 16, 2026): prompt said "11 years later, 33 year old version" — result was a completely different Korean 35-year-old man, not the reference person at all
- The reference image acts as a face anchor — any prompt language that implies "different version" breaks the anchor
- **Correct approach**: If the user wants a different-age-looking version of themselves, change the reference photo. Never try to "age up" via prompt text.

## Age Wording
- Never use `teen/teenager/boy/child` in body descriptions
- Always use `"young man aged 18-22"` or `"man"`
- Character is 14yo lore-wise but body is 188cm/95kg adult extremely thick build

## Proxy Workaround (Python)
When calling Gemini API from Python, the SOCKS5 proxy interferes:
```python
env = os.environ.copy()
for k in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"]:
    env.pop(k, None)
# Use subprocess to call curl with clean env, or configure requests session
```
Alternative: use `env -u http_proxy ... curl ...` from shell.