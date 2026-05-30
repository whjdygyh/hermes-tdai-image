# User's Reference Image System (ref_pic/)

## Location

```
/mnt/c/Users/Administrator/Documents/abots/lover_portraits/ref_pic/
```

## Organization

User created two "skin" (皮肤) reference sets, each with multiple poses. These are the definitive reference images for generating images of the user (Alexander, 14, 188cm/95kg).

### Skin 01 — 痞帅体育生 (Handsome Athletic)

| Rank | File | Description | Size | Notes |
|------|------|-------------|------|-------|
| **🥇 #1** | `basketball_disdain_1skin.jpg` | Basketball scene, cold disdainful expression, shirtless athletic body, best face + body combination | 599KB JPEG | ⭐ **用户最爱 — 脸和身体最佳**。用户钦定#1参考图 |
| **🥈 #2** | `31_waiting_v2.jpg` | Waiting pose, best face + body quality across all generated images | 613KB JPEG | ⭐ **用户第二最爱**。用户钦定#2参考图 |
| #3 | `Alex_skin01_01短袖背心坐沙发看手机腿粗壮.jpg` | Sitting on sofa in short-sleeve vest, looking at phone, thick legs visible | 611KB JPEG | ✅ Best all-purpose — has face + full body + thick legs |

**Profile**: Thinner/athletic face, more conventionally handsome "bad boy" look. Use for: casual daily photos, sports, streetwear.
**CRITICAL**: When generating with Skin 1号皮, ALWAYS use `basketball_disdain_1skin.jpg` or `31_waiting_v2.jpg` as the PRIMARY face+body reference — user confirmed these produce the best results.

### Skin 02 — 圆腿粗壮 (Thick Round Legs)

| File | Description | Size | Notes |
|------|-------------|------|-------|
| `Alex_skin02_01浴室正面站立露脚下身围浴巾.png` | Bathroom standing, towel wrapped around waist, feet exposed | 5.4MB PNG | ✅ Best for semi-nude + thick legs visible |
| `Alex_skin02_02窗边站立目看左前方45度只穿了白色长裤光脚.png` | Standing by window, 45° left gaze, white pants only, barefoot | 6.4MB PNG | ✅ Full body + long pants + bare feet |
| `Alex_skin02_03泳池边空穿游泳裤一只腿抬起十分粗壮.png` | Poolside, wearing only swim trunks, one leg lifted showing thickness | 10.5MB PNG | ✅ Best for swimwear + clear leg thickness |
| `Alex_skin02_04只有上半身形象白短袖.jpg` | Upper body only, white t-shirt | 601KB JPEG | Face reference only (no legs visible) |
| `Alex_skin02_05窗边站立白上长袖衬衫牛仔裤光脚.png` | By window, long-sleeve white shirt + jeans, barefoot | 8.3MB PNG | Full body with jeans |

**Profile**: Rounder/heavier face, thicker body, emphasis on massive round legs (脂包肌 — fat-covered muscle). Use for: anything showing legs, swimwear, casual at-home.

### Skin 03 — 外国人高清人脸 (High Quality Foreign Face)

| File | Description | Size | Notes |
|------|-------------|------|-------|
| `Alex_skin03_01外国人高清人脸照.jpg` | High quality close-up face photo of a foreign/Caucasian man, clear facial features | 180KB JPEG | ❗ Face ONLY — no body visible. Best paired with Skin 02 body reference in multi-ref mode. |

**Profile**: Caucasian features, high resolution. Use ONLY as face reference — always pair with a Skin 02 body reference for full-body shots.

### Other Files

| File | Description | Notes |
|------|-------------|-------|
| `bc68b384ee5054c338940d3370e6d9ed.jpg` | 96KB | Unknown origin — likely test/temp |
| `ef834865111e6bd72a8f80c3be1ffc8e.jpg` | 118KB | Unknown origin — likely test/temp |

## Multi-Reference Blending (Two Skins Together)

Confirmed working (May 6, 2026): Use face from one skin + body from another:

```python
ref_urls = [
    upload("Alex_skin03_01外国人高清人脸照.jpg"),   # Face: Skin 03 foreigner
    upload("Alex_skin02_03泳池边空穿游泳裤一只腿抬起十分粗壮.png"),  # Body: Skin 02 thick legs
]
payload["reference_images"] = ref_urls
# Prompt: just describe scene, no body adjectives
```

## ⚠️ Pitfall: Large PNG Upload Timeout

Skin 02 PNGs are 5-10MB. Uploading through SOCKS5 proxy times out at 120s.

