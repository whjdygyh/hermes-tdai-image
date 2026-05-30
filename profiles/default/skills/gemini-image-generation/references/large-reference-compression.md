# 参考图过大导致 curl 超时（本会话亲身教训）

## 问题描述

使用双参考图（face + body）生成 Gemini 图片时，如果参考图过大，curl 上传可能超时失败（exit code 28, rc=28）。

**本会话实测数据：**
- Skin #1 原始照片：8508KB（3584×4800 JPEG）
- 通过 `https_proxy=socks5h://localhost:1080` 代理时：连接被拒
- 通过 `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY` + 直连：curl 超时（max-time 300s 不够）
- 根因：8.5MB 图片 base64 编码后约 11.3MB，加上另一张 body ref (2.5MB)，总载荷超过 14MB，curl 上传阶段超时

## 解决方案：压缩参考图

```python
from PIL import Image
from pathlib import Path

def compress_reference(input_path, output_path=None, quality=85):
    """压缩参考图到适合 Gemini API 的大小"""
    img = Image.open(input_path)
    if output_path is None:
        stem = Path(input_path).stem
        output_path = f'/tmp/{stem}_compressed.jpg'
    img.save(output_path, 'JPEG', quality=quality, optimize=True)
    return output_path
```

## 实测结果

| 原图大小 | 压缩后大小 | quality | 是否可靠 | 备注 |
|---------|-----------|:-------:|:--------:|------|
| 8508KB | 1728KB | 85 | ✅ 可靠 | 面部特征保留完好 |
| 2511KB | 513KB | 85 | ✅ 可靠 | 腿部参考图 |
| 合计 11019KB | 2241KB | - | ✅ 成功 | 总 base64 ~3MB |

## 经验规则

- **单张参考图 ≤ 2MB**（压缩后）→ 可靠
- **总 base64 载荷 ≤ 3MB**（两张压缩图合计）→ 可靠
- 超过此范围 → curl 容易超时（即使 max-time 300 秒）
- **JPEG quality=85 optimize=True** 是最佳平衡点

## 重要注意事项

1. 面部参考图 quality≥85，太低会模糊导致 Gemini 无法匹配面部特征
2. 身体/腿部参考图可接受 quality=80
3. 优先压缩大的那张（face ref 通常是全身照/大头照，体积最大）
4. 压缩后保存到 `/tmp/`，不要覆盖原图
5. 同时使用 face + body 两张参考图时，计算总载荷
6. 如果还是超时，尝试降分辨率为 1440p 或使用单参考图方案
