#!/usr/bin/env python3
"""
WebSocket 探测工具
用于测试和探测 WebSocket 服务器的连接状态、响应时间和功能
"""

import asyncio
import websockets
import json
import time
import argparse
import logging
import ssl
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
import signal
import sys
import aiohttp

# 兼容性异常处理
class WebSocketExceptions:
    """兼容不同版本 websockets 库的异常类"""
    
    @staticmethod
    def get_invalid_status_exception():
        """获取 InvalidStatus 异常类"""
        try:
            return websockets.exceptions.InvalidStatus
        except AttributeError:
            try:
                return websockets.exceptions.InvalidStatusCode
            except AttributeError:
                return Exception
    
    @staticmethod
    def get_invalid_handshake_exception():
        """获取 InvalidHandshake 异常类"""
        try:
            return websockets.exceptions.InvalidHandshake
        except AttributeError:
            try:
                return websockets.exceptions.InvalidHandshakeError
            except AttributeError:
                return Exception
    
    @staticmethod
    def get_connection_closed_exception():
        """获取 ConnectionClosed 异常类"""
        try:
            return websockets.exceptions.ConnectionClosed
        except AttributeError:
            try:
                return websockets.exceptions.ConnectionClosedError
            except AttributeError:
                return Exception

# 创建兼容性异常类
InvalidStatusException = WebSocketExceptions.get_invalid_status_exception()
InvalidHandshakeException = WebSocketExceptions.get_invalid_handshake_exception()
ConnectionClosedException = WebSocketExceptions.get_connection_closed_exception()

