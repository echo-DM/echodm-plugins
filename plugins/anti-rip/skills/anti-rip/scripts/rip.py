#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险指数管理工具

用法:
    python3 rip.py          # 查看当前状态
    python3 rip.py -fa 3    # 设置疲劳蓄积度为3，基准风险指数
    python3 rip.py -da 15   # 增加风险指数 15 点（同时标记每日快速评估完成）
    python3 rip.py -e       # 检查完整自测和每日快速评估是否完成
    python3 rip.py -r       # 重置所有疲劳数据
"""

import argparse
import sys
import os
from datetime import datetime

# 添加 lib 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from risk_index import update_baseline, update_risk, get_current_status, get_risk_level, get_risk_advice, reset_data


def main():
    parser = argparse.ArgumentParser(description='更新风险指数')
    parser.add_argument('-fa', '--fatigue', type=int,
                        help='疲劳蓄积度 (0-7)，设置基准风险指数')
    parser.add_argument('-da', '--add-risk', type=int,
                        help='增加风险指数点数 (0-100)')
    parser.add_argument('-r', '--reset', action='store_true',
                        help='重置所有疲劳数据')
    parser.add_argument('-e', '--evaluate', action='store_true',
                        help='检查完整自测和每日快速评估是否完成')

    args = parser.parse_args()

    # -e: 检查评估完成状态
    if args.evaluate:
        status = get_current_status()
        today = datetime.now().strftime("%Y-%m-%d")

        print("=" * 40)
        print("评估完成状态")
        print("=" * 40)

        # 检查完整自测
        full_done = status['last_assessment'] is not None
        if full_done:
            full_date = status['last_assessment'][:10]
            full_status = "✅ 已完成" if full_date == today else f"⚠️ 已完成（{full_date}，需重新评估）"
        else:
            full_status = "❌ 未完成"
        print(f"完整自测（27项）: {full_status}")

        # 检查每日快速评估
        daily_done = status['last_daily_check'] is not None
        if daily_done:
            daily_date = status['last_daily_check'][:10]
            daily_status = "✅ 已完成" if daily_date == today else f"⚠️ 需今日重新评估"
        else:
            daily_status = "❌ 未完成"
        print(f"每日快速评估: {daily_status}")

        print("-" * 40)

        # 总结
        if full_done and daily_done:
            # 检查是否是今天完成的
            full_date = status['last_assessment'][:10]
            daily_date = status['last_daily_check'][:10]
            if full_date == today and daily_date == today:
                print("🎉 今日评估已全部完成！")
            else:
                print("📋 需补全今日评估项目")
        else:
            missing = []
            if not full_done:
                missing.append("完整自测")
            if not daily_done:
                missing.append("每日快速评估")
            print(f"缺少: {', '.join(missing)}")

        print("=" * 40)
        sys.exit(0)

    # -r: 重置所有数据
    if args.reset:
        reset_data()
        print("已重置所有疲劳数据")
        sys.exit(0)

    # -fa: 设置基准风险指数
    if args.fatigue is not None:
        fatigue_points = args.fatigue
        if fatigue_points < 0 or fatigue_points > 7:
            print(f"错误: 疲劳蓄积度应在 0-7 之间，当前值: {fatigue_points}")
            sys.exit(1)

        baseline_risk = update_baseline(fatigue_points)
        print(f"疲劳蓄积度: {fatigue_points}")
        print(f"基准风险指数: {baseline_risk}")

    # -da: 增加风险指数
    elif args.add_risk is not None:
        if args.add_risk < 0 or args.add_risk > 100:
            print(f"错误: 增加的风险指数应在 0-100 之间，增加的风险指数: {args.add_risk}")
            sys.exit(1)

        status = get_current_status()
        current_risk = status['current_risk']
        print(f"当前风险指数: {current_risk}")

        current_risk += args.add_risk
        current_risk = min(100, current_risk)

        current_risk = update_risk(current_risk, is_daily=True)
        print(f"增加风险: +{args.add_risk}")
        print(f"当前风险指数: {current_risk}")

    else:
        # 无参数时显示当前状态
        status = get_current_status()
        level, desc = get_risk_level(status['current_risk'])
        advice = get_risk_advice(status['current_risk'])

        print("=" * 40)
        print("当前风险状态")
        print("=" * 40)
        print(f"当前风险: {status['current_risk']} ({level})")
        print(f"风险描述: {desc}")
        print("-" * 40)
        print("建议:")
        for item in advice:
            print(f"  • {item}")
        print("-" * 40)
        print(f"上次评估: {status['last_assessment'] or '无'}")
        print(f"上次每日检查: {status['last_daily_check'] or '无'}")
        print("=" * 40)


if __name__ == '__main__':
    main()
