#!/usr/bin/env python3
"""
Generate 3 resolutions (1K/2K/4K) via toapis.com GPT-Image-2.

Usage:
  export TOAPIS_API_KEY="sk-..."
  python3 toapis_batch_generation.py

Requires: requests, Pillow (pip install requests Pillow)
Proxy: Uses SOCKS5 at 172.20.128.1:10808 (V2Ray overseas node)
"""

import requests, time, json, os, sys

API_KEY = os.environ.get("TOAPIS_API_KEY", "sk-nI0yWGJZDecPQHP7ylyEL4yvptovSFuTNqHmYlVt5YxaSAyO")
BASE = "https://toapis.com"  # ⚠️ DO NOT add /v1 here — paths below already include it
PROXY = "socks5://172.20.128.1:10808"
proxies = {"http": PROXY, "https": PROXY}
SAVE_DIR = os.path.expanduser("~/.hermes/profiles/lover/audio_cache")

DEFAULT_PROMPT = (
    "A candid realistic photo of an athletic 14-year-old teen boy with "
    "Eurasian fair warm skin tone, sitting barefoot at a wooden dining table "
    "at night eating dinner. One bare foot rests on the floor, the other foot "
    "is hooked around a chair leg, casual and playful pose. He wears a white "
    "t-shirt and grey shorts. Warm indoor evening lighting, cozy home atmosphere, "
    "natural documentary photography style from a low angle showing his legs and feet."
)

def generate(prompt, size="2:3", resolution="1K"):
    """Submit a generation task and return the task ID."""
    payload = {
        "model": "gpt-image-2",
        "prompt": prompt,
        "n": 1,
        "size": size,
        "resolution": resolution,
        "response_format": "url"
    }
    resp = requests.post(
        f"{BASE}/v1/images/generations",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json=payload,
        proxies=proxies,
        timeout=30
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Generation submission failed ({resp.status_code}): {resp.text[:300]}")
    task_id = resp.json().get("id")
    print(f"  Task created: {task_id} ({resolution}, {size})")
    return task_id

def poll(task_id, max_wait=180):
    """Poll until generation completes, return download URL."""
    start = time.time()
    while time.time() - start < max_wait:
        resp = requests.get(
            f"{BASE}/v1/images/generations/{task_id}",
            headers={"Authorization": f"Bearer {API_KEY}"},
            proxies=proxies,
            timeout=30
        )
        result = resp.json()
        status = result.get("status")
        progress = result.get("progress", 0)
        if status == "completed":
            items = result.get("result", {}).get("data", [])
            if items and items[0].get("url"):
                print(f"    Done! Progress: {progress}%, elapsed: {time.time()-start:.0f}s")
                return items[0]["url"]
        elif status == "failed":
            raise RuntimeError(f"Generation failed: {result.get('error')}")
        print(f"    Status={status}, progress={progress}%, elapsed: {time.time()-start:.0f}s", end="\r")
        time.sleep(3)
    raise TimeoutError(f"Task {task_id} timed out after {max_wait}s")

def download_and_convert(url, save_path):
    """Download image from URL and convert PNG→JPEG if needed."""
    img_resp = requests.get(url, proxies=proxies, timeout=30)
    raw = img_resp.content

    # Check if it's actually PNG (magic bytes)
    if raw[:4] == b'\x89PNG':
        from PIL import Image
        from io import BytesIO
        img = Image.open(BytesIO(raw)).convert('RGB')
        img.save(save_path, 'JPEG', quality=92)
    else:
        with open(save_path, 'wb') as f:
            f.write(raw)

    size_kb = os.path.getsize(save_path) // 1024
    print(f"  Saved: {save_path} ({size_kb}KB)")
    return size_kb

def generate_all_resolutions(prompt=DEFAULT_PROMPT, output_prefix="toapis"):
    """Generate 1K, 2K, and 4K images from the same prompt."""
    os.makedirs(SAVE_DIR, exist_ok=True)

    configs = [
        ("1K", "2:3"),
        ("2K", "9:16"),
        ("4K", "9:16"),
    ]

    # Step 1: Submit all tasks (parallel submission)
    print("Submitting generation tasks...")
    tasks = []
    for resolution, size in configs:
        task_id = generate(prompt, size=size, resolution=resolution)
        tasks.append((resolution, task_id, size))

    # Step 2: Poll and download each
    print("\nWaiting for results...")
    results = []
    for resolution, task_id, size in tasks:
        print(f"\n--- {resolution} ({size}) ---")
        try:
            url = poll(task_id)
            fname = f"{output_prefix}_{resolution}.jpg"
            save_path = os.path.join(SAVE_DIR, fname)
            size_kb = download_and_convert(url, save_path)
            results.append((resolution, save_path, size_kb))
        except Exception as e:
            print(f"  ❌ {resolution} failed: {e}")
            results.append((resolution, None, 0))

    # Summary
    print("\n=== SUMMARY ===")
    for res, path, kb in results:
        if path:
            print(f"  ✅ {res}: {path} ({kb}KB)")
        else:
            print(f"  ❌ {res}: FAILED")
    return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate ToAPIs GPT-Image-2 images at 3 resolutions")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="Generation prompt")
    parser.add_argument("--prefix", default="toapis", help="Output filename prefix")
    args = parser.parse_args()
    generate_all_resolutions(args.prompt, args.prefix)
