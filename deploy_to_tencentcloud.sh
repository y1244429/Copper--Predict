#!/bin/bash
#
# 铜价预测系统 - 一键部署到腾讯云
#

set -e  # 遇到错误立即退出

echo "========================================"
echo "铜价预测系统 - 腾讯云一键部署"
echo "========================================"
echo ""

# 检查参数
if [ $# -lt 1 ]; then
    echo "❌ 错误: 缺少服务器IP地址"
    echo ""
    echo "用法:"
    echo "  $0 <服务器IP> [用户名]"
    echo ""
    echo "示例:"
    echo "  $0 123.45.67.89"
    echo "  $0 123.45.67.89 root"
    echo ""
    exit 1
fi

SERVER_IP="$1"
SERVER_USER="${2:-root}"

echo "📋 部署配置"
echo "  服务器IP: $SERVER_IP"
echo "  用户名: $SERVER_USER"
echo ""

# 询问确认
read -p "确认部署到服务器 $SERVER_IP? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 部署取消"
    exit 0
fi

echo ""
echo "⏳ 开始部署..."
echo ""

# 测试SSH连接
echo "🔍 测试SSH连接..."
if ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_IP}" "echo 'SSH连接成功'" > /dev/null 2>&1; then
    echo "❌ 错误: 无法连接到服务器 $SERVER_IP"
    echo ""
    echo "请检查:"
    echo "  1. 服务器IP是否正确"
    echo "  2. 服务器是否正在运行"
    echo "  3. SSH端口(22)是否开放"
    echo "  4. 用户名和密码是否正确"
    echo ""
    exit 1
fi
echo "✅ SSH连接测试通过"
echo ""

# 在服务器上执行部署
ssh "${SERVER_USER}@${SERVER_IP}" << 'ENDSSH'
set -e

echo "========================================"
echo "步骤1: 更新系统和安装基础工具"
echo "========================================"

apt update && apt upgrade -y

apt install -y python3 python3-pip python3-venv git curl wget vim
apt install -y nginx supervisor
apt install -y build-essential libssl-dev libffi-dev python3-dev

echo "✅ 基础工具安装完成"
echo ""

echo "========================================"
echo "步骤2: 创建项目目录"
echo "========================================"

mkdir -p /opt/copper-prediction
cd /opt/copper-prediction

mkdir -p logs outputs reports

echo "✅ 项目目录创建完成"
echo ""

echo "========================================"
echo "步骤3: 配置Python环境"
echo "========================================"

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip

pip install flask pandas numpy scikit-learn statsmodels
pip install akshare yfinance matplotlib seaborn
pip install python-pptx openpyxl
pip install gunicorn

echo "✅ Python环境配置完成"
echo ""

echo "========================================"
echo "步骤4: 配置Gunicorn"
echo "========================================"

cat > gunicorn_config.py << 'EOF'
import multiprocessing

bind = "0.0.0.0:8002"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"

proc_name = "copper-prediction"
EOF

echo "✅ Gunicorn配置完成"
echo ""

echo "========================================"
echo "步骤5: 配置Supervisor"
echo "========================================"

cat > /etc/supervisor/conf.d/copper-prediction.conf << 'EOF'
[program:copper-prediction]
command=/opt/copper-prediction/venv/bin/gunicorn -c /opt/copper-prediction/gunicorn_config.py app:app
directory=/opt/copper-prediction
user=root
autostart=true
autorestart=true
startsecs=10
startretries=3
stderr_logfile=/opt/copper-prediction/logs/supervisor_stderr.log
stdout_logfile=/opt/copper-prediction/logs/supervisor_stdout.log
environment=PATH="/opt/copper-prediction/venv/bin"
EOF

echo "✅ Supervisor配置完成"
echo ""

echo "========================================"
echo "步骤6: 配置Nginx"
echo "========================================"

cat > /etc/nginx/sites-available/copper-prediction << 'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        proxy_pass http://127.0.0.1:8002;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

ln -sf /etc/nginx/sites-available/copper-prediction /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl enable nginx
systemctl restart nginx

echo "✅ Nginx配置完成"
echo ""

echo "========================================"
echo "步骤7: 配置防火墙"
echo "========================================"

ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8002/tcp

echo "✅ 防火墙配置完成"
echo ""

echo "========================================"
echo "步骤8: 创建定时任务脚本"
echo "========================================"

cat > /opt/copper-prediction/run_scheduled_prediction.sh << 'EOF'
#!/bin/bash
PROJECT_DIR="/opt/copper-prediction"
LOG_FILE="$PROJECT_DIR/logs/scheduled_run_$(date +%Y%m%d_%H%M%S).log"

cd "$PROJECT_DIR" || exit 1

