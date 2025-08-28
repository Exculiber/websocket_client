# WebSocket 探测工具二进制构建指南

本指南将帮助您将 WebSocket 探测工具打包为独立的二进制文件，支持 Windows、macOS 和 Linux 平台。

## 🎯 目标

- 🚀 **零依赖运行**: 用户无需安装 Python 或任何依赖包
- 🌍 **跨平台支持**: Windows、macOS、Linux 三大平台
- 📦 **单文件分发**: 生成单个可执行文件，便于分发
- ⚡ **性能优化**: 启动快速，体积合理

## 📋 前置要求

### 通用要求
- Python 3.7+ 
- pip 包管理器
- 足够的磁盘空间（至少 500MB 用于构建过程）

### 平台特定要求

#### Windows
- Windows 7+ 或 Windows Server 2008+
- Visual C++ Redistributable（通常已安装）

#### macOS  
- macOS 10.13+ (High Sierra)
- Xcode Command Line Tools（可选，用于某些包的编译）

#### Linux
- glibc 2.17+ (大多数现代发行版都满足)
- gcc 编译器（用于某些包的编译）

## 🚀 快速开始

### 方法一：使用自动化脚本

#### Windows
```cmd
# 双击运行或在命令行中执行
build.bat
```

#### Linux/macOS
```bash
# 普通构建
./build.sh

# 使用虚拟环境构建（推荐）
./build.sh --venv
```

### 方法二：手动构建

#### 1. 安装构建依赖
```bash
pip install -r requirements-build.txt
```

#### 2. 运行构建脚本
```bash
python build_binary.py
```

## 📁 构建输出

构建成功后，您将获得：

```
release-{platform}-{arch}/
├── websocket-probe-{platform}-{arch}(.exe)  # 主可执行文件
├── README.md                                 # 项目说明
├── config_example.json                       # 配置示例
└── USAGE.txt                                # 快速使用指南
```

### 文件大小参考
- **Windows**: 约 15-20 MB
- **macOS**: 约 12-18 MB  
- **Linux**: 约 10-15 MB

## 🔧 高级配置

### 自定义构建选项

编辑 `build_binary.py` 中的 `create_spec_file()` 函数可以调整：

#### 排除不需要的模块
```python
excludes=[
    'tkinter',      # GUI 库
    'matplotlib',   # 图表库
    'numpy',        # 数值计算
    'pandas',       # 数据分析
    # 添加其他不需要的模块
]
```

#### 包含额外的数据文件
```python
datas=[
    ('config_example.json', '.'),
    ('templates/', 'templates'),  # 包含整个目录
    # 添加其他需要的文件
]
```

#### 启用 UPX 压缩
```python
exe = EXE(
    # ... 其他参数
    upx=True,           # 启用 UPX 压缩
    upx_exclude=[],     # UPX 排除列表
    # ...
)
```

> **注意**: UPX 压缩可以显著减小文件大小，但可能会增加启动时间和触发某些杀毒软件警报。

## 🧪 测试构建结果

### 基础测试
```bash
# 测试帮助信息
./websocket-probe-{platform}-{arch} --help

# 测试基本连接
./websocket-probe-{platform}-{arch} wss://echo.websocket.org

# 测试交互模式
./websocket-probe-{platform}-{arch} wss://echo.websocket.org --mode interactive
```

### 兼容性测试

建议在以下环境中测试：

#### Windows
- Windows 10/11 (主要)
- Windows 7 SP1 (如需支持)
- Windows Server 2016/2019/2022

#### macOS
- 最新版本 macOS
- 较老版本 macOS (10.13+)
- 不同架构 (Intel x64, Apple Silicon M1/M2)

#### Linux
- Ubuntu 18.04+ LTS
- CentOS 7+/RHEL 7+
- Debian 9+
- Alpine Linux (Docker 环境)

## 📦 分发策略

### GitHub Releases
1. 为每个平台创建单独的发布包
2. 使用清晰的命名约定: `websocket-probe-v1.0.0-{platform}-{arch}.zip`
3. 提供校验和文件 (SHA256)

### 企业内部分发
1. 创建内部软件仓库
2. 提供自动更新机制
3. 包含安全扫描报告

## 🔍 故障排除

### 常见问题

#### 1. 构建失败 - 缺少依赖
```bash
# 解决方案：确保所有依赖已安装
pip install -r requirements-build.txt --upgrade
```

#### 2. 二进制文件过大
```python
# 解决方案：在 spec 文件中添加更多排除项
excludes=[
    'tkinter', 'matplotlib', 'numpy', 'pandas',
    'PIL', 'PyQt5', 'PyQt6', 'jupyter', 'IPython'
]
```

#### 3. 启动速度慢
- 启用 UPX 压缩可能会影响启动速度
- 考虑使用 `--onedir` 而不是 `--onefile` 模式

#### 4. macOS 安全警告
```bash
# 解决方案：移除隔离属性
xattr -d com.apple.quarantine websocket-probe-macos-*
```

#### 5. Linux 权限问题
```bash
# 解决方案：添加执行权限
chmod +x websocket-probe-linux-*
```

### 调试技巧

#### 启用 PyInstaller 调试
```bash
pyinstaller --debug=all websocket_probe.spec
```

#### 检查导入问题
```bash
# 运行二进制文件时添加调试输出
PYTHONPATH=. ./websocket-probe-* --help
```

## 🔒 安全考虑

### 代码签名

#### Windows
```bash
# 使用 signtool 进行代码签名
signtool sign /f certificate.pfx /p password websocket-probe-windows-amd64.exe
```

#### macOS  
```bash
# 使用 codesign 进行代码签名
codesign --sign "Developer ID Application: Your Name" websocket-probe-macos-amd64
```

### 病毒扫描
- 某些杀毒软件可能会误报 PyInstaller 生成的文件
- 建议提交到 VirusTotal 进行检测
- 考虑申请软件厂商白名单

## 📊 性能优化

### 减小文件大小
1. **排除不必要的模块**: 仔细检查 `excludes` 列表
2. **UPX 压缩**: 权衡文件大小和启动速度
3. **优化依赖**: 使用最小化的依赖集合

### 提升启动速度
1. **避免过度压缩**: UPX 压缩会增加解压时间
2. **预编译**: 考虑 PyInstaller 的预编译选项
3. **目录模式**: 使用 `--onedir` 而不是 `--onefile`

## 🔄 自动化构建

### GitHub Actions 示例
```yaml
name: Build Binaries

on: [push, release]

jobs:
  build:
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
    
    runs-on: ${{ matrix.os }}
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: pip install -r python/requirements-build.txt
    
    - name: Build binary
      run: |
        cd python
        python build_binary.py
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v4
      with:
        name: websocket-probe-${{ matrix.os }}
        path: python/release-*/
```

## 📚 相关资源

- [PyInstaller 官方文档](https://pyinstaller.readthedocs.io/)
- [UPX 压缩工具](https://upx.github.io/)
- [Python 应用打包最佳实践](https://packaging.python.org/)

## 🆘 获取帮助

如果遇到构建问题：

1. 检查本文档的故障排除章节
2. 确认 Python 和依赖版本兼容性
3. 查看 PyInstaller 官方文档
4. 搜索相关错误信息
5. 创建详细的问题报告

---

🎉 **恭喜！您现在可以创建跨平台的 WebSocket 探测工具二进制文件了！**
