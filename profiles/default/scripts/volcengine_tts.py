#!/usr/bin/env python3
"""Volcengine TTS custom provider for Hermes Agent.

Generates MP3 + auto-converts to OGG (Opus) for Feishu voice message delivery.

Usage:
  python3 volcengine_tts.py -t input.txt -o output.mp3 -v zh_male_xxx

Outputs:
  - <output_path>.mp3 (main output)
  - <output_path_without_ext>.ogg (Feishu voice message format, auto-generated)

Placeholders in Hermes config:
  command: "python3 ~/.hermes/scripts/volcengine_tts.py -t {input_path} -o {output_path} -v {voice}"
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import uuid

# Clear proxy env vars - Volcengine API is cloud-based, no proxy needed
for var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']:
    os.environ.pop(var, None)

import requests


API_KEY="9025a361-6a59-47ab-a131-20f1ac66be45"
APP_ID = "9768463927"
DEFAULT_VOICE = "ICL_zh_male_tiexinnanyou_tob"
ENDPOINT = "https://openspeech.bytedance.com/api/v1/tts"


def _convert_to_ogg(mp3_path: str) -> str | None:
    """Convert MP3 to OGG Opus format for Feishu voice messages.

    Feishu only supports .ogg/.opus as native voice messages (voice bubbles).
    MP3 files are sent as file attachments instead.

    Returns path to ogg file, or None if conversion failed.
    """
    ogg_path = os.path.splitext(mp3_path)[0] + ".ogg"
    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", mp3_path,
             "-c:a", "libopus", "-b:a", "24k", "-vn", ogg_path],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            print(f"  ogg: {ogg_path} ({os.path.getsize(ogg_path)} bytes)", file=sys.stderr)
            return ogg_path
        else:
            print(f"  WARN: ffmpeg failed (exit {result.returncode}): {result.stderr[:200]}", file=sys.stderr)
            return None
    except FileNotFoundError:
        print("  WARN: ffmpeg not found, skipping ogg conversion", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        print("  WARN: ffmpeg timed out, skipping ogg conversion", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="Volcengine TTS provider")
    parser.add_argument("-t", "--text", required=True, help="Input text file path")
    parser.add_argument("-o", "--output", required=True, help="Output audio file path (should end in .mp3)")
    parser.add_argument("-v", "--voice", default=DEFAULT_VOICE, help="Voice type")
    parser.add_argument("-s", "--speed", type=float, default=1.0, help="Speed ratio (default: 1.0)")
    parser.add_argument("-p", "--pitch", type=float, default=1.0, help="Pitch ratio (default: 1.0)")
    parser.add_argument("-e", "--emotion", default=None, help="Emotion mode (for _emo_ voices, default: None = auto)")
    parser.add_argument("--no-ogg", action="store_true", help="Skip OGG conversion (no voice message fallback)")
    args = parser.parse_args()

    # Read input text
    if not os.path.exists(args.text):
        print(f"Error: input file not found: {args.text}", file=sys.stderr)
        sys.exit(1)

    with open(args.text, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        print("Error: empty input text", file=sys.stderr)
        sys.exit(1)

    # Call Volcengine TTS API
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": API_KEY,
    }

    payload = {
        "app": {"appid": APP_ID, "cluster": "volcano_tts"},
        "user": {"uid": "hermes_tts"},
        "request": {
            "reqid": str(uuid.uuid4()),
            "text": text,
            "text_type": "plain",
            "operation": "query",
            "frontend_type": "unitTson",
        },
        "audio": {
            "voice_type": args.voice,
            "encoding": "mp3",
            "speed_ratio": args.speed,
            "volume_ratio": 1.0,
            "pitch_ratio": args.pitch,
        },
    }

    # Add emotion if specified
    if args.emotion:
        payload["audio"]["emotion"] = args.emotion

    # Support voice::emotion format in voice name
    if "::" in args.voice:
        parts = args.voice.split("::", 1)
        voice_actual = parts[0]
        payload["audio"]["voice_type"] = voice_actual
        payload["audio"]["emotion"] = parts[1]
        # Override: also set emotion as top-level param if applicable
    else:
        payload["audio"]["voice_type"] = args.voice

    resp = requests.post(ENDPOINT, json=payload, headers=headers, timeout=30)

    if resp.status_code != 200:
        print(f"HTTP {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
        sys.exit(1)

    result = resp.json()
    code = result.get("code")

    if code != 3000:
        print(f"API error ({code}): {result.get('message', '')}", file=sys.stderr)
        sys.exit(1)

    audio_b64 = result.get("data", "")
    if not audio_b64:
        print("Error: no audio data in response", file=sys.stderr)
        sys.exit(1)

    audio_bytes = base64.b64decode(audio_b64)

    # Generate to a temp MP3 first, then output final format
    output_dir = os.path.dirname(os.path.abspath(args.output)) or "."
    os.makedirs(output_dir, exist_ok=True)

    mp3_tmp = args.output + ".tmp.mp3"
    with open(mp3_tmp, "wb") as f:
        f.write(audio_bytes)

    print(f"OK: {len(audio_bytes)} bytes MP3 generated", file=sys.stderr)

    # Always convert to OGG for Feishu voice messages — output to the requested path
    ogg_path = _convert_to_ogg(mp3_tmp)

    if ogg_path:
        # Move ogg to the actual output path requested by Hermes
        final_path = os.path.splitext(args.output)[0] + ".ogg"
        if ogg_path != final_path:
            os.replace(ogg_path, final_path)
        print(final_path)
        print(f"  => ogg: {final_path}", file=sys.stderr)
        os.remove(mp3_tmp)
    else:
        # Fallback: output mp3 directly
        os.rename(mp3_tmp, args.output)
        print(args.output)
        print(f"  => mp3 (ogg conversion failed): {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
