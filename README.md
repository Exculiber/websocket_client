# WebSocket 探测工具

一套完整的 WebSocket 连接探测和监控工具，基于 Python 实现。

## 📁 目录结构

```
websocket-probe/
├── websocket_probe.py         # 🐍 主要的探测工具
├── websocket_probe_py36.py    # 🐍 Python 3.6 兼容版本
├── requirements.txt            # 📦 主要依赖包列表
├── requirements-dev.txt        # 🔧 开发依赖包列表
├── setup.py                   # ⚙️ 安装配置文件
├── tests/                     # 🧪 测试套件目录
│   ├── test_probe.py
│   └── test_compatibility.py
├── docs/                      # 📚 详细文档目录
│   ├── README.md              # 详细使用说明
│   ├── BUILD_GUIDE.md         # 构建指南
│   └── TOOL_SUMMARY.md        # 工具总结
├── scripts/                    # 🛠️ 构建脚本目录
│   ├── build_binary.py
│   ├── build.sh
│   └── build.bat
├── releases/                   # 📦 预编译二进制文件
│   └── v1.0.0/                # 版本发布目录
└── examples/                   # 📋 配置示例目录
    └── config_example.json
```

## 🚀 快速开始

### Python 版本
```bash
# 安装依赖
pip install -r requirements.txt

# 基础测试
python3 websocket_probe.py wss://echo.websocket.org/

# 压力测试
python3 websocket_probe.py wss://echo.websocket.org/ --mode stress --count 10
```

### 预编译二进制版本（推荐）
```bash
# macOS ARM64
./releases/v1.0.0/websocket-probe-macos-arm64 wss://echo.websocket.org/

# Linux x86_64
./releases/v1.0.0/websocket-probe-linux-x86_64 wss://echo.websocket.org/

# Linux aarch64
./releases/v1.0.0/websocket-probe-linux-aarch64 wss://echo.websocket.org/
```

## 🎯 功能特性

### 🐍 Python 版本
- ✅ **功能最全面** - 支持所有 WebSocket 特性
- ✅ **三种模式** - 基础探测、连续监控、压力测试
- ✅ **详细统计** - 响应时间、成功率等完整数据
- ✅ **安全支持** - WSS 连接、自定义头部认证
- ✅ **跨平台** - 兼容 Windows、macOS、Linux
- ✅ **预编译版本** - 无需 Python 环境即可运行

## 📖 详细文档

- **[详细使用说明](docs/README.md)** - Python 版本的完整使用指南
- **[工具集总结](docs/TOOL_SUMMARY.md)** - 工具的详细说明和状态

## 💡 使用建议

### 🎯 按场景选择

| 场景 | 推荐工具 | 理由 |
|------|----------|------|
| **开发调试** | `python/websocket_probe.py` | 功能最全面，详细日志 |
| **功能测试** | `python/websocket_probe.py` | 支持多种测试模式 |
| **CI/CD** | 预编译二进制版本 | 无需额外依赖 |
| **生产监控** | `python/websocket_probe.py` | 连续监控模式 |
| **故障排查** | `python/websocket_probe.py` | 详细诊断信息 |

### 🔧 依赖要求

#### Python 版本
- Python 3.7+
- websockets 包
- python-socks 包

#### 预编译版本
- 无需任何依赖，直接运行

## ⚡ 示例命令

```bash
# 测试本地开发服务器
python3 websocket_probe.py ws://localhost:8080/ws

# 测试生产环境（带认证）
python3 websocket_probe.py wss://api.example.com/ws \
    --headers '{"Authorization": "Bearer your-token"}'

# 测试环境跳过SSL证书验证
python3 websocket_probe.py wss://192.168.1.100:8080/ws --skip-ssl-verify

# 连续监控模式
python3 websocket_probe.py wss://your-api.com/ws --mode continuous --interval 30

# 压力测试
python3 websocket_probe.py wss://echo.websocket.org/ --mode stress --count 50 --concurrency 10

# 查看帮助
python3 websocket_probe.py --help
```

## 🛠️ 故障排除

常见问题请参考 [详细使用说明](docs/README.md#故障排除)

## 📝 更新日志

- **v1.0.0** - 初始版本，完整的 Python WebSocket 探测工具
- 支持多种探测模式和监控功能
- 完整的配置管理和文档系统
- 提供预编译二进制版本，无需 Python 环境

详细更新日志请查看 [CHANGELOG.md](CHANGELOG.md)

---

## 🤝 贡献

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与项目开发。

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

---

🎉 **这套工具可以满足从开发调试到生产监控的各种 WebSocket 探测需求！**