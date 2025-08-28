#!/usr/bin/env python3
"""
WebSocket 探测工具二进制打包脚本
支持打包为 Windows、macOS、Linux 的独立可执行文件
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def check_dependencies():
    """检查必要的依赖"""
    print("🔍 检查打包依赖...")
    
    # 检查 PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller 已安装: {PyInstaller.__version__}")
    except ImportError:
        try:
            # 尝试通过命令行检查
            result = subprocess.run([sys.executable, '-c', 'import PyInstaller; print(PyInstaller.__version__)'], 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            if result.returncode == 0:
                print(f"✅ PyInstaller 已安装: {result.stdout.strip()}")
            else:
                print("❌ PyInstaller 未安装")
                print("安装命令: pip install pyinstaller")
                return False
        except:
            print("❌ PyInstaller 未安装")
            print("安装命令: pip install pyinstaller")
            return False
    
    # 检查项目依赖
    required_modules = ['websockets', 'aiohttp']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} 已安装")
        except ImportError:
            print(f"❌ {module} 未安装")
            return False
    
    return True

def get_platform_info():
    """获取平台信息"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "windows":
        platform_name = "windows"
        ext = ".exe"
    elif system == "darwin":
        platform_name = "macos"
        ext = ""
    elif system == "linux":
        platform_name = "linux"
        ext = ""
    else:
        platform_name = system
        ext = ""
    
    return platform_name, machine, ext

def create_spec_file():
    """创建 PyInstaller 规格文件"""
    platform_name, machine, ext = get_platform_info()
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 分析脚本和依赖
a = Analysis(
    ['websocket_probe.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('examples/config_example.json', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'websockets',
        'websockets.legacy',
        'websockets.legacy.client',
        'websockets.exceptions',
        'aiohttp',
        'aiohttp.client',
        'ssl',
        'asyncio',
        'json',
        'argparse',
        'logging',
        'time',
        'signal',
        'sys',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 打包为单个文件
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='websocket-probe-{platform_name}-{machine}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''.format(platform_name=platform_name, machine=machine)
    
    spec_file = 'websocket_probe.spec'
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"✅ 已创建规格文件: {spec_file}")
    return spec_file

def build_binary():
    """构建二进制文件"""
    print("🔨 开始构建二进制文件...")
    
    # 创建规格文件
    spec_file = create_spec_file()
    
    # 清理之前的构建
    for dir_name in ['build', 'dist', '__pycache__']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🗑️ 清理目录: {dir_name}")
    
    # 运行 PyInstaller
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        spec_file
    ]
    
    print(f"🚀 执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        print("✅ 构建成功！")
        
        # 显示构建结果
        platform_name, machine, ext = get_platform_info()
        binary_name = f'websocket-probe-{platform_name}-{machine}{ext}'
        binary_path = os.path.join('dist', binary_name)
        
        if os.path.exists(binary_path):
            size = os.path.getsize(binary_path)
            size_mb = size / (1024 * 1024)
            print(f"📦 二进制文件: {binary_path}")
            print(f"📏 文件大小: {size_mb:.1f} MB")
            
            return binary_path
        else:
            print("❌ 未找到生成的二进制文件")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"错误输出: {e.stderr}")
        return None

def test_binary(binary_path):
    """测试生成的二进制文件"""
    print(f"🧪 测试二进制文件: {binary_path}")
    
    if not os.path.exists(binary_path):
        print("❌ 二进制文件不存在")
        return False
    
    # 测试帮助命令
    try:
        # Python 3.6 兼容性：简化测试逻辑
        print("⏳ 正在测试二进制文件...")
        result = subprocess.run([binary_path, '--help'], 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                              universal_newlines=True)
        
        if result.returncode == 0 and 'WebSocket 探测工具' in result.stdout:
            print("✅ 二进制文件测试通过")
            return True
        else:
            print("❌ 二进制文件测试失败")
            print(f"返回码: {result.returncode}")
            if result.stdout:
                print(f"输出: {result.stdout[:200]}...")
            if result.stderr:
                print(f"错误: {result.stderr[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ 二进制文件测试异常: {e}")
        return False

def create_release_package():
    """创建发布包"""
    platform_name, machine, ext = get_platform_info()
    binary_name = f'websocket-probe-{platform_name}-{machine}{ext}'
    binary_path = os.path.join('dist', binary_name)
    
    if not os.path.exists(binary_path):
        print("❌ 二进制文件不存在，无法创建发布包")
        return None
    
    # 创建发布目录
    release_dir = f'release-{platform_name}-{machine}'
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    # 复制文件
    shutil.copy2(binary_path, release_dir)
    shutil.copy2('README.md', release_dir)
    shutil.copy2('examples/config_example.json', release_dir)
    
    # 创建使用说明
    usage_file = os.path.join(release_dir, 'USAGE.txt')
    with open(usage_file, 'w', encoding='utf-8') as f:
        f.write(f"""WebSocket 探测工具 - {platform_name.title()} 版本

🚀 快速开始:
  ./{binary_name} wss://echo.websocket.org

📖 查看帮助:
  ./{binary_name} --help

🎮 交互式模式:
  ./{binary_name} wss://your-server/ws --mode interactive

🔧 跳过SSL验证:
  ./{binary_name} wss://192.168.1.100/ws --skip-ssl-verify

🔍 调试模式:
  ./{binary_name} wss://your-server/ws --debug

📋 更多信息请参考 README.md 文件
""")
    
    print(f"📦 发布包已创建: {release_dir}/")
    
    # 显示文件列表
    print("📁 包含文件:")
    for file in os.listdir(release_dir):
        file_path = os.path.join(release_dir, file)
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            print(f"  {file} ({size} bytes)")
    
    return release_dir

def main():
    """主函数"""
    print("🔧 WebSocket 探测工具二进制打包程序")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists('websocket_probe.py'):
        print("❌ 请在包含 websocket_probe.py 的目录中运行此脚本")
        return 1
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败，请安装必要的依赖")
        return 1
    
    # 获取平台信息
    platform_name, machine, ext = get_platform_info()
    print(f"🖥️ 当前平台: {platform_name} ({machine})")
    
    # 构建二进制文件
    binary_path = build_binary()
    if not binary_path:
        print("❌ 构建失败")
        return 1
    
    # 测试二进制文件
    if not test_binary(binary_path):
        print("❌ 二进制文件测试失败")
        return 1
    
    # 创建发布包
    release_dir = create_release_package()
    if not release_dir:
        print("❌ 创建发布包失败")
        return 1
    
    print("\n🎉 打包完成！")
    print(f"📦 发布包位置: {release_dir}/")
    print(f"🚀 可执行文件: {os.path.join(release_dir, os.path.basename(binary_path))}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
