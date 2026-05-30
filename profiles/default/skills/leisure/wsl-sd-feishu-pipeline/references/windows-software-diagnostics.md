# Windows 软件/进程诊断（从 WSL 出发）

## 适用场景

当用户询问 Windows 某个软件是否在运行、某个进程是否活着、某个服务是否已安装时，Hermes agent 需要通过 WSL 查询 Windows 宿主机状态。

## 核心挑战：cmd.exe 的 UNC 路径问题

WSL 当前目录通常是一个 Linux 路径（如 `/home/admin1`），而 Windows `cmd.exe` 不支持将 UNC 路径（`//wsl.localhost/...`）作为当前目录：

```
C:\Windows\System32\cmd.exe 启动时会报：
"CMD.EXE was started with the above path as the current directory.
UNC paths are not supported. Defaulting to Windows directory."
```

**解决方法：使用 `workdir=/mnt/c` 或绝对路径调用**

```bash
# ❌ 直接在 WSL 路径下调用 cmd.exe 会报 UNC 警告
cmd.exe /c "tasklist"

# ✅ 用 workdir 规避
terminal(command="cmd.exe /c \"tasklist /FI \\\"IMAGENAME eq SunloginClient.exe\\\"\"", workdir="/mnt/c")

# ✅ 或用绝对路径
terminal(command="/mnt/c/Windows/System32/cmd.exe /c \"tasklist\"", workdir="/mnt/c")
```

## 方法一：Windows 任务管理器（tasklist.exe）

检查特定进程是否在运行：

```bash
# 检查进程是否存在（先查进程名，再用 findstr 过滤）
terminal(command="cmd.exe /c \"tasklist /NH | findstr /I Sunlogin\"", workdir="/mnt/c")
# 输出示例:
# SunloginClient.exe              11760 Console                    1     78,980 K

# 如果返回空行 → 进程不存在
# 如果返回进程信息 → 进程在运行

# 常见远程桌面软件进程名
# Sunlogin → SunloginClient.exe / SunloginService.exe
# TeamViewer → TeamViewer_Service.exe / TeamViewer.exe
# AnyDesk → AnyDesk.exe
# 向日葵 → SunloginClient.exe
# ToDesk → ToDesk.exe / ToDesk_Service.exe
```

**tasklist 输出格式化：** 默认 tasklist 输出含表头，`/NH`（No Header）去掉表头，`/FO CSV` 输出 CSV 格式方便解析。

```bash
# CSV 格式（适合脚本解析）
terminal(command="cmd.exe /c \"tasklist /FO CSV /NH | findstr /I Sunlogin\"", workdir="/mnt/c")
```

## 方法二：Windows PowerShell（更强大的进程/服务查询）

PowerShell 的 `Get-Process` 和 `Get-Service` 比 tasklist 更灵活。

### 查进程

```bash
# ⚡ 关键：PowerShell 的 $ 符号会与 bash 冲突！必须用单引号或转义
terminal(command="cmd.exe /c \"powershell.exe -Command \\\"Get-Process -Name '*Sunlogin*' -ErrorAction SilentlyContinue | Select-Object Name, Id, StartTime\\\"\"", workdir="/mnt/c")

# 如果进程在运行 → 输出 Name, Id, StartTime
# 如果进程不存在 → 无输出（空行）
```

### 查服务

```bash
# 检查服务是否安装和运行
terminal(command="cmd.exe /c \"powershell.exe -Command \\\"Get-Service -Name '*Sunlogin*' -ErrorAction SilentlyContinue | Select-Object Name, Status, StartType\\\"\"", workdir="/mnt/c")

# 输出示例（服务存在）:
# Name                          Status   StartType
# SunloginService               Running  Automatic

# 如果服务不存在 → 无输出
```

### PowerShell 引号嵌套规则（重要）

从 bash 调用 PowerShell 时，引号嵌套顺序为：

```
最外层: cmd.exe /c "..."
中间层: powershell.exe -Command "..."
最内层: Get-Process -Name '*Pattern*' -EA SilentlyContinue | Select Name,Id
```

