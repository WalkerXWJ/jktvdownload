#!/usr/bin/env python3
"""
修复版Playwright视频下载器 - 自定义命名版本
支持通过参数指定名称，下载文件命名为: [指定名称]_第X集.mp4
"""

import asyncio
import os
import re
import logging
from urllib.parse import urlparse
import argparse
from playwright.async_api import async_playwright
import subprocess
import sys
from typing import List, Optional, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class VideoDownloader:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.m3u8_urls = []
        
    async def init_browser(self):
        """初始化浏览器"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--aggressive-cache-discard',
                '--disable-application-cache'
            ]
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # 启用请求拦截
        await self.context.route("**/*", self.handle_route)
        self.page = await self.context.new_page()
        
        logging.info("✅ Playwright浏览器启动成功")
        
    async def handle_route(self, route):
        """处理请求，捕获M3U8文件"""
        request = route.request
        url = request.url
        
        # 捕获M3U8请求
        if '.m3u8' in url:
            logging.info(f"🔗 捕获到m3u8请求: {url}")
            self.m3u8_urls.append(url)
            
        # 继续请求
        try:
            await route.continue_()
        except:
            await route.abort()
    
    def increment_episode_url(self, base_url: str, episode_num: int) -> Tuple[str, str]:
        """
        递增URL中的集数（最后一位数字）
        模式: /play/269747-1-1.html → /play/269747-1-2.html
        """
        try:
            # 使用正则表达式匹配并替换最后一位数字
            pattern = r'(\d+)-(\d+)-(\d+)(\.html)'
            match = re.search(pattern, base_url)
            
            if match:
                part1 = match.group(1)
                part2 = match.group(2)
                current_episode = int(match.group(3))
                extension = match.group(4)
                
                new_episode = episode_num
                new_filename = f"{part1}-{part2}-{new_episode}{extension}"
                new_url = re.sub(pattern, new_filename, base_url)
                episode_info = f"第{new_episode}集"
                
                logging.info(f"🔢 URL递增: {current_episode} → {new_episode}")
                return new_url, episode_info
            else:
                return self.fallback_increment_url(base_url, episode_num)
                
        except Exception as e:
            logging.error(f"❌ URL递增失败: {e}")
            return base_url, f"第{episode_num}集"
    
    def fallback_increment_url(self, base_url: str, episode_num: int) -> Tuple[str, str]:
        """备用URL递增方法"""
        try:
            parsed = urlparse(base_url)
            path_parts = parsed.path.split('/')
            filename = path_parts[-1]
            
            patterns = [
                r'(\d+)\.html$',
                r'-(\d+)\.html$',
                r'_(\d+)\.html$',
                r'\.(\d+)\.html$'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, filename)
                if match:
                    current_num = int(match.group(1))
                    new_filename = re.sub(pattern, f"{episode_num}.html", filename)
                    path_parts[-1] = new_filename
                    new_path = '/'.join(path_parts)
                    
                    new_parsed = parsed._replace(path=new_path)
                    new_url = new_parsed.geturl()
                    episode_info = f"第{episode_num}集"
                    
                    return new_url, episode_info
            
            # 如果都没有匹配，直接在文件名后添加集数
            name_without_ext = os.path.splitext(filename)[0]
            new_filename = f"{name_without_ext}_{episode_num}.html"
            path_parts[-1] = new_filename
            new_path = '/'.join(path_parts)
            
            new_parsed = parsed._replace(path=new_path)
            new_url = new_parsed.geturl()
            episode_info = f"第{episode_num}集"
            
            return new_url, episode_info
            
        except Exception as e:
            logging.error(f"❌ 备用递增失败: {e}")
            return base_url, f"第{episode_num}集"
    
    async def get_video_info(self, url: str, custom_name: str = "", episode_info: str = "") -> Tuple[str, str]:
        """
        获取视频信息
        返回: (最终文件名, 页面标题)
        """
        try:
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            await self.page.wait_for_timeout(3000)
            
            # 尝试点击播放按钮
            play_selectors = [
                '.play',
                '[class*="play"]',
                'button[class*="play"]',
                '.play-btn',
                '.video-play'
            ]
            
            for selector in play_selectors:
                try:
                    if await self.page.query_selector(selector):
                        await self.page.click(selector, timeout=5000)
                        logging.info(f"🖱️ 点击播放按钮: {selector}")
                        await self.page.wait_for_timeout(2000)
                        break
                except:
                    continue
            
            # 获取页面标题（用于日志显示）
            page_title = await self.page.title()
            logging.info(f"📝 页面标题: {page_title}")
            
            # 生成最终文件名
            if custom_name:
                # 使用自定义名称 + 集数
                safe_custom_name = re.sub(r'[<>:"/\\|?*]', '_', custom_name.strip())
                final_filename = f"{safe_custom_name}_{episode_info}"
            else:
                # 使用页面标题 + 集数
                clean_title = re.sub(r'[<>:"/\\|?*]', '_', page_title.strip())
                # 移除原标题中可能已有的集数信息
                clean_title = re.sub(r'[第集]\d+', '', clean_title)
                final_filename = f"{clean_title}_{episode_info}"
            
            return final_filename, page_title
            
        except Exception as e:
            logging.error(f"❌ 获取视频信息失败: {e}")
            # 返回默认文件名
            if custom_name:
                return f"{custom_name}_{episode_info}", "获取标题失败"
            else:
                return f"video_{episode_info}", "获取标题失败"
    
    async def wait_for_m3u8(self, timeout: int = 30000) -> Optional[str]:
        """等待M3U8地址"""
        logging.info("⏳ 等待M3U8地址...")
        
        start_time = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_time) * 1000 < timeout:
            if self.m3u8_urls:
                m3u8_url = self.m3u8_urls[-1]
                logging.info(f"✅ 使用M3U8地址: {m3u8_url}")
                return m3u8_url
            await asyncio.sleep(1)
        
        logging.warning("⚠️  M3U8等待超时")
        return None
    
    def download_video(self, m3u8_url: str, output_path: str) -> bool:
        """使用FFmpeg下载视频"""
        try:
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            
            cmd = [
                'ffmpeg',
                '-i', m3u8_url,
                '-c', 'copy',
                '-bsf:a', 'aac_adtstoasc',
                '-y',
                output_path
            ]
            
            logging.info(f"⬇️ 开始下载: {output_path}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            if result.returncode == 0:
                # 获取文件大小信息
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                    logging.info(f"✅ 下载完成: {output_path} ({file_size:.2f}MB)")
                else:
                    logging.info(f"✅ 下载完成: {output_path}")
                return True
            else:
                logging.error(f"❌ FFmpeg错误: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logging.error("❌ 下载超时")
            return False
        except Exception as e:
            logging.error(f"❌ 下载失败: {e}")
            return False
    
    async def process_video(self, base_url: str, episode_num: int, total_episodes: int, custom_name: str = "") -> bool:
        """处理单个视频"""
        logging.info(f"\n{'='*60}")
        logging.info(f"🎬 处理第 {episode_num}/{total_episodes} 集")
        if custom_name:
            logging.info(f"🏷️ 自定义名称: {custom_name}")
        
        # 生成递增后的URL
        actual_url, episode_info = self.increment_episode_url(base_url, episode_num)
        logging.info(f"🌐 基础URL: {base_url}")
        logging.info(f"🔗 实际URL: {actual_url}")
        logging.info(f"📺 集数: {episode_info}")
        logging.info(f"{'='*60}")
        
        try:
            self.m3u8_urls.clear()
            
            # 获取视频信息和最终文件名
            final_filename, page_title = await self.get_video_info(actual_url, custom_name, episode_info)
            
            # 确保文件名以.mp4结尾
            if not final_filename.endswith('.mp4'):
                final_filename += '.mp4'
            
            logging.info(f"📄 最终文件名: {final_filename}")
            logging.info(f"🔍 页面标题: {page_title}")
            
            # 获取M3U8地址
            m3u8_url = await self.wait_for_m3u8()
            if not m3u8_url:
                logging.error("❌ 未找到M3U8地址")
                return False
            
            # 下载视频
            return self.download_video(m3u8_url, final_filename)
            
        except Exception as e:
            logging.error(f"❌ 处理失败: {e}")
            return False
    
    async def close(self):
        """关闭浏览器"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logging.info("🔚 浏览器已关闭")

