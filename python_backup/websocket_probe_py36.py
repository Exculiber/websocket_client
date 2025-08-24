#!/usr/bin/env python3
"""
WebSocket 探测工具 (Python 3.6 兼容版本)
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
            self.logger.info("正在连接到 {}...".format(self.uri))
            
            if self.debug:
                self.logger.info("🔍 调试模式: 超时={}秒, 头部={}".format(self.timeout, self.headers))
            
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
                    self.logger.info("🔍 SSL设置: verify={}".format(not self.skip_ssl_verify))
            
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
            self.logger.error("❌ 连接超时 ({}秒)".format(self.timeout))
            return False
        except InvalidStatusException as e:
            self.stats['failed_connections'] += 1
            # 兼容不同版本的 websockets 库
            status_code = getattr(e, 'status_code', None) or getattr(e, 'response', None)
            if hasattr(status_code, 'status_code'):
                status_code = status_code.status_code
            status_code = status_code or 'Unknown'
            self.logger.error("❌ 连接失败，状态码: {}".format(status_code))
            
            # 如果是状态码 200，可能是普通 HTTP 服务
            if status_code == 200:
                self.logger.info("💡 提示: 状态码 200 可能表示这是一个普通 HTTP 服务，而不是 WebSocket 服务")
                self.logger.info("💡 建议: 检查 URL 是否正确，或使用 --debug 模式获取更多信息")
            
            return False
        except InvalidHandshakeException as e:
            self.stats['failed_connections'] += 1
            self.logger.error("❌ 握手失败: {}".format(str(e)))
            return False
        except Exception as e:
            self.stats['failed_connections'] += 1
            self.logger.error("❌ 连接失败: {}".format(str(e)))
            return False

    async def send_message(self, message: str) -> bool:
        """
        发送消息到 WebSocket 服务器
        
        Args:
            message: 要发送的消息
            
        Returns:
            bool: 发送是否成功
        """
        if not self.connection:
            self.logger.error("❌ 未连接到 WebSocket 服务器")
            return False
            
        try:
            self.logger.info("📤 发送消息: {}...".format(message[:100]))
            start_time = time.time()
            
            await asyncio.wait_for(
                self.connection.send(message),
                timeout=self.timeout
            )
            
            # 等待响应
            try:
                response = await asyncio.wait_for(
                    self.connection.recv(),
                    timeout=self.timeout
                )
                
                response_time = (time.time() - start_time) * 1000
                self.stats['messages_sent'] += 1
                self.stats['messages_received'] += 1
                self.stats['total_response_time'] += response_time
                self.stats['min_response_time'] = min(self.stats['min_response_time'], response_time)
                self.stats['max_response_time'] = max(self.stats['max_response_time'], response_time)
                
                self.logger.info("📥 收到响应 ({:.2f}ms): {}...".format(response_time, response[:100]))
                return True
                
            except asyncio.TimeoutError:
                self.logger.error("❌ 消息响应超时 ({}秒)".format(self.timeout))
                return False
                
        except Exception as e:
            self.logger.error("❌ 发送消息失败: {}".format(str(e)))
            return False

    async def ping_test(self) -> bool:
        """
        执行 Ping 测试
        
        Returns:
            bool: Ping 是否成功
        """
        if not self.connection:
            self.logger.error("❌ 未连接到 WebSocket 服务器")
            return False
            
        try:
            start_time = time.time()
            pong_waiter = await self.connection.ping()
            await asyncio.wait_for(pong_waiter, timeout=self.timeout)
            response_time = (time.time() - start_time) * 1000
            
            self.logger.info("🏓 Ping 成功，响应时间: {:.2f}ms".format(response_time))
            return True
            
        except Exception as e:
            self.logger.error("❌ Ping 失败: {}".format(str(e)))
            return False

    async def close(self):
        """关闭 WebSocket 连接"""
        if self.connection:
            await self.connection.close()
            self.logger.info("🔌 连接已关闭")

    def print_stats(self):
        """打印统计信息"""
        print("=" * 50)
        print("📊 WebSocket 探测统计")
        print("=" * 50)
        print("连接尝试次数: {}".format(self.stats['connection_attempts']))
        print("成功连接次数: {}".format(self.stats['successful_connections']))
        print("失败连接次数: {}".format(self.stats['failed_connections']))
        print("发送消息数量: {}".format(self.stats['messages_sent']))
        print("接收消息数量: {}".format(self.stats['messages_received']))
        
        if self.stats['messages_received'] > 0:
            avg_response_time = self.stats['total_response_time'] / self.stats['messages_received']
            print("平均响应时间: {:.2f}ms".format(avg_response_time))
            print("最小响应时间: {:.2f}ms".format(self.stats['min_response_time']))
            print("最大响应时间: {:.2f}ms".format(self.stats['max_response_time']))
        
        if self.stats['connection_attempts'] > 0:
            success_rate = (self.stats['successful_connections'] / self.stats['connection_attempts']) * 100
            print("连接成功率: {:.1f}%".format(success_rate))
        print("=" * 50)

    async def http_probe(self) -> Dict[str, Any]:
        """
        HTTP 探测（用于调试模式）
        
        Returns:
            Dict: HTTP 响应信息
        """
        http_url = self.uri.replace('ws://', 'http://').replace('wss://', 'https://')
        try:
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
                    try:
                        content = await response.text()
                        result['content'] = content[:500] if len(content) > 500 else content
                    except:
                        result['content'] = "无法读取响应内容"
                    return result
        except Exception as e:
            return {'error': str(e), 'status_code': None, 'headers': {}, 'content': None}

class WebSocketProbeRunner:
    def __init__(self):
        self.running = True
        
    def signal_handler(self, signum, frame):
        """信号处理器"""
        print("\n🛑 收到中断信号，正在退出...")
        self.running = False

    async def basic_probe(self, uri: str, message: str, headers: Optional[Dict] = None, 
                         skip_ssl_verify: bool = False, debug: bool = False):
        """基础探测模式"""
        probe = WebSocketProbe(uri, headers=headers, skip_ssl_verify=skip_ssl_verify, debug=debug)
        
        if not await probe.connect():
            if debug:
                print("\n🔍 调试模式：尝试 HTTP 探测...")
                http_result = await probe.http_probe()
                
                if 'error' in http_result:
                    print("HTTP 状态码: {}".format(http_result.get('status_code', 'N/A')))
                    print("内容类型: {}".format(http_result.get('content_type', 'N/A')))
                else:
                    print("HTTP 错误: {}".format(http_result['error']))
                    
                if http_result.get('headers'):
                    print("HTTP 响应头:")
                    for key, value in http_result['headers'].items():
                        print("  {}: {}".format(key, value))
                        
                content = http_result.get('content', '')
                if content:
                    print("响应内容前500字符:")
                    print("  {}".format(content))
            return
            
        # 执行 Ping 测试
        await probe.ping_test()
        
        # 发送测试消息
        await probe.send_message(message)
        
        # 关闭连接
        await probe.close()
        
        # 打印统计信息
        probe.print_stats()

    async def continuous_probe(self, uri: str, interval: int, message: str, 
                             headers: Optional[Dict] = None, skip_ssl_verify: bool = False):
        """连续探测模式"""
        probe = WebSocketProbe(uri, headers=headers, skip_ssl_verify=skip_ssl_verify)
        
        while self.running:
            if await probe.connect():
                await probe.ping_test()
                await probe.send_message(message)
                await probe.close()
            
            if self.running:
                print("⏳ 等待 {} 秒后进行下次探测...".format(interval))
                await asyncio.sleep(interval)
        
        probe.print_stats()

    async def stress_test(self, uri: str, count: int, concurrency: int, message: str,
                         headers: Optional[Dict] = None, skip_ssl_verify: bool = False):
        """压力测试模式"""
        print("🚀 开始压力测试: {} 次连接，并发数: {}".format(count, concurrency))
        
        async def single_test():
            probe = WebSocketProbe(uri, headers=headers, skip_ssl_verify=skip_ssl_verify)
            if await probe.connect():
                await probe.ping_test()
                await probe.send_message(message)
                await probe.close()
            return probe.stats
        
        # 创建信号量限制并发数
        semaphore = asyncio.Semaphore(concurrency)
        
        async def limited_test():
            async with semaphore:
                return await single_test()
        
        # 执行并发测试
        tasks = [limited_test() for _ in range(count)]
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
                    if key in result:
                        if key in ['total_response_time', 'min_response_time', 'max_response_time']:
                            if result[key] != float('inf'):
                                if key == 'min_response_time':
                                    total_stats[key] = min(total_stats[key], result[key])
                                elif key == 'max_response_time':
                                    total_stats[key] = max(total_stats[key], result[key])
                                else:
                                    total_stats[key] += result[key]
                        else:
                            total_stats[key] += result[key]
        
        # 打印汇总统计
        print("=" * 50)
        print("📊 压力测试汇总统计")
        print("=" * 50)
        print("总连接尝试次数: {}".format(total_stats['connection_attempts']))
        print("总成功连接次数: {}".format(total_stats['successful_connections']))
        print("总失败连接次数: {}".format(total_stats['failed_connections']))
        print("总发送消息数量: {}".format(total_stats['messages_sent']))
        print("总接收消息数量: {}".format(total_stats['messages_received']))
        
        if total_stats['messages_received'] > 0:
            avg_response_time = total_stats['total_response_time'] / total_stats['messages_received']
            print("平均响应时间: {:.2f}ms".format(avg_response_time))
        
        if total_stats['min_response_time'] != float('inf'):
            print("最小响应时间: {:.2f}ms".format(total_stats['min_response_time']))
            print("最大响应时间: {:.2f}ms".format(total_stats['max_response_time']))
        
        if total_stats['connection_attempts'] > 0:
            success_rate = (total_stats['successful_connections'] / total_stats['connection_attempts']) * 100
            print("总体连接成功率: {:.1f}%".format(success_rate))
        print("=" * 50)

    async def interactive_mode(self, uri: str, headers: Optional[Dict] = None, 
                              skip_ssl_verify: bool = False, debug: bool = False):
        """交互式模式"""
        print("🎮 进入交互式模式")
        print("💡 输入消息发送到服务器，输入 'quit' 或 'exit' 退出")
        print("💡 特殊命令: ping, stats, help")
        print("-" * 50)
        
        probe = WebSocketProbe(uri, headers=headers, skip_ssl_verify=skip_ssl_verify, debug=debug)
        if not await probe.connect():
            print("❌ 无法建立 WebSocket 连接，退出交互模式")
            return
        
        # 启动消息接收任务 (Python 3.6 兼容)
        receive_task = asyncio.ensure_future(self._message_receiver(probe))
        
        try:
            while self.running:
                try:
                    # 使用 asyncio.to_thread 替代 input (Python 3.9+ 特性)
                    # 在 Python 3.6 中，我们需要使用其他方法
                    user_input = await self._get_user_input("📤 发送: ")
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        break
                    elif user_input.lower() == 'ping':
                        await probe.ping_test()
                        continue
                    elif user_input.lower() == 'stats':
                        self._print_interactive_stats(probe)
                        continue
                    elif user_input.lower() == 'help':
                        self._print_interactive_help()
                        continue
                    elif not user_input.strip():
                        continue
                    
                    await probe.connection.send(user_input)
                    probe.stats['messages_sent'] += 1
                    print("📤 已发送: {}".format(user_input))
                    
                except Exception as e:
                    print("❌ 发送消息时出错: {}".format(e))
                    
        finally:
            receive_task.cancel()
            await probe.close()
            probe.print_stats()

    async def _get_user_input(self, prompt: str) -> str:
        """获取用户输入（Python 3.6 兼容）"""
        # 在 Python 3.6 中，我们需要使用事件循环来获取用户输入
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: input(prompt))

    async def _message_receiver(self, probe: 'WebSocketProbe'):
        """消息接收器"""
        try:
            while True:
                message = await probe.connection.recv()
                probe.stats['messages_received'] += 1
                timestamp = time.strftime("%H:%M:%S")
                print("\n📥 [{}] 收到: {}".format(timestamp, message))
                print("📤 发送: ", end="", flush=True)
        except ConnectionClosedException:
            print("\n🔌 WebSocket 连接已关闭")
        except Exception as e:
            print("\n❌ 接收消息出错: {}".format(e))

    def _print_interactive_stats(self, probe: 'WebSocketProbe'):
        """打印交互模式统计信息"""
        print("\n📊 实时统计:")
        print("  发送消息数: {}".format(probe.stats['messages_sent']))
        print("  接收消息数: {}".format(probe.stats['messages_received']))
        try:
            connected = probe.connection and not probe.connection.closed
        except:
            connected = probe.connection is not None
        print("  连接状态: {}".format('✅ 已连接' if connected else '❌ 已断开'))
        
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
    
    print("🔍 WebSocket 探测工具启动")
    print("🎯 目标地址: {}".format(args.uri))
    print("🔧 模式: {}".format(args.mode))
    print("💬 测试消息: {}".format(args.message))
    if headers:
        print("📋 HTTP头部: {}".format(headers))
    if args.skip_ssl_verify:
        print("⚠️ SSL证书验证: 已禁用（仅用于测试环境）")
    if args.debug:
        print("🔍 调试模式: 已启用")
    print("-" * 50)
    
    try:
        # Python 3.6 兼容性：使用 get_event_loop().run_until_complete() 替代 asyncio.run()
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
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
        print("\n❌ 程序执行出错: {}".format(str(e)))
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
