#!/bin/bash
# 铜价集成预测系统 - 快速启动脚本

echo "======================================"
echo "铜价集成预测系统"
echo "======================================"
echo ""

# 检查端口是否被占用
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  端口8001已被占用，正在停止旧服务..."
    lsof -ti:8001 | xargs kill -9
    sleep 2
fi

# 启动Flask服务器
echo "🚀 启动Web服务器..."
echo ""
echo "📱 本地访问: http://localhost:8001"
echo "🌐 集成预测: http://localhost:8001/integrated_prediction.html"
echo ""
echo "💡 提示:"
echo "   - 按 Ctrl+C 停止服务器"
echo "   - 可以在手机浏览器中访问 (需同一WiFi)"
echo ""

cd "$(dirname "$0")"
python3 app.py
