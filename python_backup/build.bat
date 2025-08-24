@echo off
REM WebSocket 探测工具 Windows 构建脚本

echo 🔧 WebSocket 探测工具二进制打包程序 (Windows)
echo ================================================

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装或不在 PATH 中
    echo 请安装 Python 3.7+ 并添加到 PATH
    pause
    exit /b 1
)

REM 安装构建依赖
echo 📦 安装构建依赖...
pip install -r requirements-build.txt

REM 检查 Python 版本并选择合适的构建脚本
for /f "tokens=*" %%i in ('python -c "import sys; print('{}.{}'.format(sys.version_info.major, sys.version_info.minor))"') do set PYTHON_VERSION=%%i
echo 🐍 Python 版本: %PYTHON_VERSION%

if "%PYTHON_VERSION%"=="3.6" (
    echo 🔧 使用 Python 3.6 兼容版本...
    set BUILD_SCRIPT=build_binary_py36.py
) else (
    echo 🔧 使用标准版本...
    set BUILD_SCRIPT=build_binary.py
)

REM 运行打包脚本
echo 🚀 开始打包...
python %BUILD_SCRIPT%

if errorlevel 1 (
    echo ❌ 打包失败
    pause
    exit /b 1
)

echo ✅ 打包完成！
echo 📦 请查看 release-windows-* 目录
pause
