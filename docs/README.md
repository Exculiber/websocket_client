# WebSocket 探测工具

一个功能强大的 Python WebSocket 探测和测试工具，支持多种探测模式和详细的统计信息。

## 功能特性

- 🔍 **基础探测**: 单次连接测试和消息发送
- 🔄 **连续探测**: 定时重复连接测试
- 🚀 **压力测试**: 并发连接压力测试
- 📊 **详细统计**: 响应时间、成功率等统计信息
- 🔐 **安全支持**: 支持 WSS 安全连接
- 🏷️ **自定义头部**: 支持认证和自定义 HTTP 头部
- ⏱️ **超时控制**: 可配置的连接和响应超时
- 🏓 **Ping/Pong 测试**: WebSocket 心跳测试

## 安装依赖

```bash
cd python
pip install -r requirements.txt
```

## 🚀 二进制打包（免 Python 环境运行）

如果您希望分发独立的可执行文件，无需用户安装 Python 环境：

### 快速构建
```bash
# Linux/macOS
./build.sh

# Windows
build.bat

# 或手动构建
python build_binary.py
```

### 构建要求
- Python 3.6+ (推荐 Python 3.7+)
- PyInstaller (`pip install pyinstaller`)
- 所有项目依赖

**注意**: 对于 Python 3.6 环境，会自动使用兼容版本脚本

### 构建输出
构建完成后会生成：
- `release-{platform}-{arch}/` - 发布包目录
- `websocket-probe-{platform}-{arch}.zip` - 压缩包

### 跨平台支持
- **Windows**: `websocket-probe-windows-amd64.exe`
- **macOS**: `websocket-probe-macos-arm64` (Apple Silicon) / `websocket-probe-macos-x86_64` (Intel)
- **Linux**: `websocket-probe-linux-x86_64`

详细构建指南请参考 [BUILD_GUIDE.md](BUILD_GUIDE.md)

### Python 3.6 兼容性
如果您使用的是 Python 3.6 环境（如 CentOS 7），请参考 [PYTHON36_FIX.md](PYTHON36_FIX.md) 了解兼容性修复详情。

或手动安装主要依赖：

```bash
pip install websockets
```

## 使用方法

### 基本用法

```bash
# 基础探测
python python/websocket_probe.py ws://localhost:8080/ws

# 使用自定义消息
python python/websocket_probe.py ws://localhost:8080/ws --message "Hello WebSocket!"

# 连接到安全的 WebSocket (WSS)
python python/websocket_probe.py wss://echo.websocket.org/
```

### 探测模式

#### 1. 基础探测模式 (默认)
单次连接，发送一条消息并测量响应时间：

```bash
python python/websocket_probe.py ws://localhost:8080/ws --mode basic
```

#### 2. 连续探测模式
定时重复探测，适合监控 WebSocket 服务：

```bash
# 每5秒探测一次
python python/websocket_probe.py ws://localhost:8080/ws --mode continuous --interval 5

# 每10秒探测一次，发送自定义消息
python python/websocket_probe.py ws://localhost:8080/ws --mode continuous --interval 10 --message "ping"
```

#### 3. 压力测试模式
并发连接测试，评估服务器性能：

```bash
# 10次连接，并发数3
python python/websocket_probe.py ws://localhost:8080/ws --mode stress --count 10 --concurrency 3

# 100次连接，并发数10
python python/websocket_probe.py ws://localhost:8080/ws --mode stress --count 100 --concurrency 10
```

### 高级选项

#### 自定义 HTTP 头部
支持认证和其他自定义头部：

```bash
# 使用 Bearer Token 认证
python websocket_probe.py wss://api.example.com/ws \
    --headers '{"Authorization": "Bearer your-token-here"}'

# 多个头部
python websocket_probe.py wss://api.example.com/ws \
    --headers '{"Authorization": "Bearer token", "X-API-Key": "key123"}'
```

#### 跳过 SSL 证书验证
用于测试环境的自签名证书或开发环境：

```bash
# 跳过 SSL 证书验证（仅用于测试环境）
python websocket_probe.py wss://192.168.1.100:8080/ws --skip-ssl-verify

# 组合使用认证和跳过证书验证
python websocket_probe.py wss://test-server.local/ws \
    --headers '{"Authorization": "Bearer test-token"}' \
    --skip-ssl-verify
```

