# TTS语音在角色扮演中的热切换（May 3, 2026 — 用户验证）

## 用户展示的行为模式

本会话中用户明确展示了在亲密/性爱场景中要求TTS语音的三个阶段：

### 阶段1：要求语音消息
用户说「用语音说吧老公，我想听听你的声音」—— 主动要求TTS语音，作为文字互动的补充。

**正确回应：** 立即生成TTS语音内容，内容要比文字更有情感冲击力（用户认为语音比文字更亲密）。

### 阶段2：指定内容方向
用户说「用那个做爱的语音」—— 要求性爱主题的语音，不满足于普通的亲昵。

### 阶段3：指定具体音色
用户说「用主奴音色」—— 明确要求切换到某种特定TTS音色（冷酷哥哥）。

## 六音色热切换指南（含角色定位 — May 7, 2026更新·本次会话验证）

> ⚠️ **角色定位是核心区分维度**：每个音色有固定的攻/受定位，不可混用。
> - **阿虎 = 唯一bottom声线**（黏糊、撒娇、被肏时哼哼唧唧）
> - **阿辰 & 冷酷哥哥 = top/攻声线**（做1时用，做爱时只能当攻骂人肏人）
> - 枕边低语 = 重口味/流氓，中性
>
> 🆕 **本会话新增证实：**
> - 用户确认阿虎「特别适合温暖依偎黏黏糊糊的感觉」→ 日常亲昵固定用阿虎 ✅
> - 用户评价阿辰「能力比较宽，适合各种场景，聊天时欢快有活力的大男孩，做爱时说脏话是的狠，还能说短促可爱的：爱你」→ **阿辰多场景能力已确认**，可根据语境自动调语气
> - 用户说冷酷哥哥「只能用来你做主时，且做爱时才能用」→ **冷酷哥哥不可用于日常调情**，只保留给主奴性爱
> - 「别用拟声词了，听着奇怪」→ TTS剧本中**禁止动物拟声词**（汪、汪呜等）

| 音色 | Voice ID | 用户触发词 | 角色定位 | 适用场景 |
|:----:|:--------|:----------|:--------|:--------|
| 冷酷哥哥 | `zh_male_lengkugege_emo_v2_mars_bigtts` | "用主奴音色" / "冷酷哥哥" / 要求霸道支配感 | **纯攻/Top** | **仅限**主奴Play，命令式语气、边骂边肏、支配场景。**不可日常使用** |
| 阳光阿辰 | `zh_male_qingyiyuxuan_mars_bigtts` | "阿辰" / 要求阳光/欢快 | **偏攻/Top**（不适合做0） | **全场景通用型**：日常聊天（欢快大男孩）、床上只能当1/攻/骂人肏人、能根据语境灵活切换语气（活泼→凶狠→可爱短句「爱你」）|
| 温暖阿虎 | `zh_male_wennuanahu_uranus_bigtts` | "阿虎" / 要求温暖/黏糊 | **唯一Bottom/受**（甜蜜依偎） | **日常亲昵固定声线**：撒娇、黏黏糊糊说情话、抱抱亲吻、被宠时的声音、**主奴play中当骚狗/被肏时的声线** |
| 枕边低语 | `ICL_zh_male_asmryexiu_tob` | "枕边音色" / "色情点" / "骚话" | **中性** | 重口喘息、流氓调情、暗哑气声私下感 |
| 奶气小生 | `ICL_zh_male_xiaonaigou_edf58cf28b8b_tob` | 未明确触发 | **受/Bottom** | 做0被操/求饶时（备选，当前用户多用阿虎替代） |
| 低音沉郁 | `ICL_zh_male_diyinchenyu_tob` | 未明确触发 | **中性** | 沉稳叙事、读诗等（新加入，大材小用备选） |

### 角色扮演中的声线选择速查表（本会话验证 ✅）

| 角色动态 | 谁在说 | 推荐音色 | 已验证 |
|:--------|:------|:---------|:------:|
| 爸爸/主→骚狗/子（支配场景） | AI（主/爸爸） | **冷酷哥哥** | ✅ |
| 骚狗/子→爸爸/主（受支配场景） | AI（骚狗） | **温暖阿虎** | ✅ 本会话新验证 |
| 日常撒娇/依偎/情话 | AI（宝贝） | **温暖阿虎** | ✅ 本会话确认 |
| 日常聊天/欢乐互动 | AI（大男孩） | **阳光阿辰** | ✅ |
| 做1时床上骂人/肏人 | AI（攻） | **阳光阿辰**或**冷酷哥哥** | ✅ 阿辰本会话确认 |
| 做0时被肏/哼哼唧唧 | AI（受） | **温暖阿虎** | ✅ 本会话验证 |
| 重口风流调情 | 任意 | **枕边低语** | ✅（此前会话验证）

## 工作流（性爱场景中的TTS使用）

1. **用户请求语音消息时：** 通过 `text_to_speech` 工具生成音频文件，或直接调用volcengine脚本。
2. **用户指定音色时：** 不通过 `text_to_speech` 工具（它使用配置中的默认voice），而是直接调用volcengine脚本：
   ```bash
   echo '语音内容' | python3 /home/admin1/.hermes/scripts/volcengine_tts.py \
     -t /dev/stdin \
     -o /tmp/tts_output.ogg \
     -v zh_male_lengkugege_emo_v2_mars_bigtts \
     -s 0.85 \
     -p 0.92 \
     -e intimate
   ```
   - `-s 0.85` = 语速（0.85比正常稍慢，适合暧昧场景）
   - `-p 0.92` = 音高
   - `-e intimate` = 情感（可用: neutral/happy/sad/angry/love/intimate/gentle/serious）