class WebSocketProbe:
    def __init__(self, uri: str, timeout: int = 5, headers: Optional[Dict[str, str]] = None, 
                 skip_ssl_verify: bool = False, debug: bool = False):
        """
        初始化 WebSocket 探测器
        
        Args:
            uri: WebSocket 服务器地址 (ws:// 或 wss://)
            timeout: 连接和消息超时时间（秒）
            headers: 额外的HTTP头部
            skip_ssl_verify: 是否跳过SSL证书验证（仅用于测试环境）
            debug: 是否启用调试模式
        """
        self.uri = uri
        self.timeout = timeout
        self.headers = headers or {}
        self.skip_ssl_verify = skip_ssl_verify
        self.debug = debug
        self.connection = None
        self.stats = {
            'connection_attempts': 0,
            'successful_connections': 0,
            'failed_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'total_response_time': 0,
            'min_response_time': float('inf'),
            'max_response_time': 0
        }
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)

    async def connect(self) -> bool:
        """
        连接到 WebSocket 服务器
        
        Returns:
            bool: 连接是否成功
        """
        try:
            self.stats['connection_attempts'] += 1
            self.logger.info(f"正在连接到 {self.uri}...")
            
            if self.debug:
                self.logger.info(f"🔍 调试模式: 超时={self.timeout}秒, 头部={self.headers}")
            
            # 处理 SSL 设置
            ssl_context = None
            if self.uri.startswith('wss://'):
                ssl_context = ssl.create_default_context()
                if self.skip_ssl_verify:
                    # 跳过证书验证（仅用于测试环境）
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                    self.logger.warning("⚠️ 已禁用SSL证书验证（仅用于测试环境）")
                    
                if self.debug:
                    self.logger.info(f"🔍 SSL设置: verify={not self.skip_ssl_verify}")
            
            # 处理 websockets 库版本兼容性
            try:
                # 尝试使用新版本的参数名
                self.connection = await asyncio.wait_for(
                    websockets.connect(
                        self.uri,
                        additional_headers=self.headers,
                        ssl=ssl_context,
                        ping_interval=20,
                        ping_timeout=10
                    ),
                    timeout=self.timeout
                )
            except TypeError as e:
                if 'additional_headers' in str(e):
                    # 如果 additional_headers 不支持，尝试 extra_headers
                    try:
                        self.connection = await asyncio.wait_for(
                            websockets.connect(
                                self.uri,
                                extra_headers=self.headers,
                                ssl=ssl_context,
                                ping_interval=20,
                                ping_timeout=10
                            ),
                            timeout=self.timeout
                        )
                    except TypeError as e2:
                        if 'extra_headers' in str(e2):
                            # 如果都不支持，则不传递头部
                            self.logger.warning("⚠️ 当前 websockets 版本不支持自定义头部，将忽略头部设置")
                            self.connection = await asyncio.wait_for(
                                websockets.connect(
                                    self.uri,
                                    ssl=ssl_context,
                                    ping_interval=20,
                                    ping_timeout=10
                                ),
                                timeout=self.timeout
                            )
                        else:
                            raise e2
                else:
                    raise e
            
            self.stats['successful_connections'] += 1
            self.logger.info("✅ WebSocket 连接成功建立")
            return True
            
        except asyncio.TimeoutError:
            self.stats['failed_connections'] += 1
            self.logger.error(f"❌ 连接超时 ({self.timeout}秒)")
            return False
        except InvalidStatusException as e:
            self.stats['failed_connections'] += 1
            # 兼容不同版本的 websockets 库
            status_code = getattr(e, 'status_code', None) or getattr(e, 'response', None)
            if hasattr(status_code, 'status_code'):
                status_code = status_code.status_code
            status_code = status_code or 'Unknown'
            self.logger.error(f"❌ 连接失败，状态码: {status_code}")
            
            # 提供更详细的错误信息
            if status_code == 200:
                self.logger.error("💡 提示: 状态码200表示这是普通HTTP服务，不是WebSocket服务")
                self.logger.error("   请检查：1) URL路径是否正确 2) 服务器是否支持WebSocket协议")
            elif status_code == 404:
                self.logger.error("💡 提示: 路径不存在，请检查WebSocket端点路径")
            elif status_code == 403:
                self.logger.error("💡 提示: 访问被拒绝，可能需要认证或权限")
            elif status_code == 401:
                self.logger.error("💡 提示: 需要认证，请检查认证头部")
                
            return False
        except InvalidHandshakeException as e:
            self.stats['failed_connections'] += 1
            self.logger.error(f"❌ 握手失败: {str(e)}")
            
            # 检查是否是协议升级问题
            if "upgrade" in str(e).lower() or "websocket" in str(e).lower():
                self.logger.error("💡 提示: WebSocket协议升级失败，服务器可能不支持WebSocket")
                
            return False
        except Exception as e:
            self.stats['failed_connections'] += 1
            self.logger.error(f"❌ 连接失败: {str(e)}")
            return False

    async def send_message(self, message: str) -> Optional[float]:
        """
        发送消息并测量响应时间
        
        Args:
            message: 要发送的消息
            
        Returns:
            float: 响应时间（毫秒），如果失败返回 None
        """
        if not self.connection:
            self.logger.error("❌ 没有活跃的连接")
            return None
            
        try:
            start_time = time.time()
            
            await self.connection.send(message)
            self.stats['messages_sent'] += 1
            self.logger.info(f"📤 发送消息: {message[:100]}...")
            
            # 等待响应
            response = await asyncio.wait_for(
                self.connection.recv(),
                timeout=self.timeout
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            self.stats['messages_received'] += 1
            self.stats['total_response_time'] += response_time
            self.stats['min_response_time'] = min(self.stats['min_response_time'], response_time)
            self.stats['max_response_time'] = max(self.stats['max_response_time'], response_time)
            
            self.logger.info(f"📥 收到响应 ({response_time:.2f}ms): {response[:100]}...")
            return response_time
            
        except asyncio.TimeoutError:
            self.logger.error(f"❌ 消息响应超时 ({self.timeout}秒)")
            return None
        except ConnectionClosedException:
            self.logger.error("❌ 连接已关闭")
            return None
        except Exception as e:
            self.logger.error(f"❌ 发送消息失败: {str(e)}")
            return None

    async def ping_test(self) -> bool:
        """
        执行 WebSocket ping 测试
        
        Returns:
            bool: ping 是否成功
        """
        if not self.connection:
            self.logger.error("❌ 没有活跃的连接")
            return False
            
        try:
            start_time = time.time()
            pong_waiter = await self.connection.ping()
            await asyncio.wait_for(pong_waiter, timeout=self.timeout)
            response_time = (time.time() - start_time) * 1000
            
            self.logger.info(f"🏓 Ping 成功，响应时间: {response_time:.2f}ms")
            return True
            
        except asyncio.TimeoutError:
            self.logger.error("❌ Ping 超时")
            return False
        except Exception as e:
            self.logger.error(f"❌ Ping 失败: {str(e)}")
            return False

    async def http_probe(self) -> Dict[str, Any]:
        """
        HTTP 探测，用于诊断服务器响应
        
        Returns:
            Dict: 包含HTTP响应信息
        """
        # 将 WebSocket URL 转换为 HTTP URL
        http_url = self.uri.replace('ws://', 'http://').replace('wss://', 'https://')
        
        try:
            # 创建SSL上下文
            ssl_context = None
            if http_url.startswith('https://'):
                ssl_context = ssl.create_default_context()
                if self.skip_ssl_verify:
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context) if ssl_context else None
            
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(http_url, headers=self.headers) as response:
                    result = {
                        'status_code': response.status,
                        'headers': dict(response.headers),
                        'content_type': response.content_type,
                        'url': str(response.url)
                    }
                    
                    # 读取响应内容（限制大小）
                    try:
                        content = await response.text()
                        result['content'] = content[:500] if len(content) > 500 else content
                    except:
                        result['content'] = "无法读取响应内容"
                    
                    return result
                    
        except Exception as e:
            return {
                'error': str(e),
                'status_code': None,
                'headers': {},
                'content': None
            }

    async def close(self):
        """关闭 WebSocket 连接"""
        if self.connection:
            await self.connection.close()
            self.logger.info("🔌 连接已关闭")

    def print_stats(self):
        """打印统计信息"""
        print("\n" + "="*50)
        print("📊 WebSocket 探测统计")
        print("="*50)
        print(f"连接尝试次数: {self.stats['connection_attempts']}")
        print(f"成功连接次数: {self.stats['successful_connections']}")
        print(f"失败连接次数: {self.stats['failed_connections']}")
        print(f"发送消息数量: {self.stats['messages_sent']}")
        print(f"接收消息数量: {self.stats['messages_received']}")
        
        if self.stats['messages_received'] > 0:
            avg_response_time = self.stats['total_response_time'] / self.stats['messages_received']
            print(f"平均响应时间: {avg_response_time:.2f}ms")
            print(f"最小响应时间: {self.stats['min_response_time']:.2f}ms")
            print(f"最大响应时间: {self.stats['max_response_time']:.2f}ms")
        
        success_rate = (self.stats['successful_connections'] / self.stats['connection_attempts'] * 100 
                       if self.stats['connection_attempts'] > 0 else 0)
        print(f"连接成功率: {success_rate:.1f}%")
        print("="*50)

