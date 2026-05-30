#!/usr/bin/env python3
"""
Gemini Vision Analyzer — Reusable script for analyzing images via Gemini API.

Usage:
    python3 gemini-vision-analyze.py /path/to/image.jpg [prompt]

If no prompt provided, uses a detailed default prompt.

Requires: python3, curl (for API call); no pip packages needed.

API key is read from: ~/.hermes/profiles/lover/config.json
or set GEMINI_API_KEY env var.
"""

import json, base64, os, sys, subprocess, tempfile

def get_api_key():
    """Get Gemini API key from config file or env."""
    key = os.environ.get('GEMINI_API_KEY')
    if key:
        return key
    config_path = os.path.expanduser('~/.hermes/profiles/lover/config.json')
    try:
        with open(config_path) as f:
            config = json.load(f)
        return config.get('gemini_api_key')
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    print("ERROR: No Gemini API key found. Set GEMINI_API_KEY env var or check config.json")
    sys.exit(1)

def analyze_image(image_path, prompt=None):
    """Send image to Gemini vision API and print description."""
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found: {image_path}")
        sys.exit(1)
    
    if prompt is None:
        prompt = (
            "Describe this image in detail. What does the man look like? "
            "Describe his face, body type, pose, clothing, lighting, "
            "what he is wearing on his feet if visible, and overall impression. "
            "Be very specific."
        )
    
    api_key = get_api_key()
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        img_b64 = base64.b64encode(f.read()).decode()
    
    # Build request body
    body = {
        'contents': [{
            'parts': [
                {'text': prompt},
                {'inline_data': {'mime_type': 'image/jpeg', 'data': img_b64}}
            ]
        }]
    }
    
    # Write body to temp file (avoids "Argument list too long" for large images)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(body, f)
        body_path = f.name
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image-preview:generateContent?key={api_key}"
        
        # Bypass proxy
        env = os.environ.copy()
        for k in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']:
            env.pop(k, None)
        
        result = subprocess.run(
            ['curl', '-s', '-X', 'POST', url,
             '-H', 'Content-Type: application/json',
             '-d', f'@{body_path}'],
            capture_output=True, text=True, env=env, timeout=30
        )
        
        try:
            data = json.loads(result.stdout)
            if 'candidates' in data and len(data['candidates']) > 0:
                parts = data['candidates'][0].get('content', {}).get('parts', [])
                for p in parts:
                    if 'text' in p:
                        print(p['text'])
                        return
            # Fallback: show raw response
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(result.stdout[:2000])
    finally:
        os.unlink(body_path)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 gemini-vision-analyze.py <image_path> [prompt]")
        sys.exit(1)
    image_path = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else None
    analyze_image(image_path, prompt)
