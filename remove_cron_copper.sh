#!/bin/bash
#
# 删除铜价预测系统定时任务
#

echo "========================================"
echo "铜价预测系统 - 删除定时任务"
echo "========================================"
echo ""

# 检查是否存在定时任务
if crontab -l 2>/dev/null | grep -q "run_scheduled_prediction.sh"; then
    echo "检测到以下铜价预测定时任务:"
    echo ""
    crontab -l 2>/dev/null | grep "run_scheduled_prediction.sh"
    echo ""
    read -p "确定要删除此定时任务吗? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 删除任务
        crontab -l 2>/dev/null | grep -v "run_scheduled_prediction.sh" | crontab -
        echo ""
        echo "✅ 定时任务已删除！"
        echo ""
        echo "剩余的定时任务:"
        crontab -l 2>/dev/null || echo "无"
    else
        echo ""
        echo "❌ 操作取消"
    fi
else
    echo "⚠️  未检测到铜价预测定时任务"
fi

echo ""
echo "========================================"