**规则：**
- 最外层双引号 `"..."` 给 cmd.exe
- 内层的 PowerShell 双引号需要转义为 `\"`
- PowerShell 的单引号 `'...'` 不需要转义（bash 不处理单引号内的内容）

```bash
# ✅ 正确：PowerShell 双引号转义
cmd.exe /c "powershell.exe -Command \"Get-Service | Where-Object {$_.Name -like '*Sunlogin*'}\""

# ❌ 错误：$_.Name 会被 bash 当作变量解析
cmd.exe /c "powershell.exe -Command "Get-Process | Where-Object {$_.Name -like '*Sunlogin*'}""
```

**关于 `$_` 的特殊处理：** 在 bash 双引号中，`$_` 会被替换为 bash 的最后一个参数。如果不想转义每个 `$`，有两种方案：

**方案 A：用单引号包裹 PowerShell 脚本块（推荐）**
```bash
# PowerShell 代码外层的双引号内，用 '' 包裹 $_ 等特殊字符
cmd.exe /c "powershell.exe -Command \"Get-Service | Where-Object { '$'_.Name -like '*Sunlogin*' }\""
```

**方案 B：用文件传递**
```bash
# 把 PowerShell 脚本写入文件，然后执行
write_file(path="/tmp/check_win.ps1", content='Get-Process -Name "*Sunlogin*" -ErrorAction SilentlyContinue | Format-Table Name,Id,StartTime')
terminal(command="powershell.exe -File /tmp/check_win.ps1", workdir="/mnt/c")
```

## 方法三：搜索 Windows 文件系统

当不知道进程/服务名时，直接搜索软件安装路径：

```bash
# 搜索向日葵相关文件和目录（常用安装路径）
mkdir -p /tmp/winfind
find /mnt/c/Users/ -maxdepth 5 -iname "*sunlogin*" -o -iname "*oray*" 2>/dev/null | head -20
# 常见结果：
# /mnt/c/Users/Administrator/AppData/Roaming/Oray
# /mnt/c/Users/Administrator/Documents/Sunlogin Files

# 搜索 ProgramData（系统级安装）
find /mnt/c/ProgramData/ -maxdepth 4 -iname "*sunlogin*" -o -iname "*Sunlogin*" 2>/dev/null | head -10
# 常见结果：
# /mnt/c/ProgramData/Oray/SunloginClientLite
```

**find 搜索要点：**
- `-maxdepth N` 控制搜索深度（Windows 目录结构深，设 4-5 够用）
- `-iname` 不区分大小写
- `2>/dev/null` 忽略权限错误（很多 Windows 目录 WSL 无法访问）
- 先搜 `AppData/Roaming`（用户级安装），再搜 `ProgramData`（系统级安装）
- 用 `head` 限制输出行数

### 检查常见安装路径

```bash
# 向日葵（Oray Sunlogin）
ls -la "/mnt/c/Program Files (x86)/Oray/Sunlogin/" 2>/dev/null
ls -la "/mnt/c/Program Files/Oray/Sunlogin/" 2>/dev/null

# TeamViewer
ls -la "/mnt/c/Program Files/TeamViewer/" 2>/dev/null

# AnyDesk
ls -la "/mnt/c/Program Files (x86)/AnyDesk/" 2>/dev/null
ls -la "/mnt/c/Program Files/AnyDesk/" 2>/dev/null

# ToDesk
ls -la "/mnt/c/Program Files (x86)/ToDesk/" 2>/dev/null
```

## 方法四：检查 Windows 服务注册

```bash
# 用 sc 命令查询服务状态
terminal(command="cmd.exe /c \"sc query SunloginService | findstr STATE\"", workdir="/mnt/c")
# 输出：
#   STATE                       : 4  RUNNING   → 服务在运行
#   STATE                       : 1  STOPPED    → 服务已停止
# 空行或无输出                     → 服务未安装

# 列出所有服务并过滤（搜索已安装的服务名）
terminal(command="cmd.exe /c \"sc query state= all | findstr /I Sunlogin\"", workdir="/mnt/c")
```

