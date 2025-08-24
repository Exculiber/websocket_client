#!/usr/bin/env python3
"""
WebSocket 兼容性测试脚本
用于验证不同版本 websockets 库的异常处理兼容性
"""

import sys
import websockets
import traceback

def test_websocket_exceptions():
    """测试 websockets 库的异常类兼容性"""
    print("🔍 测试 WebSocket 异常类兼容性")
    print("=" * 50)
    
    # 测试异常类是否存在
    exceptions_to_test = [
        'InvalidStatus',
        'InvalidStatusCode', 
        'InvalidHandshake',
        'InvalidHandshakeError',
        'ConnectionClosed',
        'ConnectionClosedError'
    ]
    
    results = {}
    
    for exception_name in exceptions_to_test:
        try:
            exception_class = getattr(websockets.exceptions, exception_name)
            results[exception_name] = {
                'exists': True,
                'class': exception_class,
                'error': None
            }
            print(f"✅ {exception_name}: 存在")
        except AttributeError as e:
            results[exception_name] = {
                'exists': False,
                'class': None,
                'error': str(e)
            }
            print(f"❌ {exception_name}: 不存在 ({str(e)})")
    
    print("\n📊 兼容性分析:")
    print("-" * 30)
    
    # 分析结果
    if results['InvalidStatus']['exists'] or results['InvalidStatusCode']['exists']:
        print("✅ InvalidStatus 兼容性: 支持")
    else:
        print("❌ InvalidStatus 兼容性: 不支持")
    
    if results['InvalidHandshake']['exists'] or results['InvalidHandshakeError']['exists']:
        print("✅ InvalidHandshake 兼容性: 支持")
    else:
        print("❌ InvalidHandshake 兼容性: 不支持")
    
    if results['ConnectionClosed']['exists'] or results['ConnectionClosedError']['exists']:
        print("✅ ConnectionClosed 兼容性: 支持")
    else:
        print("❌ ConnectionClosed 兼容性: 不支持")
    
    return results

def test_compatibility_module():
    """测试兼容性模块"""
    print("\n🔧 测试兼容性模块")
    print("=" * 50)
    
    try:
        # 导入兼容性模块
        from websocket_probe_py36 import WebSocketExceptions, InvalidStatusException, InvalidHandshakeException, ConnectionClosedException
        
        print("✅ 兼容性模块导入成功")
        
        # 测试异常类获取
        print(f"📋 InvalidStatusException: {InvalidStatusException}")
        print(f"📋 InvalidHandshakeException: {InvalidHandshakeException}")
        print(f"📋 ConnectionClosedException: {ConnectionClosedException}")
        
        # 测试异常类是否可用
        try:
            # 创建一个测试异常实例（这可能会失败，但应该不会抛出 AttributeError）
            if InvalidStatusException != Exception:
                print("✅ InvalidStatusException 可用")
            else:
                print("⚠️ InvalidStatusException 回退到通用 Exception")
        except Exception as e:
            print(f"❌ InvalidStatusException 测试失败: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 兼容性模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 兼容性模块测试失败: {e}")
        traceback.print_exc()
        return False

def test_websockets_version():
    """测试 websockets 库版本信息"""
    print("\n📦 WebSockets 库信息")
    print("=" * 50)
    
    try:
        version = websockets.__version__
        print(f"📋 版本: {version}")
        
        # 版本兼容性建议
        if version.startswith('10.'):
            print("💡 版本 10.x: 使用旧版异常类名")
        elif version.startswith('11.'):
            print("💡 版本 11.x: 使用新版异常类名")
        else:
            print("💡 其他版本: 需要测试兼容性")
            
    except AttributeError:
        print("⚠️ 无法获取版本信息")
    
    # 显示模块路径
    print(f"📁 模块路径: {websockets.__file__}")

def main():
    """主测试函数"""
    print("🧪 WebSocket 兼容性测试")
    print("=" * 60)
    
    # 测试 websockets 库版本
    test_websockets_version()
    
    # 测试异常类兼容性
    exception_results = test_websocket_exceptions()
    
    # 测试兼容性模块
    compatibility_ok = test_compatibility_module()
    
    # 总结
    print("\n📋 测试总结")
    print("=" * 50)
    
    if compatibility_ok:
        print("✅ 兼容性模块工作正常")
        print("✅ 可以处理不同版本的 websockets 库")
    else:
        print("❌ 兼容性模块存在问题")
        print("❌ 需要检查代码修复")
    
    # 建议
    print("\n💡 建议:")
    if exception_results['InvalidStatus']['exists'] or exception_results['InvalidStatusCode']['exists']:
        print("  - InvalidStatus 异常处理: 正常")
    else:
        print("  - InvalidStatus 异常处理: 需要兼容性修复")
    
    if exception_results['InvalidHandshake']['exists'] or exception_results['InvalidHandshakeError']['exists']:
        print("  - InvalidHandshake 异常处理: 正常")
    else:
        print("  - InvalidHandshake 异常处理: 需要兼容性修复")
    
    if exception_results['ConnectionClosed']['exists'] or exception_results['ConnectionClosedError']['exists']:
        print("  - ConnectionClosed 异常处理: 正常")
    else:
        print("  - ConnectionClosed 异常处理: 需要兼容性修复")
    
    print("\n🎯 如果所有测试都通过，说明兼容性修复成功！")

if __name__ == "__main__":
    main()
