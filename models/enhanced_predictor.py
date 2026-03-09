"""
增强预测器 - 集成实时宏观、资金流向、新闻情绪
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.copper_model_v2 import CopperPriceModel
from models.advanced_models import MacroFactorModel, FundamentalModel
from data.enhanced_data_sources import EnhancedDataIntegration
from data.prediction_db import PredictionDatabase
from data.real_data import RealDataManager
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedPredictor:
    """增强预测器 - 结合传统模型和增强数据"""
    
    def __init__(self):
        # 初始化传统模型
        self.xgboost_model = CopperPriceModel(horizon_days=5)
        self.macro_model = MacroFactorModel()
        self.fund_model = FundamentalModel()
        
        # 初始化增强数据
        self.enhanced_data = EnhancedDataIntegration()
        
        # 数据库
        self.db = PredictionDatabase()
        self.data_mgr = RealDataManager()
        
        # 权重配置（可动态调整）
        self.base_weights = {
            'xgboost': 0.40,
            'macro': 0.35,
            'fundamental': 0.25
        }
    
    def get_market_state(self, enhanced_data: dict) -> str:
        """
        判断市场状态
        返回: 'normal', 'crisis', 'bull', 'bear'
        """
        risk_signals = enhanced_data.get('risk_signals', [])
        
        # 统计高风险信号
        high_risk_count = sum(1 for s in risk_signals if s.get('level') == 'high')
        
        # 判断市场状态
        if high_risk_count >= 2 or len(risk_signals) >= 4:
            return 'crisis'
        
        # 判断牛熊
        news_sentiment = enhanced_data.get('news_sentiment', {})
        if news_sentiment.get('overall_sentiment') == 'positive':
            return 'bull'
        elif news_sentiment.get('overall_sentiment') == 'negative':
            return 'bear'
        
        return 'normal'
    
    def get_dynamic_weights(self, market_state: str, enhanced_data: dict) -> dict:
        """
        根据市场状态动态调整模型权重
        """
        weights = self.base_weights.copy()
        
        if market_state == 'crisis':
            # 危机时，降低技术模型权重，提高宏观模型权重
            weights['xgboost'] = 0.20
            weights['macro'] = 0.50
            weights['fundamental'] = 0.30
            logger.info("市场状态: 危机，调整权重: 技术降权，宏观升权")
        
        elif market_state == 'bull':
            # 牛市，均衡分配，略微提高基本面
            weights['xgboost'] = 0.35
            weights['macro'] = 0.30
            weights['fundamental'] = 0.35
            logger.info("市场状态: 牛市，调整权重: 基本面升权")
        
        elif market_state == 'bear':
            # 熊市，提高宏观权重
            weights['xgboost'] = 0.30
            weights['macro'] = 0.45
            weights['fundamental'] = 0.25
            logger.info("市场状态: 熊市，调整权重: 宏观升权")
        
        # 根据新闻情绪微调
        news = enhanced_data.get('news_sentiment', {})
        if news.get('has_emergency'):
            # 有突发事件时，进一步降低技术权重
            weights['xgboost'] *= 0.5
            # 重新归一化
            total = sum(weights.values())
            weights = {k: v/total for k, v in weights.items()}
            logger.warning("检测到突发事件，大幅降低技术模型权重")
        
        return weights
    
    def apply_risk_adjustment(self, prediction: float, enhanced_data: dict) -> dict:
        """
        根据风险信号调整预测
        """
        risk_signals = enhanced_data.get('risk_signals', [])
        
        if not risk_signals:
            return {
                'adjusted_prediction': prediction,
                'adjustment_factor': 1.0,
                'confidence_level': 'high'
            }
        
        # 计算风险系数
        risk_factor = 1.0
        high_risk_count = sum(1 for s in risk_signals if s.get('level') == 'high')
        medium_risk_count = sum(1 for s in risk_signals if s.get('level') == 'medium')
        
        # 风险调整
        for signal in risk_signals:
            if signal['level'] == 'high':
                if 'VIX' in signal['indicator'] or 'Dollar' in signal['indicator']:
                    risk_factor *= 0.95  # 降低5%
                elif 'Emergency' in signal['indicator']:
                    risk_factor *= 0.90  # 降低10%
            elif signal['level'] == 'medium':
                risk_factor *= 0.97  # 降低3%
        
        # 应用调整
        adjusted_prediction = prediction * risk_factor
        
        # 确定置信度
        if high_risk_count > 0:
            confidence_level = 'low'
        elif medium_risk_count > 1:
            confidence_level = 'medium'
        else:
            confidence_level = 'high'
        
        return {
            'adjusted_prediction': adjusted_prediction,
            'adjustment_factor': risk_factor,
            'confidence_level': confidence_level,
            'risk_signals': risk_signals
        }
    
    def predict_with_enhanced_data(self, horizon: int = 5) -> dict:
        """
        使用增强数据进行预测
        """
        logger.info(f"开始增强预测 (周期: {horizon}天)...")
        
        # 1. 获取当前价格
        current_data = self.data_mgr.get_data(days=60)
        current_price = current_data.iloc[-1]['close']
        
        logger.info(f"当前价格: {current_price:,.2f}")
        
        # 2. 获取增强数据
        logger.info("获取增强数据 (宏观、资金、情绪)...")
        enhanced_data = self.enhanced_data.get_comprehensive_data()
        
        # 3. 判断市场状态
        market_state = self.get_market_state(enhanced_data)
        logger.info(f"市场状态: {market_state}")
        
        # 4. 获取动态权重
        weights = self.get_dynamic_weights(market_state, enhanced_data)
        logger.info(f"模型权重: {weights}")
        
        # 5. 各模型预测
        logger.info("各模型预测中...")
        
        # XGBoost预测
        try:
            xgboost_pred = self.xgboost_model.predict_next()
            xgboost_return = (xgboost_pred - current_price) / current_price * 100
            logger.info(f"XGBoost预测: {xgboost_pred:,.2f} ({xgboost_return:+.2f}%)")
        except Exception as e:
            logger.warning(f"XGBoost预测失败: {e}")
            xgboost_pred = current_price
            xgboost_return = 0.0
        
        # 宏观模型预测
        try:
            macro_pred = self.macro_model.predict(horizon)
            macro_return = (macro_pred - current_price) / current_price * 100
            logger.info(f"宏观模型预测: {macro_pred:,.2f} ({macro_return:+.2f}%)")
        except Exception as e:
            logger.warning(f"宏观模型预测失败: {e}")
            macro_pred = current_price
            macro_return = 0.0
        
        # 基本面模型预测
        try:
            # 基本面模型使用180天预测,不管传入的horizon是多少
            fund_horizon = 180
            fund_pred_dict = self.fund_model.predict(current_data, horizon=fund_horizon)
            fund_pred = fund_pred_dict['predicted_price']
            fund_return = fund_pred_dict['predicted_return']
            logger.info(f"基本面预测 ({fund_horizon}天): {fund_pred:,.2f} ({fund_return:+.2f}%)")
        except Exception as e:
            logger.warning(f"基本面预测失败: {e}")
            fund_pred = current_price
            fund_return = 0.0
        
        # 6. 加权融合
        weighted_return = (
            xgboost_return * weights['xgboost'] +
            macro_return * weights['macro'] +
            fund_return * weights['fundamental']
        )
        weighted_prediction = current_price * (1 + weighted_return / 100)
        
        logger.info(f"加权预测: {weighted_prediction:,.2f} ({weighted_return:+.2f}%)")
        
        # 7. 风险调整
        risk_adjusted = self.apply_risk_adjustment(weighted_prediction, enhanced_data)
        final_prediction = risk_adjusted['adjusted_prediction']
        final_return = (final_prediction - current_price) / current_price * 100
        
        logger.info(f"风险调整后: {final_prediction:,.2f} ({final_return:+.2f}%)")
        logger.info(f"调整因子: {risk_adjusted['adjustment_factor']:.4f}")
        logger.info(f"置信度: {risk_adjusted['confidence_level']}")
        
        # 8. 生成预测区间
        confidence = risk_adjusted['confidence_level']
        if confidence == 'high':
            interval_width = 0.05  # ±5%
        elif confidence == 'medium':
            interval_width = 0.08  # ±8%
        else:
            interval_width = 0.12  # ±12%
        
        lower_bound = final_prediction * (1 - interval_width)
        upper_bound = final_prediction * (1 + interval_width)
        
        # 9. 整合结果
        result = {
            'prediction_date': datetime.now(),
            'current_price': current_price,
            'horizon_days': horizon,
            'market_state': market_state,
            'weights': weights,
            'predictions': {
                'xgboost': {
                    'price': xgboost_pred,
                    'return_pct': xgboost_return,
                    'weight': weights['xgboost']
                },
                'macro': {
                    'price': macro_pred,
                    'return_pct': macro_return,
                    'weight': weights['macro']
                },
                'fundamental': {
                    'price': fund_pred,
                    'return_pct': fund_return,
                    'weight': weights['fundamental']
                }
            },
            'weighted_prediction': {
                'price': weighted_prediction,
                'return_pct': weighted_return
            },
            'final_prediction': {
                'price': final_prediction,
                'return_pct': final_return,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound
            },
            'risk_adjustment': risk_adjusted,
            'confidence_level': confidence,
            'enhanced_data': enhanced_data,
            'recommendation': self._generate_recommendation(
                final_return, confidence, market_state, risk_adjusted['risk_signals']
            )
        }
        
        # 10. 保存到数据库
        self._save_prediction(result)
        
        logger.info("增强预测完成")
        
        return result
    
    def _generate_recommendation(self, return_pct: float, confidence: str,
                                market_state: str, risk_signals: list) -> dict:
        """
        生成投资建议
        """
        # 基础建议
        if return_pct > 2:
            base_direction = 'strong_buy'
            base_advice = '强烈建议做多'
        elif return_pct > 0:
            base_direction = 'buy'
            base_advice = '建议适度做多'
        elif return_pct > -2:
            base_direction = 'hold'
            base_advice = '建议观望'
        else:
            base_direction = 'sell'
            base_advice = '建议谨慎观望或适度做空'
        
        # 根据置信度调整
        if confidence == 'low':
            base_advice += '，但需谨慎控制仓位'
        elif confidence == 'medium':
            base_advice += '，建议设置止损'
        
        # 根据市场状态调整
        if market_state == 'crisis':
            base_advice += '，当前市场波动较大'
        elif market_state == 'bear':
            base_advice += '，当前处于熊市环境'
        
        # 风险提示
        risk_warnings = []
        for signal in risk_signals:
            if signal['level'] == 'high':
                risk_warnings.append(signal['message'])
        
        return {
            'direction': base_direction,
            'advice': base_advice,
            'risk_warnings': risk_warnings,
            'position_size': self._suggest_position_size(confidence, market_state)
        }
    
    def _suggest_position_size(self, confidence: str, market_state: str) -> str:
        """
        建议仓位大小
        """
        if confidence == 'low' or market_state == 'crisis':
            return '轻仓 (10-20%)'
        elif confidence == 'medium':
            return '适中仓位 (30-50%)'
        else:
            if market_state == 'bull':
                return '重仓 (60-80%)'
            else:
                return '标准仓位 (40-60%)'
    
    def _save_prediction(self, result: dict):
        """保存预测到数据库"""
        try:
            self.db.save_enhanced_prediction(result)
            logger.info("预测已保存到数据库")
        except Exception as e:
            logger.error(f"保存预测失败: {e}")
    
    def print_prediction_summary(self, result: dict):
        """打印预测摘要"""
        print("\n" + "="*70)
        print("增强预测结果")
        print("="*70)
        
        # 基本信息
        print(f"\n【基本信息】")
        print(f"  预测时间: {result['prediction_date'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  当前价格: ¥{result['current_price']:,.2f}")
        print(f"  预测周期: {result['horizon_days']}天")
        print(f"  市场状态: {result['market_state']}")
        
        # 各模型预测
        print(f"\n【各模型预测】")
        preds = result['predictions']
        for model_name, pred_data in preds.items():
            print(f"  {model_name.upper():12s}: ¥{pred_data['price']:,.2f} ({pred_data['return_pct']:+.2f}%) [权重:{pred_data['weight']:.0%}]")
        
        # 最终预测
        print(f"\n【最终预测】")
        final = result['final_prediction']
        print(f"  预测价格: ¥{final['price']:,.2f} ({final['return_pct']:+.2f}%)")
        print(f"  预测区间: ¥{final['lower_bound']:,.2f} ~ ¥{final['upper_bound']:,.2f}")
        print(f"  置信度: {result['confidence_level']}")
        
        # 风险调整
        risk_adj = result['risk_adjustment']
        if risk_adj['adjustment_factor'] != 1.0:
            print(f"\n【风险调整】")
            print(f"  调整因子: {risk_adj['adjustment_factor']:.4f}")
            if risk_adj['risk_signals']:
                print(f"  触发信号: {len(risk_adj['risk_signals'])}个")
                for i, signal in enumerate(risk_adj['risk_signals'][:3], 1):
                    level_icon = '🔴' if signal['level'] == 'high' else '🟡'
                    print(f"    {i}. {level_icon} {signal['message']}")
        
        # 投资建议
        print(f"\n【投资建议】")
        rec = result['recommendation']
        direction_map = {
            'strong_buy': '🟢 强烈做多',
            'buy': '🟢 做多',
            'hold': '🟡 观望',
            'sell': '🔴 做空'
        }
        print(f"  操作方向: {direction_map.get(rec['direction'], rec['direction'])}")
        print(f"  建议: {rec['advice']}")
        print(f"  仓位建议: {rec['position_size']}")
        
        if rec['risk_warnings']:
            print(f"\n  ⚠️  风险提示:")
            for warning in rec['risk_warnings']:
                print(f"    - {warning}")
        
        # 增强数据摘要
        print(f"\n【增强数据摘要】")
        enhanced = result['enhanced_data']
        macro = enhanced['macro']
        print(f"  美元指数: {macro['dollar_index']['value']:.2f}")
        print(f"  PMI: {macro['pmi']['value']:.1f}")
        print(f"  VIX: {macro['vix']['value']:.1f}")
        
        news = enhanced['news_sentiment']
        if 'error' not in news:
            print(f"  新闻情绪: {news['overall_sentiment']} ({news['overall_sentiment_score']:.2f})")
            if news['has_emergency']:
                print(f"  ⚠️  检测到突发事件: {len(news['emergency_events'])}个")
        
        print("\n" + "="*70)


if __name__ == '__main__':
    """测试"""
    predictor = EnhancedPredictor()
    
    # 执行预测
    result = predictor.predict_with_enhanced_data(horizon=5)
    
    # 打印摘要
    predictor.print_prediction_summary(result)