## 方法五：检查 Windows 启动项/注册表

```bash
# 检查启动文件夹
terminal(command="cmd.exe /c \"dir \\\"C:\\Users\\Administrator\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\\" | findstr /I Sunlogin\"", workdir="/mnt/c")

# 检查注册表启动项
terminal(command="cmd.exe /c \"reg query HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run | findstr /I Sunlogin\"", workdir="/mnt/c")

# 检查所有用户启动项
terminal(command="cmd.exe /c \"reg query HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run | findstr /I Sunlogin\"", workdir="/mnt/c")

# ⚠️ reg query 可能因权限问题失败，备选方案
```

## 综合诊断案例：向日葵（Sunlogin）

```bash
echo "=== Sunlogin 诊断 ==="

echo "1. 查进程..."
cmd.exe /c "tasklist /NH | findstr /I Sunlogin"

echo "2. 查服务..."
cmd.exe /c "sc query SunloginService | findstr STATE"

echo "3. 查安装痕迹..."
find /mnt/c/ -maxdepth 4 -iname "*sunlogin*" 2>/dev/null | head -5

echo "4. 查启动项..."
cmd.exe /c "reg query HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run | findstr /I Sunlogin" 2>/dev/null
```

**完整 Python 诊断脚本（可复用）：**

```python
import subprocess, json

results = {}

# 查进程
r = subprocess.run(
    ["cmd.exe", "/c", "tasklist /NH /FO CSV | findstr /I Sunlogin"],
    capture_output=True, text=True, timeout=30, cwd="/mnt/c"
)
results["process"] = r.stdout.strip() or "NOT RUNNING"

# 查服务  
r = subprocess.run(
    ["cmd.exe", "/c", "sc query SunloginService | findstr STATE"],
    capture_output=True, text=True, timeout=30, cwd="/mnt/c"
)
results["service"] = r.stdout.strip() or "NOT INSTALLED"

# 查安装
r = subprocess.run(
    ["find", "/mnt/c/ProgramData/", "-maxdepth", "3", "-iname", "*sunlogin*"],
    capture_output=True, text=True, timeout=30
)
results["install_paths"] = r.stdout.strip().split("\n") if r.stdout.strip() else []

print(json.dumps(results, indent=2))
```

## 常见的远程桌面/远程控制软件

| 软件 | 进程名 | 服务名 | 安装目录（常见） |
|------|--------|--------|-----------------|
| 向日葵（Sunlogin/Oray） | `SunloginClient.exe` | `SunloginService` | `C:\ProgramData\Oray\SunloginClientLite` |
| TeamViewer | `TeamViewer.exe` | `TeamViewer_Service` | `C:\Program Files\TeamViewer` |
| AnyDesk | `AnyDesk.exe` | `AnyDesk_Service` | `C:\Program Files (x86)\AnyDesk` |
| ToDesk | `ToDesk.exe` | `ToDesk_Service` | `C:\Program Files (x86)\ToDesk` |
| 微软远程桌面 | `mstsc.exe` | `TermService` | 系统内置 |
| VNC | `vncserver.exe` | `vncserver` | `C:\Program Files\VNC` |

## 注意事项

1. **UNC 路径警告可忽略** — cmd.exe 的 "UNC paths are not supported" 只是一个警告，实际大部分命令仍能正确执行，只会改变 cwd 到 Windows 目录
2. **权限问题** — 有些路径（如 `C:\Windows\System32\config`）WSL 无法访问，用 `2>/dev/null` 静默忽略
3. **PowerShell 执行策略** — `powershell.exe -Command` 不受执行策略限制，比 `-File` 更稳定
4. **不要用 `execute_code()`** — 飞书 API 和 Windows 交互都应在 terminal() 中完成，`execute_code()` 的沙箱无法访问 `/mnt/` 挂载