class WebSocketProbeRunner:
    def __init__(self):
        self.running = True
        
    def signal_handler(self, signum, frame):
        """处理中断信号"""
        print("\n\n🛑 收到中断信号，正在停止...")
        self.running = False

    async def basic_probe(self, uri: str, message: str = "ping", headers: Optional[Dict] = None,
                         skip_ssl_verify: bool = False, debug: bool = False):
        """基础探测模式"""
        probe = WebSocketProbe(uri, headers=headers, skip_ssl_verify=skip_ssl_verify, debug=debug)
        
        try:
            if await probe.connect():
                await probe.ping_test()
                await probe.send_message(message)
            else:
                # WebSocket 连接失败时，进行 HTTP 探测诊断
                if debug:
                    print("\n" + "="*50)
                    print("🔍 WebSocket 连接失败，进行 HTTP 探测诊断...")
                    print("="*50)
                    
                    try:
                        http_result = await probe.http_probe()
                        
                        print(f"HTTP 状态码: {http_result.get('status_code', 'N/A')}")
                        print(f"内容类型: {http_result.get('content_type', 'N/A')}")
                        
                        if http_result.get('error'):
                            print(f"HTTP 错误: {http_result['error']}")
                        else:
                            print("HTTP 响应头部:")
                            for key, value in http_result.get('headers', {}).items():
                                if key.lower() in ['upgrade', 'connection', 'sec-websocket-accept', 'sec-websocket-protocol']:
                                    print(f"  {key}: {value}")
                            
                            content = http_result.get('content', '')
                            if content:
                                print(f"响应内容前500字符:")
                                print(f"  {content}")
                                
                    except Exception as e:
                        print(f"HTTP 探测失败: {e}")
                        
                    print("="*50)
        finally:
            await probe.close()
            probe.print_stats()

    async def continuous_probe(self, uri: str, interval: int = 5, message: str = "ping", 
                             headers: Optional[Dict] = None, skip_ssl_verify: bool = False):
        """连续探测模式"""
        probe = WebSocketProbe(uri, headers=headers, skip_ssl_verify=skip_ssl_verify)
        
        try:
            while self.running:
                if await probe.connect():
                    await probe.ping_test()
                    await probe.send_message(message)
                    await probe.close()
                
                if self.running:
                    print(f"⏳ 等待 {interval} 秒后进行下次探测...")
                    await asyncio.sleep(interval)
                    
        except KeyboardInterrupt:
            print("\n🛑 用户中断")
        finally:
            await probe.close()
            probe.print_stats()

    async def stress_test(self, uri: str, count: int = 10, concurrency: int = 3,
                         message: str = "ping", headers: Optional[Dict] = None, 
                         skip_ssl_verify: bool = False):
        """压力测试模式"""
        print(f"🚀 开始压力测试: {count} 次连接，并发数: {concurrency}")
        
        semaphore = asyncio.Semaphore(concurrency)
        
        async def single_test():
            async with semaphore:
                probe = WebSocketProbe(uri, headers=headers, skip_ssl_verify=skip_ssl_verify)
                try:
                    if await probe.connect():
                        await probe.send_message(message)
                    return probe.stats
                finally:
                    await probe.close()
        
        # 执行并发测试
        tasks = [single_test() for _ in range(count)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 汇总统计
        total_stats = {
            'connection_attempts': 0,
            'successful_connections': 0,
            'failed_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'total_response_time': 0,
            'min_response_time': float('inf'),
            'max_response_time': 0
        }
        
        for result in results:
            if isinstance(result, dict):
                for key in total_stats:
                    if key == 'min_response_time':
                        if result[key] != float('inf'):
                            total_stats[key] = min(total_stats[key], result[key])
                    elif key == 'max_response_time':
                        total_stats[key] = max(total_stats[key], result[key])
                    else:
                        total_stats[key] += result[key]
        
        # 打印汇总统计
        print("\n" + "="*50)
        print("📊 压力测试汇总统计")
        print("="*50)
        print(f"总连接尝试次数: {total_stats['connection_attempts']}")
        print(f"总成功连接次数: {total_stats['successful_connections']}")
        print(f"总失败连接次数: {total_stats['failed_connections']}")
        print(f"总发送消息数量: {total_stats['messages_sent']}")
        print(f"总接收消息数量: {total_stats['messages_received']}")
        
        if total_stats['messages_received'] > 0:
            avg_response_time = total_stats['total_response_time'] / total_stats['messages_received']
            print(f"平均响应时间: {avg_response_time:.2f}ms")
            if total_stats['min_response_time'] != float('inf'):
                print(f"最小响应时间: {total_stats['min_response_time']:.2f}ms")
            print(f"最大响应时间: {total_stats['max_response_time']:.2f}ms")
        
        success_rate = (total_stats['successful_connections'] / total_stats['connection_attempts'] * 100 
                       if total_stats['connection_attempts'] > 0 else 0)
        print(f"总体连接成功率: {success_rate:.1f}%")
        print("="*50)

    async def interactive_mode(self, uri: str, headers: Optional[Dict] = None, 
                              skip_ssl_verify: bool = False, debug: bool = False):
        """交互式模式 - 建立持久连接并允许实时消息交互"""
        print("🎮 交互式 WebSocket 通道")
        print("=" * 50)
        print("📋 命令说明:")
        print("  输入消息并按回车发送")
        print("  输入 'quit' 或 'exit' 退出")
        print("  输入 'ping' 发送心跳测试")
        print("  输入 'stats' 查看统计信息")
        print("  输入 'help' 查看帮助")
        print("=" * 50)
        
        probe = WebSocketProbe(uri, headers=headers, skip_ssl_verify=skip_ssl_verify, debug=debug)
        
        try:
            # 建立连接
            if not await probe.connect():
                print("❌ 无法建立 WebSocket 连接，退出交互模式")
                return
            
            print("✅ WebSocket 连接已建立，开始交互模式")
            print("💡 提示：输入您的消息并按回车发送")
            print("-" * 30)
            
            # 启动消息接收任务
            receive_task = asyncio.create_task(self._message_receiver(probe))
            
            # 主交互循环
            while True:
                try:
                    # 获取用户输入
                    # Python 3.7+ 兼容性：使用 run_in_executor 替代 to_thread
                    loop = asyncio.get_event_loop()
                    user_input = await loop.run_in_executor(None, lambda: input("📤 发送: "))
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        print("👋 退出交互模式...")
                        break
                    elif user_input.lower() == 'ping':
                        success = await probe.ping_test()
                        if success:
                            print("🏓 心跳测试成功")
                        else:
                            print("❌ 心跳测试失败")
                        continue
                    elif user_input.lower() == 'stats':
                        self._print_interactive_stats(probe)
                        continue
                    elif user_input.lower() == 'help':
                        self._print_interactive_help()
                        continue
                    elif not user_input.strip():
                        continue
                    
                    # 发送用户消息
                    start_time = time.time()
                    await probe.connection.send(user_input)
                    probe.stats['messages_sent'] += 1
                    
                    print(f"📤 已发送: {user_input}")
                    
                except KeyboardInterrupt:
                    print("\n👋 收到中断信号，退出交互模式...")
                    break
                except Exception as e:
                    print(f"❌ 发送消息时出错: {e}")
                    break
            
            # 取消接收任务
            receive_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                pass
                
        finally:
            await probe.close()
            print("\n📊 最终统计信息:")
            probe.print_stats()

    async def _message_receiver(self, probe: 'WebSocketProbe'):
        """后台任务：接收 WebSocket 消息"""
        try:
            while True:
                try:
                    message = await probe.connection.recv()
                    probe.stats['messages_received'] += 1
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"\n📥 [{timestamp}] 收到: {message}")
                    print("📤 发送: ", end="", flush=True)  # 重新显示提示符
                except ConnectionClosedException:
                    print("\n🔌 WebSocket 连接已关闭")
                    break
                except Exception as e:
                    print(f"\n❌ 接收消息出错: {e}")
                    break
        except asyncio.CancelledError:
            pass

    def _print_interactive_stats(self, probe: 'WebSocketProbe'):
        """打印交互模式的实时统计信息"""
        print("\n📊 实时统计信息:")
        print(f"  发送消息数: {probe.stats['messages_sent']}")
        print(f"  接收消息数: {probe.stats['messages_received']}")
        try:
            connected = probe.connection and not probe.connection.closed
        except:
            connected = probe.connection is not None
        print(f"  连接状态: {'✅ 已连接' if connected else '❌ 已断开'}")
        
    def _print_interactive_help(self):
        """打印交互模式帮助信息"""
        print("\n📋 交互模式命令:")
        print("  直接输入文本      - 发送自定义消息")
        print("  ping             - 发送心跳测试")
        print("  stats            - 查看实时统计")
        print("  help             - 显示此帮助")
        print("  quit/exit/q      - 退出交互模式")
        print("  Ctrl+C           - 强制退出")
        print()
        
        print("💡 使用技巧:")
        print("  - 发送 JSON: {\"type\":\"message\",\"data\":\"hello\"}")
        print("  - 发送纯文本: hello world")
        print("  - 查看连接状态: stats")
        print()

