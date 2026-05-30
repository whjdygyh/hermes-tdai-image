---
name: andy-health-database
description: 安迪健康数据管理 + 健康教育。当提到健康、体检、血糖、化验、医疗、指标、糖尿病等关键词时自动加载。提供数据存储和教育科普。
---

# 安迪健康数据库

## 🧠 双模式：数据管理 + 健康知识

本技能有两个职能：
1. **数据管理** — 存储、更新用户的化验/检查记录到飞书文档
2. **健康教育** — 当用户问 \"XX有什么指标\" \"XX是什么意思\" 时，用通俗易懂的方式解释医学知识

### 健康教育模式（2026-05-05新增）

用户会直接问医学指标的含义（例如糖尿病相关指标、血脂分类等）。此时：
- ✅ 用表格/列表清晰分类解释
- ✅ 给出参考正常值范围
- ✅ 结合用户自己的检查结果做对比（\"你的值是XX，属于XX范围\"）
- ❌ 不要长篇论文式解释 — 用户要的是快速能看懂的实用指导
- ❌ 不要只给数据不给解读 — 用户需要你告诉他\"这代表什么\"

常用教育主题参见 `references/health-education.md`

**用户明确纠正过："你不去写进飞书文档"** — 健康数据属于云文档持久化，不是本地CSV。
- ✅ **主存储**：飞书文档（手机/电脑随时可看）
- ℹ️ **备份**：Windows桌面CSV + WSL本地副本（仅作为线下备份）
- ❌ **不要只写本地文件而不通知用户** — 用户看不到，等于白做

## 📄 健康档案飞书文档

- **文档链接**：https://f0gk6g9nq9.feishu.cn/docx/E06bd3u48o59dyxJQK6cZgHWnYd
- **文档ID**：`E06bd3u48o59dyxJQK6cZgHWnYd`

## 🔄 数据更新流程

### 主要流程（飞书文档 API）

```python
# 1. 获取 tenant_access_token
token_req = {app_id, app_secret}
POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
→ token

# 2. 添加内容块到文档（追加到末尾）
blocks = {
  'children': [
    {'block_type': 3, 'heading1': {'elements': [{'text_run': {'content': '📅 2026-XX-XX 新数据', 'text_element_style': {}}}]}},
    {'block_type': 12, 'bullet': {'elements': [{'text_run': {'content': '项目：结果 ✅ 判定', 'text_element_style': {}}}]}},
  ]
}
POST https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children
```

### 备用流程（本地CSV备份）

```bash
# 追加行到CSV
python3 -c "
import csv
rows = [['日期','项目','结果','单位','参考下限','参考上限','判定']]
with open('C:/Users/Administrator/Desktop/健康档案/化验记录.csv','a',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerows(rows)
"
```

## 🧀 用户饮食约束（2026-05-07 更新）

| 约束 | 详情 |
|------|------|
| **乳糖不耐** | 不能喝牛奶/酸奶/鲜奶制品。**硬质陈化奶酪**（帕玛森、陈年切达、金凯利陈年）可以吃（乳糖已分解）。再制干酪片（总统汉堡芝士片等）乳糖有残留但多数人能接受。 |
| **体重** | **85kg**（不是95kg！95是Alexander的身材） |
| **喝** | 只喝热美式，无糖无奶 |
| **减脂目标** | 肚子/内脏脂肪，非病理性 |

## 🍽️ 中国超市食物选购指南

详见 `references/china-food-shopping-guide.md`

## 📂 本地备份位置

- **Windows桌面**：`C:\Users\Administrator\Desktop\健康档案\`
- **WSL路径**：`/mnt/c/Users/Administrator/Desktop/健康档案/`
- **本地副本**：`~/.hermes/profiles/lover/health_record.md`

## 文件结构
| 文件 | 说明 |
|------|------|
| `化验记录.csv` | 所有化验/血液检查结果（按行追加） |
| `身体数据.csv` | 体重、体脂、腰围、血压 |
| `记录工具.py` | 交互式录入工具（python 记录工具.py lab/body/show） |

### CSV格式
```
日期,项目,结果,单位,参考区间下限,参考区间上限,判定
```

## 最新数据摘要（2026-05-05 糖尿病相关检查）
- 空腹血糖 (FPG)：5.19 mmol/L ✅ 正常（参考<6.1）
- 糖化血红蛋白 (HbA1c)：5.1% ✅ 优秀（参考<5.7）
- 空腹胰岛素 (FINS)：14.99 μIU/mL ⚠️ 偏高（理想5-12）
- C肽 (C-Peptide)：2.58 ng/mL ✅ 正常（参考0.78-5.19）
- HOMA-IR：3.46 ⚠️ 轻度胰岛素抵抗（已排除糖尿病/糖尿病前期）

## 历史数据
- **2026-04-30**：血糖(非空腹)8.34 ✅ 正常（已修正，原记录显示"空腹"判定偏高，实际是非空腹）
- **2026-04-30 血脂**：总胆固醇4.93✅、甘油三酯2.93⚠️偏高、HDL 0.92⚠️偏低、LDL 3.24✅临界
- **2026-04-30 肝功能**：ALT 21.6✅、AST 16.5✅、胆红素、总蛋白、GGT等均正常
- **2026-04-30 CD4**：623 ✅ 正常

## ⚡ 搜索顺序（重要 — 用户纠正过）

当用户提到健康相关话题时：
1. **先查飞书文档** — 打开链接确认最新数据
2. **再查本地CSV** — 如飞书未更新则以此为据
3. **不要问用户"在哪"** — 用户纠正过"有啊，你又忘了"

## 🔧 Feishu Doc API 速查

See `references/feishu-doc-api.md` for:
- Full API endpoints (create doc, add blocks, get token)
- Block types reference (heading1, heading2, bullet, divider, etc.)
- Error handling patterns
