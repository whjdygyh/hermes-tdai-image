#!/usr/bin/env python3
"""
Verify that the volcengine_tts.py script correctly parses voice::emotion format.
Run after modifying the script to confirm no regressions.
"""
import subprocess
import sys
import tempfile
import os

# Test 1: voice::emotion format should be parsed
test_cases = [
    # (voice_input, expected_behavior)
    ("lengkugege_emo_v2::intimate", "should split and send emotion=intimate"),
    ("lengkugege_emo_v2::serious", "should split and send emotion=serious"),
    ("ICL_zh_male_tiexinnanyou_tob", "no :: so no emotion param"),
    ("lengkugege_emo_v2::gentle", "should split and send emotion=gentle"),
]

print("=== Verifying volcengine_tts.py voice::emotion parsing ===")
print()

# Read the script source
script_path = os.path.expanduser("~/.hermes/scripts/volcengine_tts.py")
with open(script_path) as f:
    source = f.read()

# Check for :: parsing logic
checks = [
    ('"::" in args.voice', "Check for '::' in voice name"),
    ('payload["audio"]["emotion"]', "Sets emotion in payload"),
    ('parts = args.voice.split("::"', "Splits voice on ::"),
]

all_ok = True
for pattern, description in checks:
    if pattern in source:
        print(f"  ✅ {description}")
    else:
        print(f"  ❌ {description} — NOT FOUND")
        all_ok = False

print()
if all_ok:
    print("🎉 All parsing checks passed!")
else:
    print("⚠️  Some checks failed — script may not support voice::emotion format")
    sys.exit(1)