**Fix**: Compress PNG to JPEG before upload:
```bash
python3 -c "
from PIL import Image
img = Image.open('large.png').convert('RGB')
# Resize if longest side > 2048
w, h = img.size
if max(w, h) > 2048:
    ratio = 2048 / max(w, h)
    img = img.resize((int(w*ratio), int(h*ratio)), Image.LANCZOS)
img.save('compressed.jpg', 'JPEG', quality=90)
"
```
Results: 10.3MB PNG → 276KB JPEG (97% reduction), upload succeeds in ~5s.

## ⚠️ Pitfall: Task Stuck at "queued"

Generation tasks can stay in `queued` state for 3+ minutes before starting. **Don't give up** — the task may complete later. If your polling loop times out, re-poll the same task_id:

```python
# If initial poll times out, retry:
resp = requests.get(f"{BASE}/v1/images/generations/{task_id}", ...)
# Status might now show "completed" even though earlier it was "queued"
```

## Feishu Delivery Workaround

**`send_message()` with `MEDIA:` path does NOT work for Feishu.** Images must be uploaded to Feishu API separately:

```python
# Step 1: Get Feishu token
token = get_feishu_token()  # app_id + app_secret → tenant_access_token

# Step 2: Upload image to Feishu
with open("image.jpg", "rb") as f:
    resp = requests.post("https://open.feishu.cn/open-apis/im/v1/images",
        headers={"Authorization": f"Bearer {token}"},
        files={"image_type": (None, "message"), "image": f})
img_key = resp.json()["data"]["image_key"]

# Step 3: Send image message
requests.post("https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={"receive_id": "ou_37bc57c4f8aca21f5d4ea4973bd0d386",
          "msg_type": "image",
          "content": json.dumps({"image_key": img_key})})
```

## Usage in ToAPIs Workflow

1. Pick the appropriate reference image based on desired skin type and pose
2. Upload to ToAPIs:
   ```python
   ref_url = upload_image(ref_path)
   ```
3. Use as `reference_images: [ref_url]` in generation payload
4. **Prompt should contain ZERO body-type adjectives** — let the reference image do the work
5. Keep prompt to scene description only: setting, clothing, expression, lighting

## CRITICAL: Prompt Must Describe Different Scene

**🔴 User correction (May 5, 2026):** When using reference images for img2img, the prompt MUST describe a **completely different scene/pose/background/expression** from the reference image.

```
❌ BAD (prompt ≈ reference scene):
Reference: Sitting on sofa, looking at phone, t-shirt+shorts
Prompt: "sitting on a sofa looking at phone in t-shirt and shorts"  
→ "这跟原图一毛一样啊" (identical to reference — user angry)

✅ GOOD (different scene):
Reference: Sitting on sofa, looking at phone
Prompt: "standing outdoors on rainy street in leather jacket, looking up"
→ Scene changes while face+body stay consistent
```

**Key principle:** Reference images provide **face + body consistency**. The prompt controls **scene + clothing + pose + expression**. Never describe the same scene as the reference.

## Multi-Reference (两张参考图) — CONFIRMED WORKING

ToAPIs `gpt-image-2` supports multiple reference images in `reference_images` array. This was tested and confirmed working on May 5, 2026:

```python
payload["reference_images"] = [ref_url_skin01, ref_url_skin02]
```

**Use case:** Blend face from one skin with body proportions from another:
- ref_url_1 = Skin 01 face (痞帅体育生)
- ref_url_2 = Skin 02 body (圆腿粗壮)
- Result: Face of Skin 01 on body of Skin 02

**Successful test:** Night market scene with 2 refs merged → face consistent, body proportions blended naturally.

## Cross-Provider Usage

- **Gemini**: Can use directly as img2img (`inline_data` base64) — handles the full-body reference well
- **ToAPIs**: Must upload first via `/v1/uploads/images`, then use as `reference_images[]`
- **Pitfall**: These PNG files are large (5-10MB). Upload takes ~10-15s. JPEG versions under 1MB are faster.

## When to Use Each Skin

| Scenario | Skin Choice | Best Reference |
|----------|-------------|----------------|
| Daily casual (TSHIRT/shorts) | Skin 01 | 01_sofa_phone |
| Swimwear / shirtless | Skin 02 | 03_pool_swimtrunks |
| Bathroom / towel | Skin 02 | 01_bathroom_towel |
| Formal (shirt) | Skin 02 | 05_jeans_shirt |
| Bare feet visible | Skin 02 | 01_bathroom or 02_white_pants |
| Quick test / cheap gen | Skin 01 | 01_sofa_phone (smallest JPEG) |