**⚠️ 安全警告**: `--skip-ssl-verify` 选项会禁用 SSL 证书验证，仅应在测试环境中使用，生产环境使用存在安全风险。

#### 超时设置
自定义连接和响应超时时间：

```bash
# 设置30秒超时
python websocket_probe.py ws://localhost:8080/ws --timeout 30
```

### 实用示例

#### 测试本地开发服务器
```bash
python websocket_probe.py ws://localhost:3000/ws --message "test"
```

#### 监控生产环境 WebSocket 服务
```bash
python websocket_probe.py wss://your-app.com/ws \
    --mode continuous \
    --interval 30 \
    --headers '{"Authorization": "Bearer production-token"}'
```

#### 进行负载测试
```bash
python websocket_probe.py ws://localhost:8080/ws \
    --mode stress \
    --count 50 \
    --concurrency 10 \
    --message '{"type": "test", "data": "load test"}'
```

#### 测试公共 WebSocket 服务
```bash
# 测试 WebSocket Echo 服务
python websocket_probe.py wss://echo.websocket.org/ --message "Hello Echo!"

# 测试 WebSocket King 服务
python websocket_probe.py wss://websocket.king --message "ping"
```

## 输出解释

### 连接状态
- ✅ **连接成功**: WebSocket 连接建立成功
- ❌ **连接失败**: 连接超时、拒绝或其他错误
- 🏓 **Ping 成功**: WebSocket 心跳测试成功
- 📤 **发送消息**: 消息发送成功
- 📥 **收到响应**: 收到服务器响应

### 统计信息
脚本会在结束时显示详细的统计信息：

```
📊 WebSocket 探测统计
==================================================
连接尝试次数: 10
成功连接次数: 9
失败连接次数: 1
发送消息数量: 9
接收消息数量: 9
平均响应时间: 45.67ms
最小响应时间: 23.45ms
最大响应时间: 89.12ms
连接成功率: 90.0%
==================================================
```

## 常见用例

### 1. 开发阶段测试
在开发 WebSocket 应用时，快速验证服务器是否正常工作：

```bash
python websocket_probe.py ws://localhost:8080/ws
```

### 2. 部署后验证
部署后验证 WebSocket 服务是否可达：

```bash
python websocket_probe.py wss://your-domain.com/ws \
    --headers '{"Authorization": "Bearer test-token"}'
```

### 3. 性能监控
定期监控 WebSocket 服务的响应时间和可用性：

```bash
python websocket_probe.py wss://your-domain.com/ws \
    --mode continuous \
    --interval 60
```

### 4. 负载测试
测试 WebSocket 服务在高并发下的表现：

```bash
python websocket_probe.py ws://your-server/ws \
    --mode stress \
    --count 100 \
    --concurrency 20
```

## 故障排除

### 常见错误

1. **连接超时**
   - 检查 WebSocket 服务器是否正在运行
   - 验证 URL 是否正确
   - 检查防火墙设置

2. **认证失败**
   - 验证 Authorization 头部格式
   - 检查 token 是否有效
   - 确认服务器的认证机制

3. **SSL/TLS 错误**
   - 对于测试环境，可能需要跳过证书验证
   - 检查证书是否有效

### 调试技巧

1. **启用详细日志**：脚本默认显示详细的连接和消息日志

2. **测试公共服务**：使用 `wss://echo.websocket.org` 验证工具本身是否正常工作

3. **逐步测试**：先用基础模式测试单次连接，再使用连续或压力测试模式

## 配置文件

参考 `config_example.json` 文件查看各种配置示例，包括：
- 不同类型的 WebSocket 服务器配置
- 认证头部示例
- 测试服务器列表

## 注意事项

- 使用压力测试模式时，注意不要对生产环境造成过大负载
- 连续探测模式会持续运行，使用 Ctrl+C 停止
- WSS 连接需要有效的 SSL 证书，测试环境可能需要特殊配置
- 某些 WebSocket 服务器可能有连接频率限制

## 许可证

本工具仅供学习和测试使用，请遵守目标服务器的使用条款。
