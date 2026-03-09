#!/bin/bash
#
# 铜价风险预警系统定时运行脚本
# 每天早上9:15自动运行
#

PROJECT_DIR="/Users/ydy/CodeBuddy/20260227142050/copper_prediction_v2"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/risk_alert_$(date +%Y%m%d_%H%M%S).log"

# 创建日志目录
mkdir -p "$LOG_DIR"

echo "========================================" | tee -a "$LOG_FILE"
echo "铜价风险预警系统 - 定时任务启动" | tee -a "$LOG_FILE"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 切换到项目目录
cd "$PROJECT_DIR" || exit 1

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    echo "激活虚拟环境..." | tee -a "$LOG_FILE"
    source venv/bin/activate
fi

# 运行风险预警系统
echo "" | tee -a "$LOG_FILE"
echo "开始运行铜价风险预警系统..." | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

python3 run_risk_alerts.py 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 铜价风险预警系统运行完成！" | tee -a "$LOG_FILE"
else
    echo "⚠️ 铜价风险预警系统运行完成，退出码: $EXIT_CODE" | tee -a "$LOG_FILE"
fi
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 退出脚本
exit $EXIT_CODE
