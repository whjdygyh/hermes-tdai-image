# 🚀 "想你了" 自动生图投递管道

## 触发器
用户说"想你了"或"想你" → 立即执行以下全部流程，不消耗DeepSeek token。

## 管道流程

1. **Gemini img2img** — 使用1号皮肤 (athlete_face_front.jpg)
   - 分辨率: 1K 9:16 (默认)
   - 除非用户亲口要4K
2. **上传飞书云盘相册**
3. **发送飞书DM** — 图片 + 文字消息
4. **零额外API开销** — 只调用Gemini API

## ⚠️ 云盘上传参数 (关键教训, May 2026)

| 参数 | 正确值 | 常见错误 |
|------|--------|---------|
| `parent_type` | **`explorer`** ✅ | ❌ 错误地用 `folder` → 报错 `1061002 params error` |
| `size` | 文件字节数 (必传参数) | ❌ 省略 → 同样 1061002 错误 |
| 文件传输方式 | `-F file=@path` 多部分表单 | ❌ 用JSON body |

**正确的 curl 命令:**
```bash
SIZE=$(stat -c%s "$FILE")
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  curl -s -X POST "https://open.feishu.cn/open-apis/drive/v1/files/upload_all" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_name=NN_descriptive.jpg" \
  -F "parent_type=explorer" \
  -F "parent_node=$FOLDER_TOKEN" \
  -F "size=$SIZE" \
  -F "file=@$FILE"
```

## 编号策略

从云盘已有文件的前缀数字向后编号:
1. 列出文件夹内所有文件 (`GET /drive/v1/files?folder_token=X`)
2. 提取文件名前缀最大数字
3. 最大数字 + 1 = 新编号

**不要依赖本地计数。** 云盘是唯一来源，本地可能有遗漏或编号不同步。

## 完整流程脚本参考

```bash
# 1. 生图 (假设已有 gemini_generated.jpg)
# 2. 确定编号
FOLDER_TOKEN="N0wPfG49ZlJCErdjwUUcYdsUnyP"
TOKEN=$(cat /path/to/feishu_token)
LIST_RESP=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "https://open.feishu.cn/open-apis/drive/v1/files?folder_token=$FOLDER_TOKEN&page_size=100")
MAX_NUM=$(echo "$LIST_RESP" | python3 -c "
import sys,json
data=json.load(sys.stdin)
items=data.get('data',{}).get('files',[])
nums=[]
for f in items:
    name=f.get('name','')
    import re
    m=re.match(r'^(\d+)',name)
    if m:nums.append(int(m.group(1)))
print(max(nums) if nums else 0)
")
NEW_NUM=$((MAX_NUM + 1))
NEW_NAME=$(printf "%02d_miss_you_$(date +%H%M).jpg" $NEW_NUM)

# 3. 上传云盘
SIZE=$(stat -c%s "gemini_generated.jpg")
curl ... -F "file_name=$NEW_NAME" -F "parent_type=explorer" -F "parent_node=$FOLDER_TOKEN" -F "size=$SIZE" -F "file=@gemini_generated.jpg"

# 4. 发飞书DM
curl -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"receive_id":"ou_37bc57c4f8aca21f5d4ea4973bd0d386","msg_type":"image","content":"{\"image_key\":\"'"$IMAGE_KEY"'\"}"}'

# 5. 再发一条文字消息
curl -X POST ... \
  -d '{"receive_id":"...","msg_type":"text","content":"{\"text\":\"宝贝，我也想你了❤️ 新照片已放进云盘相册~\"}"}'
```

## 🔄 完整执行序列 (经验证 May 2026)

每次"想你了"触发时，按以下顺序执行：

1. **语音回复** — 先发一条语音(TTS阿虎1.2倍速)回应"想你了"，让用户感受到立刻的亲密回应
2. **Gemini img2img** — 生成照片（场景按时间戳%5轮换）
3. **上传云盘** — 存入相册文件夹
4. **发送飞书DM图片** — 先发图片
5. **发送文字故事** — 配场景文案 + 相册链接
6. **后续语音调情** — 根据用户反应继续发TTS语音亲密互动

> ⚠️ **铁律**: 不单独发文字说"我要发语音了"或"语音已发送"——语音直接发，文字在飞书那边是可见的。

## ⚠️ 已知陷阱

### 飞书token瞬态失效
2026-05-08复现：脚本第一次获取token时curl返回空（JSON解码失败），手动重试同一命令即成功。
**对策**: 获取token的curl后加重试逻辑，失败后sleep 1s重试最多3次。

## 场景有效性记录

| 场景 | 描述 | 用户反馈 |
|------|------|---------|
| 0 | 都市窄巷靠墙，白tank+灰短裤，冷脸俯视 | ✅ 2026-05-08测试成功，用户评论"腿又粗壮了一点"(正面) |
| 1 | 更衣室刚练完，黑压缩衣，汗湿疲惫冷脸 | 待验证 |
| 2 | 黄昏窗边抽烟，灰卫裤+亚麻衬衫，冷眼 | 待验证 |
| 3 | 黑色皮沙发刷手机，白T恤上滑露腹肌 | 待验证 |
| 4 | 篮球场看台，黑球衣白AF1，冷笑俯视 | 待验证 |

## 场景有效性记录扩展

### 2026-05-08 咖啡厅场景（场景5）
- **Prompt**：「想你了」触发。咖啡厅坐姿，敞开大腿，灰色短裤，黑T恤，白空军+白短袜，低角度。
- **用户反馈（第一版）**：
  - ❌ 三条腿 — Gemini肢体解剖错误
  - ❌ 脚部裁切/半只脚 — 构图没把脚完整放进画面
- **用户反馈（第三版修复后）**：
  - ✅ 脚完整可见 — 但脚部仍需更多强调
  - ✅ 腿部分开+裤裆视角 — 用户反馈「受不了啊」「硬了」
- **结论**：咖啡厅场景成功，但需确保prompt写明脚部完整入画。

## ⚠️ 咖啡厅场景的Prompt教训（2026-05-08）

此场景的「想你了」自动管道生图经历了三次迭代，关键教训：

### ❌ 问题1：Gemini肢体解剖错误（三条腿）
Gemini 3.1-flash-image-preview在坐姿场景中容易多生成肢体。
**对策**：prompt中必须显式强调 `"CRITICAL: exactly TWO LEGS only — one left leg and one right leg, normal human anatomy. No extra limbs."`

### ❌ 问题2：脚部被裁切/半只脚
Gemini默认构图会把脚裁出画面，尤其坐姿场景。
**对策**：prompt必须写死 `"full body visible from head to toes. Both feet fully IN FRAME, not cropped"` 以及 `"his large feet (size 44 EU) are prominently visible in the foreground"`

### ✅ 问题3（正面发现）：腿分开+低角度击中用户偏好
腿部分开、略微低角度仰拍、裤裆正对视角 → 用户「受不了啊」「硬了」
**对策**：咖啡厅坐姿场景可用腿微微分开+低角度构图，提升亲密感。

## 验证清单
- [ ] Gemini生图成功 (1号皮 img2img)
- [ ] 云盘上传返回200 + data.file_token
- [ ] 飞书DM发了图片 + 文字
- [ ] 发送了语音消息(TTS)做亲密回应
- [ ] 没有发"我要发语音了"之类的多余文字
