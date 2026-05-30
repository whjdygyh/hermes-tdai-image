# Feishu Doc API — Document Management Reference

## Overview
Create and update Feishu Docs from the Linux terminal using the Feishu Open API.
Tested and working (2026-05-05). Token expires ~2 hours; re-fetch each session.

## Authentication

```bash
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id":"cli_a94f935cbd225ceb",
    "app_secret":"msO20pEVc7lKeYG2j2jjWbq2J70XLaKi"
  }' | python3 -c "import sys,json;print(json.load(sys.stdin)['tenant_access_token'])")
```

## Create a New Document

```bash
curl -s -X POST "https://open.feishu.cn/open-apis/docx/v1/documents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"文档标题"}' | python3 -m json.tool
```

Returns: `document_id` (the doc URL is `https://f0gk6g9nq9.feishu.cn/docx/{document_id}`)

## Add Content Blocks (Append to Document)

```bash
curl -s -X POST "https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"children": [...]}' | python3 -m json.tool
```

## Block Types Reference

| `block_type` | Type | Code |
|:---:|---|---|
| 1 | Page (root) | auto |
| 2 | Text paragraph | `{'block_type': 2, 'text': {'elements': [{'text_run': {'content': '...', 'text_element_style': {}}}]}}` |
| 3 | Heading 1 | `{'block_type': 3, 'heading1': {'elements': [{'text_run': {'content': '...', 'text_element_style': {}}}]}}` |
| 4 | Heading 2 | `{'block_type': 4, 'heading2': {'elements': [{'text_run': {'content': '...', 'text_element_style': {}}}]}}` |
| 5 | Heading 3 | `{'block_type': 5, 'heading3': {...}}` |
| 10 | Ordered list | `{'block_type': 10, 'ordered': {'elements': [...]}}` |
| 11 | Bullet | `{'block_type': 11, 'bullet': {'elements': [...]}}` |
| 12 | Toggle list | `{'block_type': 12, 'bullet': {'elements': [...]}}` *(note: 11 and 12 are both bullet-like)* |
| 22 | Divider | `{'block_type': 22, 'divider': {}}` |
| 27 | Quote | see below |
| 29 | Callout | see below |

## Text Element Styling

```python
# Basic text run
{'text_run': {'content': 'text here', 'text_element_style': {}}}

# With formatting
{'text_run': {'content': 'bold text', 'text_element_style': {
    'bold': True,
    'italic': False,
    'underline': False,
    'strikethrough': False,
    'inline_code': False
}}}
```

## Full Python Example (Add Content to Existing Doc)

```python
import requests, json

token = '...'  # fetched above
doc_id = 'E06bd3u48o59dyxJQK6cZgHWnYd'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

url = f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children'

blocks = {
    'children': [
        {'block_type': 3, 'heading1': {'elements': [{'text_run': {'content': '📅 标题', 'text_element_style': {}}}]}},
        {'block_type': 12, 'bullet': {'elements': [{'text_run': {'content': '内容...', 'text_element_style': {}}}]}},
        {'block_type': 22, 'divider': {}},
    ]
}

resp = requests.post(url, headers=headers, json=blocks)
print(resp.json())
```

## Block Types for Health Data

Health archive typically uses:
- **Heading 1** (block_type=3) — section titles: "基本信息", "2026-XX-XX 检查", "小结"
- **Heading 2** (block_type=4) — subsection: "血糖类", "胰岛功能", "血脂类"
- **Bullet** (block_type=12) — individual results with emoji indicators
- **Divider** (block_type=22) — between sections

## Error Handling

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 200 / code=0 | Success | ✅ |
| 401 | Token expired | Re-fetch token |
| 403 | No permission | Check app_id permissions |
| 404 | doc_id not found | Verify doc_id |
| 400 / code=xxx | Bad request | Check JSON structure |

## Known Document IDs

- 安迪健康档案: `E06bd3u48o59dyxJQK6cZgHWnYd`
