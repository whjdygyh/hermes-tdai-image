---
name: huggingface-hub
description: "HuggingFace hf CLI: search/download/upload models, datasets."
version: 1.0.0
author: Hugging Face
license: MIT
tags: [huggingface, hf, models, datasets, hub, mlops]
platforms: [linux, macos, windows]
---

# Hugging Face CLI (`hf`) Reference Guide

The `hf` command is the modern command-line interface for interacting with the Hugging Face Hub, providing tools to manage repositories, models, datasets, and Spaces.

> **IMPORTANT:** The `hf` command replaces the now deprecated `huggingface-cli` command.

## Quick Start
*   **Installation:** `curl -LsSf https://hf.co/cli/install.sh | bash -s`
*   **Help:** Use `hf --help` to view all available functions and real-world examples.
*   **Authentication:** Recommended via `HF_TOKEN` environment variable or the `--token` flag.

---

## Core Commands

### General Operations
*   `hf download REPO_ID`: Download files from the Hub.
*   `hf upload REPO_ID`: Upload files/folders (recommended for single-commit).
*   `hf upload-large-folder REPO_ID LOCAL_PATH`: Recommended for resumable uploads of large directories.
*   `hf sync`: Sync files between a local directory and a bucket.
*   `hf env` / `hf version`: View environment and version details.

### Authentication (`hf auth`)
*   `login` / `logout`: Manage sessions using tokens from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
*   `list` / `switch`: Manage and toggle between multiple stored access tokens.
*   `whoami`: Identify the currently logged-in account.

### Repository Management (`hf repos`)
*   `create` / `delete`: Create or permanently remove repositories.
*   `duplicate`: Clone a model, dataset, or Space to a new ID.
*   `move`: Transfer a repository between namespaces.
*   `branch` / `tag`: Manage Git-like references.
*   `delete-files`: Remove specific files using patterns.

---

## Specialized Hub Interactions

### Datasets & Models
*   **Datasets:** `hf datasets list`, `info`, and `parquet` (list parquet URLs).
*   **SQL Queries:** `hf datasets sql SQL` — Execute raw SQL via DuckDB against dataset parquet URLs.
*   **Models:** `hf models list` and `info`.
*   **Papers:** `hf papers list` — View daily papers.

### Discussions & Pull Requests (`hf discussions`)
*   Manage the lifecycle of Hub contributions: `list`, `create`, `info`, `comment`, `close`, `reopen`, and `rename`.
*   `diff`: View changes in a PR.
*   `merge`: Finalize pull requests.

### Infrastructure & Compute
*   **Endpoints:** Deploy and manage Inference Endpoints (`deploy`, `pause`, `resume`, `scale-to-zero`, `catalog`).
*   **Jobs:** Run compute tasks on HF infrastructure. Includes `hf jobs uv` for running Python scripts with inline dependencies and `stats` for resource monitoring.
*   **Spaces:** Manage interactive apps. Includes `dev-mode` and `hot-reload` for Python files without full restarts.

### Storage & Automation
*   **Buckets:** Full S3-like bucket management (`create`, `cp`, `mv`, `rm`, `sync`).
*   **Cache:** Manage local storage with `list`, `prune` (remove detached revisions), and `verify` (checksum checks).
*   **Webhooks:** Automate workflows by managing Hub webhooks (`create`, `watch`, `enable`/`disable`).
*   **Collections:** Organize Hub items into collections (`add-item`, `update`, `list`).

---

## China Mirror Downloads (hf-mirror.com)

### Background
When operating from mainland China, `huggingface.co` is blocked/timeout. Use `hf-mirror.com` via `HF_ENDPOINT`.

### Quick Setup
```bash
export HF_ENDPOINT=https://hf-mirror.com
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
```

### Large File Downloads (>4GB)
**Large files frequently fail** on hf-mirror due to connection drops mid-transfer (curl hits 63-83% then disconnects). **wget with unlimited retries** is the most reliable approach:

```bash
wget --tries=0 --timeout=120 --read-timeout=60 --retry-connrefused -c \
  -O model.safetensors \
  "https://hf-mirror.com/repo_id/resolve/main/model.safetensors"
```

### Validation is Mandatory
Network drops cause partial writes that look complete but fail at load time. Always validate safetensors files after download:

```python
from safetensors import safe_open
with safe_open("file.safetensors", framework="pt", device="cpu") as f:
    keys = f.keys()
print(f"✅ VALID: {len(keys)} tensors")
```

### Tools Comparison
| Method | Reliability | Large Files | Notes |
|--------|------------|-------------|-------|
| **wget** | ✅ Best | ✅ ✅ | Unlimited retries, auto-resume |
| **curl** | ⚠️ Moderate | ⚠️ Fails at 63-83% | `--retry` helps but often fails |
| **hf CLI** | ⚠️ Moderate | ⚠️ Can hang 24min+ | Needs HF_TOKEN |
| **huggingface-cli** | ❌ Deprecated | ❌ | Use `hf` instead |
| **huggingface_hub** | ⚠️ Moderate | ⚠️ Unstable | Python lib |

**Full guide with all pitfalls:** See `references/china-mirror-download.md`

---

## Advanced Usage & Tips

### Global Flags
*   `--format json`: Produces machine-readable output for automation.
*   `-q` / `--quiet`: Limits output to IDs only.

### Extensions & Skills
*   **Extensions:** Extend CLI functionality via GitHub repositories using `hf extensions install REPO_ID`.
*   **Skills:** Manage AI assistant skills with `hf skills add`.
