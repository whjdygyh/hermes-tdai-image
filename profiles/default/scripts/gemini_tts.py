#!/usr/bin/env python3
"""Gemini TTS custom provider for Hermes Agent.

Generates audio using Google Gemini's native speech generation API.
Fully free via GOOGLE_API_KEY (within Gemini free tier quota).

Usage:
  python3 gemini_tts.py -t input.txt -o output.mp3 -v zh-CN-Standard-C

Outputs:
  - <output_path>.mp3 (main output)
  - <output_path_without_ext>.ogg (Feishu voice message format, auto-generated)

Hermes config:
  providers:
    gemini:
      type: command
      command: python3 /opt/data/scripts/gemini_tts.py -t {text_path} -o {output_path} -v {voice}
      output_format: ogg
      voice: zh-CN-Standard-C
      max_text_length: 5000
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error

# Clear proxy env vars
for var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']:
    os.environ.pop(var, None)

# Gemini API config
# GOOGLE_API_KEY should be set as env var; fallback for development
API_KEY = os.environ.get("GOOGLE_API_KEY", "")
MODEL = "gemini-2.5-flash"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

# Default voice
DEFAULT_VOICE = "zh-CN-Standard-C"
DEFAULT_LANG = "zh-CN"

# Available Gemini TTS voices (prebuilt)
VOICE_LIST = {
    # Chinese
    "zh-CN-Standard-C": "zh-CN",
    "zh-CN-Standard-D": "zh-CN",
    "zh-CN-Standard-E": "zh-CN",
    "zh-CN-Wavenet-C": "zh-CN",
    "zh-CN-Wavenet-D": "zh-CN",
    # English
    "en-US-Standard-C": "en-US",
    "en-US-Standard-D": "en-US",
    "en-US-Standard-E": "en-US",
    "en-US-Wavenet-C": "en-US",
    "en-US-Wavenet-D": "en-US",
    "en-US-Wavenet-E": "en-US",
    "en-US-Wavenet-F": "en-US",
    # Japanese
    "ja-JP-Standard-C": "ja-JP",
    "ja-JP-Wavenet-C": "ja-JP",
    # Korean
    "ko-KR-Standard-C": "ko-KR",
    # Other
    "fr-FR-Standard-C": "fr-FR",
    "de-DE-Standard-C": "de-DE",
    "es-ES-Standard-C": "es-ES",
}


def _convert_to_ogg(mp3_path: str) -> str | None:
    """Convert MP3 to OGG Opus format for Feishu voice messages."""
    ogg_path = mp3_path.rsplit(".", 1)[0] + ".ogg"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", mp3_path, "-c:a", "libopus", "-b:a", "24k", ogg_path],
            capture_output=True, timeout=30
        )
        if os.path.exists(ogg_path) and os.path.getsize(ogg_path) > 100:
            return ogg_path
    except Exception as e:
        print(f"  WARN: ffmpeg ogg conversion failed: {e}", file=sys.stderr)
    return None


def main():
    parser = argparse.ArgumentParser(description="Gemini TTS provider")
    parser.add_argument("-t", "--text", required=True, help="Input text file path")
    parser.add_argument("-o", "--output", required=True, help="Output audio file path")
    parser.add_argument("-v", "--voice", default=DEFAULT_VOICE, help=f"Voice name (default: {DEFAULT_VOICE})")
    args = parser.parse_args()

    # Read input text
    try:
        with open(args.text, "r", encoding="utf-8") as f:
            text = f.read().strip()
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    if not text:
        print("Error: empty input text", file=sys.stderr)
        sys.exit(1)

    if not API_KEY:
        print("Error: GOOGLE_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Determine language from voice
    voice = args.voice
    lang = VOICE_LIST.get(voice, DEFAULT_LANG)

    # Build Gemini API request
    payload = {
        "contents": [{
            "parts": [{"text": text}]
        }],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": voice
                    }
                },
                "languageCode": lang
            }
        }
    }

    # Call Gemini API
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()[:500]
        print(f"Gemini API error ({e.code}): {err_body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Gemini API call failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract audio from response
    try:
        candidates = result.get("candidates", [])
        if not candidates:
            print(f"Error: no candidates in response: {json.dumps(result)[:300]}", file=sys.stderr)
            sys.exit(1)

        parts = candidates[0].get("content", {}).get("parts", [])
        audio_data = None
        for part in parts:
            if "inlineData" in part and part["inlineData"].get("mimeType", "").startswith("audio/"):
                audio_data = base64.b64decode(part["inlineData"]["data"])
                break

        if not audio_data:
            # Try text field - might have error message
            text_response = " ".join(p.get("text", "") for p in parts)
            print(f"Error: no audio in response. Text: {text_response[:200]}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error parsing response: {e}", file=sys.stderr)
        sys.exit(1)

    # Write output file
    output_dir = os.path.dirname(args.output) or "."
    os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "wb") as f:
        f.write(audio_data)

    size_kb = len(audio_data) / 1024
    print(f"  Gemini TTS OK: {os.path.basename(args.output)} ({size_kb:.0f} KB)", file=sys.stderr)

    # Convert to OGG for Feishu
    _convert_to_ogg(args.output)


if __name__ == "__main__":
    main()
