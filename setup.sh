#!/bin/bash
# setup.sh - 自动设置脚本

echo ">> jktv视频下载器 - 自动设置"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo ">> 请先安装 Python 3.8+"
    exit 1
fi

# 创建虚拟环境
echo ">> 创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
echo ">> 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo ">> 升级pip..."
pip install --upgrade pip

# 安装依赖
echo ">> 安装Python依赖..."
pip install playwright requests beautifulsoup4 lxml urllib3

# 安装Playwright浏览器
echo ">> 安装Playwright浏览器..."
playwright install chromium

# 检查FFmpeg
echo ">> 检查FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo ">> 请手动安装FFmpeg:"
    echo "Ubuntu/Debian: sudo apt install ffmpeg"
    echo "macOS: brew install ffmpeg"
    echo "Windows: choco install ffmpeg"
else
    echo ">> FFmpeg已安装"
fi

echo ">> 设置完成！"
echo ">> 使用方法: python video_downloader.py -h"