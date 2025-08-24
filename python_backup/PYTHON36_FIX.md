# Python 3.6 兼容性修复指南

## 🐛 问题描述

在 Linux 系统（如 CentOS 7）上使用 Python 3.6 构建 WebSocket 探测工具时，可能会遇到以下错误：

### 错误 1: `capture_output` 参数错误
```
TypeError: __init__() got an unexpected keyword argument 'capture_output'
```

### 错误 2: `asyncio.run` 方法不存在
```
module 'asyncio' has no attribute 'run'
```

### 错误 3: `additional_headers` 参数错误
```
create_connection() got an unexpected keyword argument 'additional_headers'
```

## ✅ 解决方案

### 方案一：使用自动检测脚本（推荐）

```bash
# 脚本会自动检测 Python 版本并选择合适的构建脚本
./build.sh
```

### 方案二：手动使用 Python 3.6 兼容版本

```bash
# 1. 使用 Python 3.6 兼容的构建脚本
python3 build_binary_py36.py

# 2. 直接测试 Python 3.6 兼容的探测脚本
python3 websocket_probe_py36.py wss://echo.websocket.org
```

## 🔧 修复内容

### 1. 构建脚本兼容性修复

**原始代码** (Python 3.7+):
```python
result = subprocess.run(cmd, capture_output=True, text=True)
```

**修复后** (Python 3.6 兼容):
```python
result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
```

### 2. WebSocket 探测脚本兼容性修复

**原始代码** (Python 3.7+):
```python
asyncio.run(runner.basic_probe(args.uri, args.message, headers, args.skip_ssl_verify, args.debug))
```

**修复后** (Python 3.6 兼容):
```python
loop = asyncio.get_event_loop()
loop.run_until_complete(runner.basic_probe(args.uri, args.message, headers, args.skip_ssl_verify, args.debug))
```

### 3. WebSocket 连接参数兼容性修复

**原始代码**:
```python
websockets.connect(
    self.uri,
    additional_headers=self.headers,
    ssl=ssl_context,
    ping_interval=20,
    ping_timeout=10
)
```

**修复后** (兼容不同版本的 websockets 库):
```python
try:
    # 尝试使用新版本的参数名
    websockets.connect(
        self.uri,
        additional_headers=self.headers,
        ssl=ssl_context,
        ping_interval=20,
        ping_timeout=10
    )
except TypeError as e:
    if 'additional_headers' in str(e):
        # 如果 additional_headers 不支持，尝试 extra_headers
        try:
            websockets.connect(
                self.uri,
                extra_headers=self.headers,
                ssl=ssl_context,
                ping_interval=20,
                ping_timeout=10
            )
        except TypeError:
            # 如果都不支持，则不传递头部
            websockets.connect(
                self.uri,
                ssl=ssl_context,
                ping_interval=20,
                ping_timeout=10
            )
```

### 4. 事件循环处理修复

**原始代码**:
```python
loop = asyncio.get_event_loop()
```

**修复后**:
```python
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    # 如果没有事件循环，创建一个新的
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
```

## 📋 文件说明

| 文件 | 用途 | Python 版本支持 |
|------|------|----------------|
| `build_binary.py` | 标准构建脚本 | Python 3.7+ |
| `build_binary_py36.py` | Python 3.6 兼容构建脚本 | Python 3.6+ |
| `websocket_probe.py` | 标准 WebSocket 探测脚本 | Python 3.7+ |
| `websocket_probe_py36.py` | Python 3.6 兼容 WebSocket 探测脚本 | Python 3.6+ |

## 🧪 测试验证

### 1. 构建测试
```bash
# 测试构建脚本
python3 build_binary_py36.py

# 验证生成的二进制文件
./dist/websocket-probe-linux-x86_64 --help
```

### 2. 功能测试
```bash
# 基础连接测试
./dist/websocket-probe-linux-x86_64 wss://echo.websocket.org

# SSL 跳过测试
./dist/websocket-probe-linux-x86_64 wss://192.168.20.100:10034/signal/websocket --skip-ssl-verify

# 交互式模式测试
./dist/websocket-probe-linux-x86_64 wss://echo.websocket.org --mode interactive
```

## 🎯 预期结果

修复后，您应该能够：

1. ✅ 成功构建二进制文件
2. ✅ 正常运行 WebSocket 探测功能
3. ✅ 支持所有探测模式（基础、连续、压力测试、交互式）
4. ✅ 支持 SSL 跳过验证
5. ✅ 支持调试模式

## 📊 兼容性对比

| 功能 | Python 3.6 | Python 3.7+ |
|------|------------|-------------|
| 基础探测 | ✅ | ✅ |
| 连续探测 | ✅ | ✅ |
| 压力测试 | ✅ | ✅ |
| 交互式模式 | ✅ | ✅ |
| SSL 跳过 | ✅ | ✅ |
| 调试模式 | ✅ | ✅ |
| 二进制打包 | ✅ | ✅ |

## 🚀 快速开始

如果您使用的是 CentOS 7 或其他 Python 3.6 环境：

```bash
# 1. 克隆或下载项目
cd websocket/python

# 2. 安装依赖
pip3 install -r requirements-build.txt

# 3. 构建二进制文件
python3 build_binary_py36.py

# 4. 测试功能
./dist/websocket-probe-linux-x86_64 wss://echo.websocket.org
```

## 🔍 故障排除

### 如果仍然遇到问题：

1. **检查 Python 版本**:
   ```bash
   python3 --version
   ```

2. **确认依赖安装**:
   ```bash
   pip3 list | grep -E "(websockets|aiohttp|pyinstaller)"
   ```

3. **查看详细错误**:
   ```bash
   python3 websocket_probe_py36.py wss://echo.websocket.org --debug
   ```

4. **检查系统依赖**:
   ```bash
   # CentOS/RHEL
   sudo yum install python3-devel gcc
   
   # Ubuntu/Debian
   sudo apt-get install python3-dev build-essential
   ```

---

🎉 **现在您可以在 Python 3.6 环境下成功构建和使用 WebSocket 探测工具了！**