def main():
    parser = argparse.ArgumentParser(description='WebSocket 探测工具')
    parser.add_argument('uri', help='WebSocket 服务器地址 (例如: ws://localhost:8080/ws)')
    parser.add_argument('-m', '--mode', choices=['basic', 'continuous', 'stress', 'interactive'], 
                       default='basic', help='探测模式 (默认: basic)')
    parser.add_argument('--message', default='ping', help='发送的测试消息 (默认: ping)')
    parser.add_argument('--interval', type=int, default=5, 
                       help='连续模式下的间隔时间秒数 (默认: 5)')
    parser.add_argument('--count', type=int, default=10, 
                       help='压力测试模式下的连接次数 (默认: 10)')
    parser.add_argument('--concurrency', type=int, default=3, 
                       help='压力测试模式下的并发数 (默认: 3)')
    parser.add_argument('--headers', help='JSON格式的HTTP头部 (例如: \'{"Authorization": "Bearer token"}\')')
    parser.add_argument('--timeout', type=int, default=5, help='超时时间秒数 (默认: 5)')
    parser.add_argument('--skip-ssl-verify', action='store_true', 
                       help='跳过SSL证书验证 (仅用于测试环境，有安全风险)')
    parser.add_argument('--debug', action='store_true', 
                       help='启用调试模式，显示详细的诊断信息')
    
    args = parser.parse_args()
    
    # 解析头部
    headers = None
    if args.headers:
        try:
            headers = json.loads(args.headers)
        except json.JSONDecodeError:
            print("❌ 错误: 无法解析headers JSON格式")
            return 1
    
    # 验证URI格式
    parsed_uri = urlparse(args.uri)
    if parsed_uri.scheme not in ['ws', 'wss']:
        print("❌ 错误: URI必须以 ws:// 或 wss:// 开头")
        return 1
    
    runner = WebSocketProbeRunner()
    
    # 设置信号处理
    signal.signal(signal.SIGINT, runner.signal_handler)
    signal.signal(signal.SIGTERM, runner.signal_handler)
    
    print(f"🔍 WebSocket 探测工具启动")
    print(f"🎯 目标地址: {args.uri}")
    print(f"🔧 模式: {args.mode}")
    print(f"💬 测试消息: {args.message}")
    if headers:
        print(f"📋 HTTP头部: {headers}")
    if args.skip_ssl_verify:
        print(f"⚠️ SSL证书验证: 已禁用（仅用于测试环境）")
    if args.debug:
        print(f"🔍 调试模式: 已启用")
    print("-" * 50)
    
    try:
        # Python 3.6 兼容性：使用 get_event_loop().run_until_complete() 替代 asyncio.run()
        loop = asyncio.get_event_loop()
        
        if args.mode == 'basic':
            loop.run_until_complete(runner.basic_probe(args.uri, args.message, headers, args.skip_ssl_verify, args.debug))
        elif args.mode == 'continuous':
            loop.run_until_complete(runner.continuous_probe(args.uri, args.interval, args.message, headers, args.skip_ssl_verify))
        elif args.mode == 'stress':
            loop.run_until_complete(runner.stress_test(args.uri, args.count, args.concurrency, args.message, headers, args.skip_ssl_verify))
        elif args.mode == 'interactive':
            loop.run_until_complete(runner.interactive_mode(args.uri, headers, args.skip_ssl_verify, args.debug))
    except KeyboardInterrupt:
        print("\n🛑 程序被用户中断")
        return 0
    except Exception as e:
        print(f"\n❌ 程序执行出错: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
