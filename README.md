![](https://img.shields.io/badge/jktv视频下载脚本-red) 
![](https://img.shields.io/badge/Python-3.13-yellow) 
# jktv视频下载脚本的使用说明
视频网站：https://www.jktv.app/
播放想要下载的的视频的第一集，复制视频链接，如：https://www.jktv.app/play/269747-5-1.html
# 使用方式1
## 步骤 1: 下载脚本文件
```bash
# 方法3: 如果是在仓库中，直接 git clone
git clone https://github.com/你的用户名/你的仓库.git
cd jktvdownload
```
## 步骤 2: 创建并激活虚拟环境（推荐）
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```
## 步骤 3: 安装依赖
```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```
## 步骤 4: 确保 FFmpeg 已安装
```bash
# 检查 FFmpeg 是否已安装
ffmpeg -version

# 如果未安装，根据系统安装：
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# macOS (使用 Homebrew)
brew install ffmpeg

# Windows (使用 Chocolatey)
choco install ffmpeg

# 或者从官网下载: https://ffmpeg.org/download.html
```
## 步骤 5: 使用脚本
```bash
# 查看帮助
python video_downloader.py -h

# 基本用法（单集下载）
python video_downloader.py -u "https://www.jktv.app/play/269747-1-1.html"

# 使用自定义名称下载单集
python video_downloader.py -u "https://www.jktv.app/play/269747-1-1.html" -n "要保存的文件名称"

# 下载多集（从第1集开始下载3集）
python video_downloader.py -u "https://www.jktv.app/play/269747-1-1.html" -n "要保存的文件名称" -e 3

# 从指定集数开始下载（从第5集开始下载2集）
python video_downloader.py -u "https://www.jktv.app/play/269747-1-1.html" -n "要保存的文件名称" -s 5 -e 2

# 指定保存目录
python video_downloader.py -u "https://www.jktv.app/play/269747-1-1.html" -n "要保存的文件名称" -d "./downloads"
```
# 使用方式2
## 步骤1:
执行setup.sh对环境进行设置
```bash
chmod +x setup.sh
bash setup.sh
```
## 步骤2:
```bash
# 查看帮助
python video_downloader.py -h

# 基本用法（单集下载）
python video_downloader.py -u "https://www.jktv.app/play/269747-1-1.html"

# 使用自定义名称下载单集
python video_downloader.py -u "https://www.jktv.app/play/269747-1-1.html" -n "要保存的文件名称"

# 下载多集（从第1集开始下载3集）
python video_downloader.py -u "https://www.jktv.app/play/269747-1-1.html" -n "要保存的文件名称" -e 3

# 从指定集数开始下载（从第5集开始下载2集）
python video_downloader.py -u "https://www.jktv.app/play/269747-1-1.html" -n "要保存的文件名称" -s 5 -e 2

# 指定保存目录
python video_downloader.py -u "https://www.jktv.app/play/269747-1-1.html" -n "要保存的文件名称" -d "./downloads"
```