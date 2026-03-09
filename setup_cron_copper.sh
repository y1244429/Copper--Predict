#!/bin/bash
#
# 配置铜价预测系统定时任务
# 每天早上9:20自动运行
#

PROJECT_DIR="/Users/ydy/CodeBuddy/20260227142050/copper_prediction_v2"
CRON_ENTRY="20 9 * * * cd $PROJECT_DIR && $PROJECT_DIR/run_scheduled_prediction.sh >> $PROJECT_DIR/logs/cron.log 2>&1"

echo "========================================"
echo "铜价预测系统 - 定时任务配置"
echo "========================================"
echo ""
echo "配置详情："
echo "  - 运行时间: 每天 09:20"
echo "  - 项目目录: $PROJECT_DIR"
echo "  - 脚本文件: run_scheduled_prediction.sh"
echo "  - 日志目录: $PROJECT_DIR/logs"
echo ""

# 创建日志目录
mkdir -p "$PROJECT_DIR/logs"

# 检查是否已经存在相同的定时任务
if crontab -l 2>/dev/null | grep -q "run_scheduled_prediction.sh"; then
    echo "⚠️  检测到已存在的定时任务"
    echo ""
    echo "当前定时任务:"
    crontab -l 2>/dev/null | grep "run_scheduled_prediction.sh"
    echo ""
    read -p "是否删除旧任务并重新配置? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 删除旧任务
        crontab -l 2>/dev/null | grep -v "run_scheduled_prediction.sh" | crontab -
        echo "✅ 旧任务已删除"
    else
        echo "❌ 配置取消"
        exit 0
    fi
fi

# 添加新的定时任务
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo ""
echo "✅ 定时任务配置成功！"
echo ""
echo "定时任务内容:"
crontab -l 2>/dev/null | grep "run_scheduled_prediction.sh"
echo ""
echo "========================================"
echo "📅 下次运行: $(date -v +1d '+%Y-%m-%d 09:20:00')"
echo ""
echo "查看日志:"
echo "  tail -f $PROJECT_DIR/logs/scheduled_run_*.log"
echo ""
echo "查看定时任务:"
echo "  crontab -l"
echo ""
echo "删除定时任务:"
echo "  crontab -e (删除相关行后保存)"
echo "========================================"