async def main():
    parser = argparse.ArgumentParser(description='视频下载器 - 自定义命名版')
    parser.add_argument('-u', '--url', required=True, help='基础URL（如: https://www.jktv.app/play/269747-1-1.html）')
    parser.add_argument('-n', '--name', type=str, default="", help='自定义文件名称（如: 我在天庭收废品）')
    parser.add_argument('-e', '--episodes', type=int, default=1, help='下载集数数量（默认: 1）')
    parser.add_argument('-s', '--start', type=int, default=1, help='起始集数（默认: 1）')
    parser.add_argument('-d', '--directory', type=str, default="", help='保存目录（可选）')
    
    args = parser.parse_args()
    
    if not args.url.startswith(('http://', 'https://')):
        logging.error("❌ 请输入有效的URL")
        return
    
    # 从URL中检测起始集数
    match = re.search(r'(\d+)-(\d+)-(\d+)(\.html)', args.url)
    if match:
        detected_start = int(match.group(3))
        if args.start == 1:  # 如果用户没有指定起始集数，使用URL中的集数
            args.start = detected_start
        logging.info(f"🔍 检测到URL中的集数: {detected_start}")
    
    # 处理保存目录
    if args.directory:
        if not os.path.exists(args.directory):
            os.makedirs(args.directory, exist_ok=True)
            logging.info(f"📁 创建目录: {args.directory}")
        os.chdir(args.directory)
    
    logging.info(f"🚀 启动自定义命名下载器...")
    logging.info(f"🌐 基础URL: {args.url}")
    if args.name:
        logging.info(f"🏷️ 自定义名称: {args.name}")
    logging.info(f"▶️ 起始集数: {args.start}")
    logging.info(f"🔢 下载数量: {args.episodes}集")
    logging.info(f"⏹️ 结束集数: {args.start + args.episodes - 1}")
    if args.directory:
        logging.info(f"📁 保存目录: {os.path.abspath(args.directory)}")
    
    downloader = VideoDownloader()
    
    try:
        await downloader.init_browser()
        
        for i in range(args.episodes):
            current_episode = args.start + i
            logging.info(f"\n📺 下载进度: {i+1}/{args.episodes} (第{current_episode}集)")
            
            success = await downloader.process_video(args.url, current_episode, args.episodes, args.name)
            
            if success:
                logging.info(f"✅ 第 {current_episode} 集下载成功")
            else:
                logging.warning(f"⚠️ 第 {current_episode} 集下载失败")
            
            # 间隔
            if i < args.episodes - 1:
                await asyncio.sleep(3)
                
    except KeyboardInterrupt:
        logging.info("⏹️ 用户中断下载")
    except Exception as e:
        logging.error(f"❌ 程序错误: {e}")
    finally:
        await downloader.close()

if __name__ == "__main__":
    # 检查FFmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except:
        print("❌ 错误: 请先安装FFmpeg")
        print("安装方法: brew install ffmpeg")
        sys.exit(1)
    
    asyncio.run(main())