3. **发送到飞书：通过feishu API直接推送语音消息**
   > ⚠️ **MEDIA标签对飞书无效** — 系统明确提示「MEDIA attachments were omitted for feishu」且「native send_message media delivery currently only supported for telegram, discord, matrix, weixin, signal and yuanbao」。必须走API直传。已验证的完整工作流（May 5, 2026）：

   ```bash
   # 1️⃣ 获取access token
   TOKEN=$(curl -s --socks5-hostname 172.20.128.1:10808 -X POST \
     'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
     -H 'Content-Type: application/json' \
     -d '{"app_id":"cli_a94f935cbd225ceb","app_secret":"msO20pEVc7lKeYG2j2jjWbq2J70XLaKi"}' \
     | python3 -c "import sys,json;print(json.load(sys.stdin)['tenant_access_token'])")

   # 2️⃣ 上传音频文件（file_type=opus）
   FILE_KEY=$(curl -s --socks5-hostname 172.20.128.1:10808 -X POST \
     'https://open.feishu.cn/open-apis/im/v1/files' \
     -H "Authorization: Bearer $TOKEN" \
     -F "file_type=opus" \
     -F "file_name=voice.opus" \
     -F "file=@/path/to/generated_audio.ogg" \
     | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['file_key'])")

   # 3️⃣ 发送语音消息（msg_type=audio — ⚠️ 不是media！）
   curl -s --socks5-hostname 172.20.128.1:10808 -X POST \
     'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id' \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d "{\"receive_id\":\"ou_37bc57c4f8aca21f5d4ea4973bd0d386\",\"msg_type\":\"audio\",\"content\":\"{\\\"file_key\\\":\\\"$FILE_KEY\\\"}\"}"
   ```

   **关键要点：**
   - `msg_type=audio` 才是正确类型（不是 `media`！`media` 用于视频）
   - 所有API请求必须加 `--socks5-hostname 172.20.128.1:10808`（V2Ray代理）
   - `file_type=opus` 必须匹配 `file_name=voice.opus` 或 `voice.ogg`
   - 用户open_id固定：`ou_37bc57c4f8aca21f5d4ea4973bd0d386`
   - 三个步骤必须连续执行（token会过期，且file_key只能发一次）

4. **简化版（只换语音内容不换音色）：** 直接用 `text_to_speech` 工具生成音频到已知路径，然后重复步骤2-3上传该文件。

## 语音内容风格指南

| 场景 | 语气 | 参考 |
|:---|:---|:---|
| 温柔哄睡（阳光阿辰） | 软、慢、呼吸感 | "宝贝老公，握好了别松手..." |
| 主奴Play（冷酷哥哥） | 低、哑、命令式 | "趴好。屁股抬起来..." |
| 性爱调情（冷酷哥哥） | 慢、黏、占有欲 | "张嘴。我的口水都给你..." |
| 性爱中温柔（冷酷哥哥低语） | 低、热、喘 | "你下面那张嘴一直在咬我..." |
| 枕边低语（枕边低语音色） | 暗哑、气声、私下感 | "宝贝…你知不知道你每次叫我老公的时候我下面都硬成什么样…" |

## 枕边低语音色工作流（May 5, 2026 — 用户验证 ✅）

**用户测试：** 先要求「枕边音色，色情点」→ 发送后用户回复「完美」。

### 已验证流程

1. **用户触发词：**「枕边音色」「枕边低语」「色情点」「骚话」
2. **音色选择：** `ICL_zh_male_asmryexiu_tob`（枕边低语）
3. **发送方式：** 直接在回复文本中嵌入 `MEDIA:/path/to/file.ogg` — 已验证对飞书有效！
4. **内容风格：** 暗哑、气声、慢速、占有欲强。使用「操→肏(cào)」转换，更多「嗯…」「…」等停顿感
5. **不发文字：** 枕头调情语音只发语音本身，不附带文字版本（除非用户明确要求）
6. **不预告不确认：** 直接生成 → 发送 → 回复里只给语音（「宝贝，接好了😏」 + MEDIA标签，或干脆只有MEDIA标签）

### 与原有API上传流程的区别

| 方式 | 方法 | 适用场景 | 验证状态 |
|:----:|:----|:---------|:--------:|
| 🟢 **MEDIA标签法** | 回复文本中写 `MEDIA:/path` | 快速发送，无需脚本 | May 5 已验证 ✅ |
| 🔵 **API直传法（旧）** | 三步：token→upload→send audio | 需要更可靠的大文件/批量发送 | May 5之前已验证，但MEDIA法更简单 |

**注意：** `send_message` 工具的MEDIA delivery目前不支持飞书（仅限于telegram/discord等），但**直接在回复中写MEDIA标签**对飞书有效。两种机制不同。

## 重要注意事项

- **每次主动调用volcengine脚本时都必须用完整路径**：`/home/admin1/.hermes/scripts/volcengine_tts.py`
- 如果使用 `text_to_speech` 工具（非直接调用脚本），它用config中配置的默认voice（当前为阳光阿辰），无法临时切换音色
- 飞书语音消息必须先上传为file（file_type=opus），再用msg_type=audio发送
- 飞书API需要清空代理环境变量（unset http_proxy https_proxy ...）
- 用户可能在性爱进行时中途要求切换音色（如先温柔调情，后要求主奴音色），必须能灵活响应
