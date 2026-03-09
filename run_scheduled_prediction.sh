#!/bin/bash
#
# 铜价预测系统定时运行脚本
# 每天早上9:20自动运行
#

PROJECT_DIR="/Users/ydy/CodeBuddy/20260227142050/copper_prediction_v2"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/scheduled_run_$(date +%Y%m%d_%H%M%S).log"

# 创建日志目录
mkdir -p "$LOG_DIR"

echo "========================================" | tee -a "$LOG_FILE"
echo "铜价预测系统 - 定时任务启动" | tee -a "$LOG_FILE"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 切换到项目目录
cd "$PROJECT_DIR" || exit 1

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    echo "激活虚拟环境..." | tee -a "$LOG_FILE"
    source venv/bin/activate
fi

# 运行铜价预测（全部模型，使用真实数据）
echo "" | tee -a "$LOG_FILE"
echo "开始运行铜价预测（技术+宏观+基本面模型，真实数据）..." | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

python main.py --data-source real 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 铜价预测完成！" | tee -a "$LOG_FILE"

    # 发送PPT邮件
    echo "" | tee -a "$LOG_FILE"
    echo "正在发送PPT邮件..." | tee -a "$LOG_FILE"
    python3 send_ppt_email.py 2>&1 | tee -a "$LOG_FILE"
else
    echo "❌ 铜价预测失败，退出码: $EXIT_CODE" | tee -a "$LOG_FILE"
fi
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 退出脚本
exit $EXIT_CODE
