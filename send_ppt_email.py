#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
铜价预测PPT邮件发送脚本
只发送PPT报告
"""

import sys
from pathlib import Path
from datetime import datetime
import os


def find_latest_ppt_file():
    """查找最新的PPT文件"""
    # 项目目录
    base_dir = Path(__file__).parent

    # 查找今天生成的PPT文件
    today = datetime.now().strftime("%Y%m%d")

    # 查找所有pptx文件
    ppt_files = []
    for file_path in base_dir.rglob(f"*{today}*.pptx"):
        ppt_files.append(file_path)

    # 如果没有找到今天的文件，查找最近的PPT文件
    if not ppt_files:
        for file_path in base_dir.rglob("*.pptx"):
            ppt_files.append(file_path)

    # 按修改时间排序，获取最新的
    if ppt_files:
        ppt_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return str(ppt_files[0])

    return None


def send_ppt_email():
    """发送铜价预测PPT邮件"""
    try:
        # 导入邮件发送模块
        base_dir = Path(__file__).parent
        email_sender_path = base_dir / "email_sender.py"

        # 如果没有email_sender.py，则查找新闻项目的
        if not email_sender_path.exists():
            news_dir = base_dir.parent.parent / "20260301115643"
            email_sender_path = news_dir / "email_sender.py"

        if not email_sender_path.exists():
            print("邮件发送模块不存在")
            return False

        sys.path.insert(0, str(email_sender_path.parent))
        from email_sender import EmailSender, load_email_config

        # 加载邮件配置
        config = load_email_config()

        # 检查配置是否完整
        required_fields = ['smtp_server', 'smtp_port', 'sender_email', 'sender_password', 'receiver_email']
        for field in required_fields:
            if not config.get(field):
                print(f"邮件配置不完整（缺少 {field}）")
                return False

        # 查找PPT文件
        print("正在查找最新的PPT文件...")
        ppt_file = find_latest_ppt_file()

        if not ppt_file:
            print("未找到PPT文件")
            return False

        print(f"找到PPT文件: {ppt_file}")

        # 创建邮件发送器
        email_sender = EmailSender(
            smtp_server=config['smtp_server'],
            smtp_port=config['smtp_port'],
            sender_email=config['sender_email'],
            sender_password=config['sender_password']
        )

        # 构建HTML邮件内容
        today = datetime.now().strftime("%Y年%m月%d日")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    text-align: center;
                    padding: 30px 0;
                    margin-bottom: 30px;
                    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                    color: white;
                    border-radius: 10px;
                }}
                .header h1 {{
                    margin: 0 0 10px 0;
                    font-size: 2em;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }}
                .header p {{
                    margin: 5px 0 0 0;
                    opacity: 0.9;
                }}
                .info-badge {{
                    display: inline-block;
                    background: rgba(255,255,255,0.2);
                    padding: 8px 20px;
                    border-radius: 20px;
                    margin: 10px;
                    font-size: 0.9em;
                }}
                .section {{
                    margin: 30px 0;
                    padding: 25px;
                    background: #fef3c7;
                    border-radius: 10px;
                    border-left: 5px solid #f59e0b;
                }}
                .file-info {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 30px;
                    margin-top: 40px;
                    color: #718096;
                    background: #f8f9fa;
                    border-radius: 10px;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 铜价预测PPT报告</h1>
                <p>{today}</p>
                <div class="info-badge">真实数据分析</div>
                <div class="info-badge">技术+宏观+基本面</div>
                <p style="margin-top: 15px; font-size: 0.9em;">生成时间：{timestamp}</p>
            </div>

            <div class="section">
                <h2 style="color: #92400e; margin-bottom: 15px;">📎 PPT报告附件</h2>
                <div class="file-info">
                    <p><strong>文件名：</strong>{os.path.basename(ppt_file)}</strong></p>
                    <p><strong>说明：</strong>包含完整的铜价预测分析报告</p>
                    <p><strong>内容：</strong></p>
                    <ul>
                        <li>技术分析模型（XGBoost）- 短期预测</li>
                        <li>宏观因子模型（ARDL）- 中期预测</li>
                        <li>基本面模型（VAR）- 长期预测</li>
                        <li>数据可视化图表</li>
                        <li>预测结论和建议</li>
                    </ul>
                </div>
            </div>

            <div class="section">
                <h2 style="color: #92400e; margin-bottom: 15px;">📈 预测模型说明</h2>
                <p>本次预测使用真实市场数据，通过三个模型进行分析：</p>
                <ul style="margin-left: 20px; line-height: 2;">
                    <li><strong>技术分析：</strong>基于价格、成交量、技术指标进行短期预测</li>
                    <li><strong>宏观因子：</strong>考虑美元指数、通胀、PMI等宏观经济因素</li>
                    <li><strong>基本面：</strong>基于供需、库存、产能等基本面数据</li>
                </ul>
            </div>

            <div class="footer">
                <p>⚠️ 以上预测仅供参考，不构成投资建议</p>
                <p>🤖 铜价预测系统 - 技术分析 + 宏观因子 + 基本面</p>
                <p style="margin-top: 10px;">© 2026 铜价预测系统</p>
            </div>
        </body>
        </html>"""

        subject = f"📊 铜价预测PPT报告 - {today}"

        # 发送邮件（只发送PPT附件）
        success, message = email_sender.send_email(
            to_email=config['receiver_email'],
            subject=subject,
            html_content=html_content,
            attachments=[ppt_file]
        )

        if success:
            print(f"✅ PPT邮件发送成功")
            return True
        else:
            print(f"❌ PPT邮件发送失败: {message}")
            return False

    except Exception as e:
        print(f"发送邮件时出错: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("铜价预测PPT邮件发送")
    print("=" * 50)
    print()

    success = send_ppt_email()

    print()
    print("=" * 50)
    if success:
        print("邮件发送完成！")
    else:
        print("邮件发送失败！")
    print("=" * 50)
