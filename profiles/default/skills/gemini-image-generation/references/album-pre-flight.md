# Album Pre-Flight Checklist — DO NOT SKIP

## 重大版本更新（2026-05-18）

**🚨 废弃了：GitHub仓库方案（git push → Cloudflare Pages）**
**🚀 现用方案：仅限飞书云盘（Feishu Drive）**

> **严禁：** Git推送、更新GitHub相册仓库、Cloudflare Pages部署。
> **铁律：** 生图 → 上传飞书云盘 → 发飞书消息给安迪。三步走，无多余动作。

## Why This Exists

**The user has corrected me multiple times for forgetting to update the album after generating a photo.** The last correction (May 18, 2026): "你还在用旧相册，能不能更新你的记忆" + "那你倒是更新上去啊".

## The Hard Rule

> **飞书云盘必须先更新，再发飞书消息给安迪。**
> 
> 你不能把图发给用户直到它已经上传到飞书云盘。

## Execution Sequence

```
Step 0 — PRE-FLIGHT (PLAN):
  □ 确认图片已保存到本地

Step 1 — GENERATE:
  □ Generate image → save to /tmp/gemini_output.jpg（或类似路径）

Step 2 — 上传飞书云盘（MANDATORY BEFORE FEISHU NOTIFICATION）
  □ 用飞书API: drive/v1/files/upload_all
  □ 必须传 size 参数（文件实际字节数，否则报错）
  □ 目标文件夹 folder_token=N0wPfG49ZlJCErdjwUUcYdsUnyP
  □ 文件名：NN_name.jpg（NN = 文件夹现有文件最大编号+1）

Step 3 — 发飞书消息（ONLY AFTER UPLOAD SUCCEEDS）
  □ 上传图片到飞书消息API（im/v1/images + msg_type=image）
  □ 发送图片给安迪
  □ 不用附任何旧相册网址
```

## Feishu Drive Info

| Detail | Value |
|--------|-------|
| Folder token | `N0wPfG49ZlJCErdjwUUcYdsUnyP` |
| Upload API | `drive/v1/files/upload_all` |
| Required param | `size`（文件实际字节数，必须传否则报错） |
| 图片命名 | `NN_name.jpg`, NN = 文件夹现有文件最大编号+1 |
| Image send | `im/v1/images` + `msg_type=image`（先上传图片到im/v1/images拿image_key） |
| 错误流 | 如果size传错或token失效→用户收不到图。必须检查返回状态码。 |

## What NOT to Do

- ❌ 绝对不要推送到GitHub（alexander_repo仓库已废弃）
- ❌ 绝对不要更新Cloudflare Pages
- ❌ 绝对不要访问或提及旧相册网址 https://alexander-album.pages.dev/
- ❌ Never send the Feishu image before uploading to Feishu Drive
- ❌ Never ask "要不要加相册？" — it's not optional
- ❌ Never generate a second photo before uploading the first one
- ❌ Never forget the `size` parameter on drive/v1/files/upload_all

## Common Pitfalls (From Experience)

| 错误 | 后果 | 修复 |
|------|------|------|
| 忘记传size参数 | API报错，图片上不了云盘 | 检查文件大小：`stat -c%s /tmp/gemini_output.jpg` |
| 先发飞书消息再上传云盘 | 用户收到图但云盘没备份 | 铁律：先云盘，再飞书 |
| 记忆中的旧GitHub流程 | push到废弃仓库，浪费时间和API | 记忆已更新为仅飞书云盘 |
