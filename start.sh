#!/bin/bash

# 铜价预测系统启动脚本

cd "$(dirname "$0")"

echo "=========================================="
echo "铜价预测系统 v3 - Web服务器启动"
echo "=========================================="
echo ""

# 停止占用端口的进程
echo "检查端口 8001..."
lsof -ti:8001 | xargs kill -9 2>/dev/null
echo "端口已就绪"
echo ""

# 启动服务器
echo "正在启动服务器..."
echo "📱 本地访问: http://localhost:8001"
echo "🌐 局域网访问: http://<本机IP>:8001"
echo "📡 可以在手机浏览器中访问上述地址"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "=========================================="
echo ""

python3 app.py
