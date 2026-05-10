#!/bin/bash
cd "$(dirname "$0")"

# 创建 .env（如果不存在）
if [ ! -f .env ]; then
  cp .env.example .env
  echo "⚠️  请编辑 .env 文件填写 DASHSCOPE_API_KEY"
fi

# 安装依赖
echo "📦 检查依赖..."
pip3 install -r requirements.txt -q

# 安装 Playwright 浏览器（首次需要）
if [ ! -d "$HOME/.cache/ms-playwright" ]; then
  echo "🌐 安装 Playwright 浏览器..."
  python3 -m playwright install chromium
fi

echo ""
echo "🚀 启动推广自动化系统..."
echo "   访问地址: http://127.0.0.1:5000"
echo ""
python3 app.py
