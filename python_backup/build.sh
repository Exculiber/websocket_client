#!/bin/bash
# WebSocket 探测工具 Linux/macOS 构建脚本

set -e

echo "🔧 WebSocket 探测工具二进制打包程序"
echo "================================================"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装或不在 PATH 中"
    echo "请安装 Python 3.7+ "
    exit 1
fi

echo "✅ Python 版本: $(python3 --version)"

# 检查是否在正确目录
if [ ! -f "websocket_probe.py" ]; then
    echo "❌ 请在包含 websocket_probe.py 的目录中运行此脚本"
    exit 1
fi

# 创建虚拟环境（可选）
if [ "$1" = "--venv" ]; then
    echo "🔧 创建虚拟环境..."
    python3 -m venv build_env
    source build_env/bin/activate
    echo "✅ 虚拟环境已激活"
fi

# 安装构建依赖
echo "📦 安装构建依赖..."
pip3 install -r requirements-build.txt

# 检查 Python 版本并选择合适的构建脚本
PYTHON_VERSION=$(python3 -c "import sys; print('{}.{}'.format(sys.version_info.major, sys.version_info.minor))")
echo "🐍 Python 版本: $PYTHON_VERSION"

if [[ "$PYTHON_VERSION" == "3.6" ]]; then
    echo "🔧 使用 Python 3.6 兼容版本..."
    BUILD_SCRIPT="build_binary_py36.py"
else
    echo "🔧 使用标准版本..."
    BUILD_SCRIPT="build_binary.py"
fi

# 运行打包脚本
echo "🚀 开始打包..."
python3 "$BUILD_SCRIPT"

echo "✅ 打包完成！"
echo "📦 请查看 release-* 目录"

# 如果使用了虚拟环境，退出它
if [ "$1" = "--venv" ]; then
    deactivate
    echo "🗑️ 可以删除 build_env 目录"
fi
