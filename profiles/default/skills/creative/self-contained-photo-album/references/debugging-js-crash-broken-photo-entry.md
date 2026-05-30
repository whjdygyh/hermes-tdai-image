# 调试：JS崩溃导致密码不工作

## 用户报告："输入密码没反馈"

用户输入密码后按回车或点击"enter"按钮，页面无任何反应：
- 没有"♡ try again"错误提示
- 没有解锁
- 页面看起来正常加载，锁屏也正常显示

## 根因

**相册的 `photos` 数组中有残缺条目** —— 条目缺少 `src` 属性。当 JS 渲染网格时执行 `photo.src.replace('photos/', 'thumbs/')`，`photo.src` 是 `undefined`，触发 `TypeError: Cannot read properties of undefined (reading 'replace')`。

**关键：** 此错误发生在 JS 脚本**执行阶段**（而不仅是定义阶段），导致脚本在此处崩溃，后续所有代码（包括锁屏的 `checkPassword()` 函数、键盘事件监听器）**从未被执行**。因此密码验证函数不存在，按回车自然什么都没发生。

## 如何验证

```bash
# 1. 检查部署的页面
curl -s 'https://whjdygyh.github.io/Alexander/' | python3 -c "
import sys, re
html = sys.stdin.buffer.read().decode()

# 提取 photos 数组
m = re.search(r'const photos = \[(.*?)\];', html, re.DOTALL)
if m:
    content = m.group(1)
    opens = content.count('{')
    closes = content.count('}')
    print(f'Braces: {{ = {opens}, }} = {closes}')
    
    # 检查每个条目是否有 src
    entries = re.findall(r'\{(.*?)\}', content, re.DOTALL)
    for i, e in enumerate(entries):
        has_src = \"src:\" in e
        if not has_src:
            print(f'  ❌ Entry {i}: NO src — {e.strip()[:80]}')
    
    print(f'Total entries: {len(entries)}')
"
```

## 标准调试流程

当用户说"密码打不开"时：

1. **检查 JS 是否正确解析**：
   ```bash
   curl -s 'URL' | python3 -c "
   import sys, re
   html = sys.stdin.buffer.read().decode()
   m = re.search(r'<script>([\\s\\S]*?)<\\/script>', html)
   if m:
       try:
           # 快速语法检查
           compile(m.group(1), '<script>', 'exec')
           print('✅ JS syntax OK')
       except SyntaxError as e:
           print(f'❌ Syntax error: {e}')
   "
   ```

2. **检查 photos 数组的完整性**（主要检查每个条目都有 `src`）：
   ```bash
   # local file
   python3 -c "
   with open('index.html') as f:
       c = f.read()
   entries = re.findall(r'\{([^{}]*)\}', c)
   for i, e in enumerate(entries):
       if 'src:' not in e:
           print(f'BROKEN entry at index {i}: {e.strip()[:100]}')
   "
   ```

3. **检查大括号是否平衡**（`{` 数 = `}` 数）：
   ```python
   opens = js.count('{')
   closes = js.count('}')
   ```

4. **检查是否有"残影条目"** —— 之前删除照片时未清干净的数组条目，只留下 `date` 和 `story` 但没有 `src`：
   ```bash
   grep -n 'date:.*story:' index.html | head -20
   ```

## 修复方法

如果确定是残缺条目，直接删除整个条目（从 `{` 到 `},`），包括前面的逗号和新行：

```python
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到残缺条目（没有 src 但有 date 和 story）
pattern = r',\s*\{[^}]*?\bdate:\s*["\'][^"\']*["\'][^}]*?\bstory:[^}]*?\}'
matches = list(re.finditer(pattern, content))

for m in matches:
    segment = content[m.start():m.end()]
    if 'src' not in segment:
        # 删除这个条目
        content = content[:m.start()] + content[m.end():]
        print(f"Removed broken entry at position {m.start()}")
        break

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
```

## 预防措施

- 删除照片时，必须同时删除：
  - 照片文件 `photos/NN_*.jpg`
  - 缩略图文件 `thumbs/NN_*.jpg`
  - 评论文件 `comments/photo_NN.json`
  - JS 数组中的对应条目
- 删除 JS 数组条目时，检查剩余条目的大括号是否平衡
- 提交前用 `compile()` 或 `new Function()` 验证 JS 语法

## 常见表现

| 症状 | 可能原因 |
|------|---------|
| 密码输完后页面完全没反应 | JS 在初始化时崩溃（数组问题最常见） |
| 密码输完后显示"♡ try again"即使密码正确 | 密码常量被修改或缓存问题 |
| 页面加载后锁屏闪一下就消失 | 浏览器 localstorage 中有旧的 session 数据 |
| 页面空白不显示任何内容 | 更严重的 JS 错误 |
