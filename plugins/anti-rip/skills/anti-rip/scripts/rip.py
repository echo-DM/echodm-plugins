#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险指数管理工具

用法:
    python3 rip.py          # 查看当前状态
    python3 rip.py -fa 3    # 设置疲劳蓄积度为3，基准风险指数
    python3 rip.py -da 15   # 增加风险指数 15 点
"""

import argparse
import sys
import os

# 添加 lib 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from risk_index import update_baseline, update_risk, get_current_status, get_risk_level, get_risk_advice


def main():
    parser = argparse.ArgumentParser(description='更新风险指数')
    parser.add_argument('-fa', '--fatigue', type=int,
                        help='疲劳蓄积度 (0-7)，设置基准风险指数')
    parser.add_argument('-da', '--add-risk', type=int,
                        help='增加风险指数点数 (0-100)')

    args = parser.parse_args()

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

        current_risk = update_risk(current_risk)
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
