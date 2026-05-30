# Post-Release Artist Links — 发行后全平台艺人页查询

> 最后更新：2026-05-18
> 关联歌曲：千帆尽处 (Elian Chen)
> 发行方式：DistroKid (2026-05-16 提交，5/18 验证)

## Elian Chen 全平台艺人页

| 平台 | 艺人页链接 | 状态 | 备注 |
|------|-----------|------|------|
| **Spotify** | https://open.spotify.com/artist/3wD0iub0xdtu63ccMApzvH | ✅ 已上线 | 0 monthly listeners |
| **YouTube Music** | https://music.youtube.com/channel/UCcr3-2xxJ3YBTii96PqepQA | ✅ 已上线 | "Elian Chen - Topic" 自动频道 |
| **YouTube (单曲直链)** | https://www.youtube.com/watch?v=DcwSizGJkyM | ✅ 已上线 | 千帆尽处 |
| **Deezer** | https://www.deezer.com/artist/391302251 | ✅ 已上线 | 1 album, 0 fans |
| **Apple Music** | iTunes暂无结果（Elian Chen未搜到） | ⏳ 审核中 | DistroKid推送后3-7天 |
| **Amazon Music** | 未验证 | ⏳ 待上线 | DistroKid自动推送 |
| **Tidal** | API需countryCode参数 | ⏳ 待上线 | DistroKid自动推送 |
| **网易云音乐** | — | ❌ 未发行 | 需单独以"陈一"名义发行 |
| **QQ音乐** | — | ❌ 未发行 | 同上 |

## 查询方法论

### 1. Spotify
- 浏览器访问 `https://open.spotify.com/search/{艺名}/artists`
- 选择搜索结果的"Artists"标签
- 点击艺人名进入艺人页
- 从浏览器地址栏获取 URL

### 2. YouTube Music / YouTube
- 搜索：`https://www.youtube.com/results?search_query="{艺名}"`
- DistroKid发行后会自动创建 "艺名 - Topic" 频道
- 搜索歌名也能找到
- 使用 oEmbed API 验证：`https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={id}&format=json`

### 3. Deezer
- API 查询：`https://api.deezer.com/search/artist?q={url编码的艺名}`
- 返回 JSON 中 `data[].id` 即artist ID
- 艺人页：`https://www.deezer.com/artist/{id}`

### 4. Apple Music / iTunes
- API 查询：`https://itunes.apple.com/search?term={艺名}&entity=allArtist&limit=5`
- 注意：DistroKid 新艺人在 Apple Music 上可能需3-7天才会索引
- 返回的 `artistName` 精确匹配才有效（Elian ≠ Elaine）

### 5. 通用注意事项
- 代理问题：WSL环境下SOCKS5代理(socks5h://localhost:1080)会阻断部分API，需 `HTTP_PROXY= HTTPS_PROXY= NO_PROXY=*` 临时覆盖
- DistroKid的DK_SYN Cookie失效快(1-2天)，无法通过API查询发行状态
- 各平台上线时间不等：YouTube最快(~2天)，Apple Music最慢(3-7天)
- 国内平台（网易云/QQ音乐）需以"陈一"名义单独发行，不走DistroKid国际分发

## 关键词
elian chen 艺人页 音乐平台 发行验证 distrokid 上线检查
