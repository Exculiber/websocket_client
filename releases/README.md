# 预编译二进制文件

本目录包含预编译的二进制文件，无需Python环境即可运行。

## 📦 可用版本

### macOS
- `websocket-probe-macos-arm64` - macOS ARM64 (Apple Silicon)

### Linux
- `websocket-probe-linux-x86_64` - Linux x86_64
- `websocket-probe-linux-aarch64` - Linux ARM64

### Windows
- `websocket-probe-windows-amd64.exe` - Windows AMD64

## 🚀 使用方法

### 1. 下载对应平台的二进制文件
### 2. 设置执行权限（Linux/macOS）
```bash
chmod +x websocket-probe-macos-arm64
```

### 3. 运行工具
```bash
# macOS/Linux
./websocket-probe-macos-arm64 wss://echo.websocket.org/

# Windows
websocket-probe-windows-amd64.exe wss://echo.websocket.org/
```

## 🔧 功能特性

预编译版本包含与Python版本完全相同的功能：
- ✅ 基础探测模式
- ✅ 连续监控模式  
- ✅ 压力测试模式
- ✅ WSS安全连接支持
- ✅ 自定义头部认证
- ✅ 详细的统计信息

## 📋 系统要求

- **macOS**: 10.15+ (Catalina)
- **Linux**: Ubuntu 18.04+, CentOS 7+, 其他主流发行版
- **Windows**: Windows 10+ (64位)

## 🆚 与Python版本对比

| 特性 | Python版本 | 预编译版本 |
|------|------------|------------|
| 功能完整性 | ✅ 100% | ✅ 100% |
| 运行速度 | 标准 | ⚡ 更快 |
| 依赖管理 | 需要pip | 🚫 无需依赖 |
| 源代码访问 | ✅ 可修改 | ❌ 不可修改 |
| 部署便利性 | 需要环境 | 🎯 即开即用 |

## 📝 注意事项

1. 预编译版本功能与Python版本完全一致
2. 无需安装Python或任何依赖包
3. 适合CI/CD和自动化部署
4. 建议在生产环境使用预编译版本

---

更多详细信息请查看 [主项目README](../../README.md) 和 [详细文档](../docs/README.md)