source venv/bin/activate

echo "========================================" | tee -a "$LOG_FILE"
echo "铜价预测系统 - 定时任务启动" | tee -a "$LOG_FILE"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

python main.py --demo --data-source auto 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo "" | tee -a "$LOG_FILE"
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

exit $EXIT_CODE
EOF

chmod +x /opt/copper-prediction/run_scheduled_prediction.sh

echo "✅ 定时任务脚本创建完成"
echo ""

echo "========================================"
echo "步骤9: 配置定时任务"
echo "========================================"

(crontab -l 2>/dev/null | grep -v "copper-prediction"; echo "20 9 * * * cd /opt/copper-prediction && /opt/copper-prediction/run_scheduled_prediction.sh >> /opt/copper-prediction/logs/cron.log 2>&1") | crontab -

echo "✅ 定时任务配置完成"
echo ""

echo "========================================"
echo "步骤10: 启动服务"
echo "========================================"

supervisorctl reread
supervisorctl update
supervisorctl start copper-prediction

echo "✅ 服务启动完成"
echo ""

echo "========================================"
echo "🎉 服务器环境配置完成！"
echo "========================================"
echo ""
echo "下一步："
echo "  1. 上传项目文件到服务器"
echo "  2. 安装Python依赖"
echo "  3. 启动应用"
echo ""
echo "上传命令："
echo "  scp -r copper_prediction_v2/ ${SERVER_USER}@${SERVER_IP}:/opt/copper-prediction/"
echo ""
echo "或先打包再上传："
echo "  tar -czf copper-prediction.tar.gz copper_prediction_v2/"
echo "  scp copper-prediction.tar.gz ${SERVER_USER}@${SERVER_IP}:/opt/"
echo ""
echo "在服务器上解压："
echo "  cd /opt/copper-prediction"
echo "  tar -xzf /opt/copper-prediction.tar.gz --strip-components=1"
echo ""
echo "重启应用："
echo "  supervisorctl restart copper-prediction"
echo ""
ENDSSH

echo "========================================"
echo "✅ 服务器环境部署完成！"
echo "========================================"
echo ""

# 询问是否立即上传文件
read -p "是否立即上传项目文件到服务器? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "⏳ 上传项目文件..."
    echo ""

    # 压缩项目
    LOCAL_DIR="/Users/ydy/CodeBuddy/20260227142050/copper_prediction_v2"
    TAR_FILE="copper-prediction.tar.gz"

    cd "/Users/ydy/CodeBuddy/20260227142050"
    echo "📦 压缩项目文件..."
    tar -czf "$TAR_FILE" copper_prediction_v2/ --exclude='*.pyc' --exclude='__pycache__' --exclude='*.log' --exclude='outputs/*' --exclude='reports/*'

    echo "📤 上传到服务器..."
    scp "$TAR_FILE" "${SERVER_USER}@${SERVER_IP}:/opt/"

    echo "📥 在服务器上解压..."
    ssh "${SERVER_USER}@${SERVER_IP}" << ENDSSH
cd /opt
tar -xzf /opt/copper-prediction.tar.gz --strip-components=1 -C /opt/copper-prediction/
rm -f /opt/copper-prediction.tar.gz
ENDSSH

    # 清理本地临时文件
    rm -f "$TAR_FILE"

    echo "✅ 项目文件上传完成"
    echo ""

    # 询问是否安装依赖并启动
    read -p "是否在服务器上安装依赖并启动应用? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "⏳ 安装依赖并启动应用..."
        echo ""

        ssh "${SERVER_USER}@${SERVER_IP}" << 'ENDSSH'
cd /opt/copper-prediction
source venv/bin/activate

echo "安装Python依赖..."
pip install -r requirements.txt 2>/dev/null || true

echo "启动应用..."
supervisorctl restart copper-prediction

echo ""
echo "等待应用启动..."
sleep 10

echo "检查应用状态..."
supervisorctl status copper-prediction
ENDSSH

        echo ""
        echo "✅ 应用已启动"
        echo ""
    fi
fi

echo "========================================"
echo "🎉 部署完成！"
echo "========================================"
echo ""
echo "📱 访问地址:"
echo "  http://$SERVER_IP"
echo ""
echo "🔍 查看应用状态:"
echo "  ssh ${SERVER_USER}@${SERVER_IP} 'supervisorctl status copper-prediction'"
echo ""
echo "📝 查看日志:"
echo "  ssh ${SERVER_USER}@${SERVER_IP} 'tail -f /opt/copper-prediction/logs/supervisor_stdout.log'"
echo ""
echo "📅 定时任务: 每天早上9:20"
echo ""
echo "详细文档: deploy_tencentcloud.md"
echo ""
echo "========================================"
