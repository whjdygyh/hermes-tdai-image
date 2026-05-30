#!/usr/bin/env python3
"""
Suno AI 音乐生成客户端 — CLI wrapper around the suno-api Python package.

Features:
  - One-time cookie setup with --setup
  - Auto-refresh JWT via Clerk session tokens (cookie lasts days/weeks)
  - Custom Mode (separate lyrics + style tags) or Describe Mode
  - Auto-download completed audio

Usage:
  python3 suno_client.py --setup           # First run: paste cookie
  python3 suno_client.py --credits         # Check remaining credits
  python3 suno_client.py --list            # List recent songs
  python3 suno_client.py --custom --prompt "lyrics" --tags "style"   # Custom mode
  python3 suno_client.py --prompt "description"                       # Describe mode

Cookie export (one-time):
  F12 → Network → refresh → find `__clerk_api_version` request
  → Headers → copy Cookie value → paste during --setup

Dependencies:
  pip install suno-api
"""

import os, sys, json, time, argparse, urllib.request
from pathlib import Path

COOKIE_FILE = os.path.expanduser("~/.suno_cookie")


def load_cookie():
    if not os.path.exists(COOKIE_FILE):
        return None
    with open(COOKIE_FILE) as f:
        return f.read().strip()


def save_cookie(cookie):
    with open(COOKIE_FILE, "w") as f:
        f.write(cookie.strip())
    os.chmod(COOKIE_FILE, 0o600)
    print(f"✅ Cookie saved to {COOKIE_FILE}")


def setup():
    """Interactive setup: prompt user to paste their Suno cookie."""
    print("=" * 60)
    print("  Suno AI Client — First-Time Setup")
    print("=" * 60)
    print()
    print("1. Open https://suno.com/create in your browser (logged in)")
    print("2. F12 → Network tab → Refresh the page")
    print("3. Find a request containing '__clerk_api_version' in the URL")
    print("4. Click it → Request Headers → find 'Cookie:' line")
    print("5. Right-click → Copy value")
    print()
    print("Paste the full cookie string below, then press Ctrl+D (or Enter twice):")
    print()

    lines = []
    try:
        while True:
            line = input()
            if line.strip() == "":
                if lines and lines[-1] == "":
                    break
            lines.append(line)
    except EOFError:
        pass

    cookie = "".join(lines).strip()
    if not cookie:
        print("❌ No cookie entered")
        return False

    print("\nVerifying cookie...")
    try:
        from suno import Suno
        client = Suno(cookie)
        credits = client.get_credits()
        save_cookie(cookie)
        print(f"\n✅ Verified! Credits remaining: {credits}")
        print("🎉 Setup complete — you can now generate songs directly.")
        return True
    except Exception as e:
        print(f"\n❌ Cookie verification failed: {e}")
        print("Possible: expired cookie, wrong format, or network issue.")
        return False


def get_client():
    cookie = load_cookie()
    if not cookie:
        print("❌ No saved cookie. Run: python3 suno_client.py --setup")
        sys.exit(1)
    from suno import Suno
    return Suno(cookie)


def cmd_credits():
    client = get_client()
    print(f"💰 Credits remaining: {client.get_credits()}")


def cmd_list():
    client = get_client()
    songs = client.songs.list()
    if not songs:
        print("No songs found.")
        return
    for i, s in enumerate(songs[:20], 1):
        title = s.get("title") or "(untitled)"
        status = s.get("status", "?")
        aid = s.get("id", "?")
        print(f"  {i:2d}. [{status}] {title}  (id: {aid})")


def cmd_generate(prompt, tags="", custom=False, instrumental=False, wait=True):
    client = get_client()
    mode = "Custom" if custom else "Describe"
    print(f"🎵 Generating ({mode} mode)...")
    if custom:
        print(f"   Lyrics: {prompt[:80]}...")
        print(f"   Style:  {tags}")
    else:
        print(f"   Prompt: {prompt[:80]}...")

    try:
        songs = client.songs.generate(prompt=prompt, tags=tags, custom=custom, instrumental=instrumental)
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return

    print(f"✅ Generated {len(songs)} song(s)")
    ids = [s["id"] for s in songs]
    for s in songs:
        print(f"   🎵 https://app.suno.ai/song/{s['id']}")

    if wait:
        print("\n⏳ Waiting for completion...")
        time.sleep(10)
        completed = {}
        for _ in range(12):  # ~2 min max
            for sid in ids:
                if sid in completed:
                    continue
                try:
                    s = client.songs.get(sid)
                    if s.get("status") == "complete" and s.get("audio_url"):
                        completed[sid] = s
                        print(f"   ✅ {s.get('title', sid)} ready")
                except Exception:
                    pass
            if len(completed) >= len(ids):
                break
            time.sleep(10)

        for sid, s in completed.items():
            title = s.get("title") or sid
            slug = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)
            url = s.get("audio_url")
            if url:
                fname = os.path.join(os.getcwd(), f"{slug}_{sid}.mp3")
                try:
                    urllib.request.urlretrieve(url, fname)
                    print(f"   📥 Downloaded: {fname}")
                except Exception as e:
                    print(f"   ❌ Download failed: {e}")


def main():
    p = argparse.ArgumentParser(description="Suno AI Music Generator")
    p.add_argument("--setup", action="store_true", help="One-time cookie setup")
    p.add_argument("--credits", action="store_true", help="Check remaining credits")
    p.add_argument("--list", action="store_true", help="List recent songs")
    p.add_argument("--custom", action="store_true", help="Custom mode (separate lyrics + style)")
    p.add_argument("--instrumental", action="store_true", help="No vocals")
    p.add_argument("--prompt", type=str, help="Lyrics (custom) or description (standard)")
    p.add_argument("--tags", type=str, default="", help="Style tags (required for custom mode)")
    p.add_argument("--no-wait", action="store_true", help="Don't wait for completion")
    args = p.parse_args()

    if args.setup:
        setup()
    elif args.credits:
        cmd_credits()
    elif args.list:
        cmd_list()
    elif args.prompt:
        cmd_generate(args.prompt, args.tags, args.custom, args.instrumental, not args.no_wait)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
