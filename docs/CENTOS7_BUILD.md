# CentOS 7 构建和部署指南

本指南专门针对 CentOS 7 环境下的 WebSocket 探测工具构建和部署。

## 🎯 问题修复

### 修复的问题
- ✅ **InvalidStatus 异常兼容性**: 修复了 `websockets.exceptions.InvalidStatus` 在不同版本库中的兼容性问题
- ✅ **InvalidHandshake 异常兼容性**: 修复了握手异常的处理
- ✅ **ConnectionClosed 异常兼容性**: 修复了连接关闭异常的处理

### 兼容性改进
- 🔧 添加了动态异常类检测，自动适配不同版本的 `websockets` 库
- 🔧 支持 `InvalidStatusCode`、`InvalidHandshakeError`、`ConnectionClosedError` 等新异常名
- 🔧 保持向后兼容性，支持旧版本的异常类名

## 🚀 快速构建

### 1. 环境准备
```bash
# 确保 Python 3.6+ 已安装
python3 --version

# 安装构建依赖
pip3 install -r requirements-build.txt

# 或者手动安装
pip3 install pyinstaller websockets aiohttp
```

### 2. 构建二进制文件
```bash
# 使用 Python 3.6 兼容版本构建
python3 build_binary_py36.py
```

### 3. 验证构建结果
```bash
# 检查生成的文件
ls -la release-linux-x86_64/

# 测试二进制文件
./release-linux-x86_64/websocket-probe-linux-x86_64 --help
```

## 🧪 测试验证

### 基础连接测试
```bash
# 测试本地 WebSocket 服务
./websocket-probe-linux-x86_64 ws://localhost:8080/ws

# 测试公共 WebSocket 服务
./websocket-probe-linux-x86_64 wss://echo.websocket.org --message "test"
```

### SSL 连接测试
```bash
# 测试 WSS 连接（跳过证书验证）
./websocket-probe-linux-x86_64 wss://192.168.20.100:10034/signal/ --skip-ssl-verify

# 测试带认证的 WSS 连接
./websocket-probe-linux-x86_64 wss://your-server.com/ws \
    --headers '{"Authorization": "Bearer your-token"}' \
    --skip-ssl-verify
```

### 连续监控测试
```bash
# 每30秒探测一次
./websocket-probe-linux-x86_64 wss://192.168.20.100:10034/signal/ \
    --mode continuous \
    --interval 30 \
    --skip-ssl-verify
```

## 🔧 故障排除

### 常见问题

1. **权限问题**
   ```bash
   # 给二进制文件执行权限
   chmod +x websocket-probe-linux-x86_64
   ```

2. **依赖库问题**
   ```bash
   # 检查动态库依赖
   ldd websocket-probe-linux-x86_64
   
   # 如果缺少库，可能需要安装
   yum install glibc-devel
   ```

3. **SSL 证书问题**
   ```bash
   # 对于自签名证书或测试环境，使用 --skip-ssl-verify
   ./websocket-probe-linux-x86_64 wss://your-server.com/ws --skip-ssl-verify
   ```

### 调试模式
```bash
# 启用调试模式获取详细信息
./websocket-probe-linux-x86_64 wss://192.168.20.100:10034/signal/ \
    --skip-ssl-verify \
    --debug
```

## 📦 部署建议

### 生产环境部署
1. **文件权限**: 确保二进制文件有执行权限
2. **目录结构**: 建议放在 `/usr/local/bin/` 或 `/opt/websocket-probe/`
3. **配置文件**: 将 `config_example.json` 复制到配置目录
4. **日志管理**: 考虑使用 `systemd` 服务管理

### systemd 服务配置示例
```ini
[Unit]
Description=WebSocket Probe Service
After=network.target

[Service]
Type=simple
User=websocket-probe
ExecStart=/usr/local/bin/websocket-probe-linux-x86_64 wss://your-server.com/ws --mode continuous --interval 60
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 🔄 更新流程

### 版本更新步骤
1. **备份当前版本**
   ```bash
   cp websocket-probe-linux-x86_64 websocket-probe-linux-x86_64.backup
   ```

2. **部署新版本**
   ```bash
   # 停止服务（如果使用 systemd）
   systemctl stop websocket-probe
   
   # 替换二进制文件
   cp new-version/websocket-probe-linux-x86_64 /usr/local/bin/
   chmod +x /usr/local/bin/websocket-probe-linux-x86_64
   
   # 重启服务
   systemctl start websocket-probe
   ```

3. **验证更新**
   ```bash
   # 检查版本和功能
   /usr/local/bin/websocket-probe-linux-x86_64 --help
   
   # 测试连接
   /usr/local/bin/websocket-probe-linux-x86_64 wss://your-server.com/ws --skip-ssl-verify
   ```

## 📋 检查清单

### 构建前检查
- [ ] Python 3.6+ 已安装
- [ ] PyInstaller 已安装
- [ ] 项目依赖已安装
- [ ] 有足够的磁盘空间（至少 500MB）

### 构建后检查
- [ ] 二进制文件生成成功
- [ ] 文件大小合理（约 10-15MB）
- [ ] 基础功能测试通过
- [ ] SSL 连接测试通过

### 部署后检查
- [ ] 二进制文件有执行权限
- [ ] 可以正常连接到目标服务器
- [ ] 日志输出正常
- [ ] 监控功能正常

## 🆘 技术支持

如果遇到问题，请提供以下信息：
1. CentOS 版本: `cat /etc/redhat-release`
2. Python 版本: `python3 --version`
3. 错误信息: 完整的错误日志
4. 目标服务器信息: WebSocket 服务器地址和配置
5. 网络环境: 防火墙、代理等配置

---

**注意**: 本修复版本专门解决了 CentOS 7 环境下的兼容性问题，确保在不同版本的 `websockets` 库下都能正常工作。
