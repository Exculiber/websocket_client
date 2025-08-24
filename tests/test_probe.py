#!/usr/bin/env python3
"""
WebSocket 探测工具测试脚本
用于快速测试 websocket_probe.py 的功能
"""

import subprocess
import sys
import time

def run_test(description, command):
    """运行测试命令"""
    print(f"\n🧪 测试: {description}")
    print(f"命令: {' '.join(command)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ 测试成功")
        else:
            print("❌ 测试失败")
            print(f"错误输出: {result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏰ 测试超时")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def main():
    print("🚀 WebSocket 探测工具测试套件")
    print("=" * 50)
    
    tests = [
        {
            "description": "帮助信息显示",
            "command": [sys.executable, "websocket_probe.py", "--help"]
        },
        {
            "description": "基础探测 - Echo 服务器",
            "command": [sys.executable, "websocket_probe.py", "wss://echo.websocket.org", "--mode", "basic"]
        },
        {
            "description": "自定义消息测试",
            "command": [sys.executable, "websocket_probe.py", "wss://echo.websocket.org", "--message", "Hello Test!"]
        },
        {
            "description": "JSON 消息测试",
            "command": [sys.executable, "websocket_probe.py", "wss://echo.websocket.org", 
                       "--message", '{"type": "test", "data": "probe"}']
        }
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if run_test(test["description"], test["command"]):
            passed += 1
        time.sleep(1)  # 避免过于频繁的请求
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查输出")
        return 1

if __name__ == "__main__":
    sys.exit(main())
