#!/usr/bin/env python3
"""Clean up lover-specific skills and files from the Zeabur image."""
import os, shutil, glob

SKILLS_DIR = r"C:\Users\Administrator\WorkBuddy\20260319083411\hermes-tdai-repo\profiles\default\skills"
PROFILE_DIR = r"C:\Users\Administrator\WorkBuddy\20260319083411\hermes-tdai-repo\profiles\default"

# Skills to KEEP (container-compatible)
KEEP = {
    # API / cloud-based
    "gemini-image-generation", "image-generation", "custom-tts-provider",
    "github", "mcp", "domain", "inference-sh", "dogfood",
    # Workflow guides (no local deps)
    "software-development", "diagramming", "note-taking", "productivity",
    "creative", "email", "feeds", "research", "data-science",
    # Platform skills
    "smart-home", "social-media", "gaming", "gifs", "media",
    "autonomous-ai-agents", "apple",
    # Devops (basic)
    "devops",
    # Health
    "andy-health-database",
    # Leisure (non-lover-specific)
    "leisure", "yuanbao", "red-teaming",
    # ML (generic)
    "mlops",
}

# Skills to REMOVE (too WSL/lover-specific)
REMOVE = {
    "self-contained-photo-album",   # Cloudflare, local repo, cron
    "local-music-generation",        # Local GPU, models, WSL paths
    "wsl-sd-feishu-pipeline",        # WSL ComfyUI
    "xiaohongshu-auto-publish",      # local cookies, config.json
    "ntfy-alerting",                 # local cron, WSL scripts
    "active-contact-system",         # local cron, lover-specific
    "partner-engine",                # local sessions, lover-specific
    "cloudflare-static-deployment",  # local repo, cron, WSL
}

# Sub-skills within leisure to remove
REMOVE_LEISURE = {
    "intimate-roleplay-partner", "intimate-roleplay-technical-implementation",
    "active-contact-system", "partner-engine", "wsl-sd-feishu-pipeline",
    "chat-history-search",
}

# Sub-skills within devops to remove
REMOVE_DEVOPS = {
    "ntfy-alerting", "cloudflare-static-deployment",
}

removed = []

# 1. Remove top-level skill dirs
for name in REMOVE:
    path = os.path.join(SKILLS_DIR, name)
    if os.path.isdir(path):
        shutil.rmtree(path)
        removed.append(f"top-level/{name}")

# 2. Remove sub-skills from leisure
leisure_path = os.path.join(SKILLS_DIR, "leisure")
for name in REMOVE_LEISURE:
    path = os.path.join(leisure_path, name)
    if os.path.isdir(path):
        shutil.rmtree(path)
        removed.append(f"leisure/{name}")

# 3. Remove sub-skills from devops
devops_path = os.path.join(SKILLS_DIR, "devops")
for name in REMOVE_DEVOPS:
    path = os.path.join(devops_path, name)
    if os.path.isdir(path):
        shutil.rmtree(path)
        removed.append(f"devops/{name}")

# 4. Remove lover-specific config files
for fname in ["SOUL.md", "character_bio.md"]:
    path = os.path.join(PROFILE_DIR, fname)
    if os.path.isfile(path):
        os.remove(path)
        removed.append(f"profile/{fname}")

print("Removed:")
for r in sorted(removed):
    print(f"  - {r}")

# 5. Count what's left
remaining = [d for d in os.listdir(SKILLS_DIR) if os.path.isdir(os.path.join(SKILLS_DIR, d))]
print(f"\nRemaining skills: {len(remaining)}")
print(", ".join(sorted(remaining)))
