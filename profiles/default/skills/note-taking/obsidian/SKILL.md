---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
platforms: [linux, macos, windows]
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `~/.hermes/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

### ⚠️ User-specific vault setup (安迪)

安迪的 Obsidian vault 在 **`G:\MyAIProject\alexworks`**（WSL路径: `/mnt/g/MyAIProject/alexworks`）。

- `.obsidian` 在 vault 根目录
- 注意：vault 内可能有一个同名的嵌套 `alexworks/` 子目录（同步产生的套娃），**不要混淆** — vault 根目录是有 `.obsidian` 的那一层
- 如果后续路径变动，先确认 `.obsidian` 的位置来确定真正的 vault 根目录

### ⚠️ 文件组织规范

所有写入 vault 的文件必须遵循以下层级：

```
📁 <项目名>/              ← 顶层项目文件夹（如 "Weald & Ember"）
├── 📄 项目概述文件         ← 顶层的项目说明/简介
├── 📁 单曲/               ← 单曲类内容（歌词、发布信息）
│   └── ...
├── 📁 专辑/               ← 专辑类内容（曲目表、提示词）
│   └── ...
└── ...                   ← 其他类型子文件夹按需创建
```

### ⚠️ 技能资料分类文件夹约定（PicMe / Vox Being）

用户创建了专属技能资料文件夹来存放 LLM 辅助技能（如「想你了」生图、语音合成）的完整参考材料。这些是**能力分类，不是项目**：

- `PicMe/` — 生图技能（智能场景引擎、Gemini/SD/ToAPIs 多方案、参考图库、自动管道脚本）
- `Vox Being/` — 语音合成技能（TTS 切换架构、音色映射、配置模板、情感解析脚本）

**约定：**
- 技能资料文件夹直接放 vault 根目录（与项目文件夹同级）
- 每个技能文件夹下放置该技能的全部文档 + 脚本 + 配置模板 + 参考文件
- 文件的完整复制由 LLM 自己执行（用 `cp`/`write_file`），用户只负责建文件夹
- 不要在这些文件夹里创建「单曲/」「专辑/」等子分类 — 它们是扁平的参考仓库

**铁律：**
- 不要直接写文件到 vault 根目录（`欢迎.md` 除外，那是 Obsidian 自动创建的）
- 不要套多层无意义的子目录
- 项目文件夹名用中文（如 "Weald & Ember" 保留原名中的 & 符号）
- 类型子文件夹用中文命名（单曲、专辑、笔记、参考等）
- 纯信息类 Markdown 用 `.md`，纯文本数据用 `.txt`

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

### ⚠️ 写多文件时注意路径中的特殊字符

项目文件夹名如果包含 `&`（如 "Weald & Ember"），bash 命令中会解析为后台进程标志。有两种处理方式：

1. **首选：使用 `execute_code`（Python）** 处理含 `&` 的路径，避免 shell 转义问题
2. **或者：用 `write_file`（Hermes 原生工具）** — 该工具不经过 bash，不会受 `&` 影响
3. 尽量避免在 terminal 命令中直接传含 `&` 的路径

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.
