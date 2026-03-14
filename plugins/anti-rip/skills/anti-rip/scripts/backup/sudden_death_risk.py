# -*- coding: utf-8 -*-
"""
猝死风险指数系统 - 交互式CLI
用于Claude Code Skill的交互接口
"""

import json
import os
import sys
from datetime import datetime

# 添加lib目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from risk_index import (
    get_or_init_data,
    update_baseline,
    update_daily_risk,
    get_current_status,
    fatigue_to_risk,
    get_risk_level,
    get_risk_advice,
    DAILY_QUESTIONS,
    FATIGUE_SYMPTOMS,
    FATIGUE_WORK,
    reset_data
)


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_question(q, options):
    """打印问题并返回用户选择的值"""
    print(f"\n{q}")
    for i, (text, value) in enumerate(options, 1):
        print(f"  {i}. {text}")

    while True:
        try:
            choice = input(f"请输入选项编号 (1-{len(options)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx][1]
            else:
                print(f"输入无效，请输入 1 到 {len(options)} 之间的数字。")
        except ValueError:
            print("输入无效，请输入数字。")


def print_multi_select_question(q, options):
    """打印多选题并返回用户选择的值列表"""
    print(f"\n{q}")
    for i, (text, value) in enumerate(options, 1):
        print(f"  {i}. {text}")
    print("  （可多选，用逗号分隔，如：1,3,5）")

    while True:
        try:
            choice = input("请输入选项编号: ").strip()
            if not choice:
                return ["无"]

            indices = [int(x.strip()) - 1 for x in choice.split(",")]
            if all(0 <= idx < len(options) for idx in indices):
                return [options[idx][1] for idx in indices]
            else:
                print("输入无效，请输入有效的选项编号。")
        except ValueError:
            print("输入无效，请输入数字。")


def run_fatigue_assessment():
    """运行疲劳程度自测"""
    print_header("疲劳程度自测")

    print("\n本检查表通过您的「自觉症状」和「近1个月的勤务状况」")
    print("来判定您的疲劳蓄积程度。")
    print("请根据实际情况回答以下问题。\n")

    # 第一部分：自觉症状
    print("-" * 60)
    print("【第一部分：最近1个月的自觉症状】")
    print("-" * 60)

    symptom_options = [("几乎没有", 0), ("有时有", 1), ("经常有", 3)]

    symptom_score = 0
    for i, symptom in enumerate(FATIGUE_SYMPTOMS, 1):
        print(f"\n{i}. {symptom}")
        for j, (text, score) in enumerate(symptom_options, 1):
            print(f"  {j}. {text} (得分: {score})")

        while True:
            try:
                choice = int(input(f"请选择 (1-3): ").strip())
                if 1 <= choice <= 3:
                    symptom_score += symptom_options[choice - 1][1]
                    break
                else:
                    print("输入无效，请输入1-3之间的数字。")
            except ValueError:
                print("输入无效，请输入数字。")

    # 计算自觉症状等级
    if symptom_score <= 2:
        symptom_cat = 'I'
    elif symptom_score <= 7:
        symptom_cat = 'II'
    elif symptom_score <= 14:
        symptom_cat = 'III'
    else:
        symptom_cat = 'IV'

    print(f"\n>> 自觉症状总分: {symptom_score} 点 -> 等级: {symptom_cat}")

    # 第二部分：勤务状况
    print("\n" + "-" * 60)
    print("【第二部分：最近1个月的勤务状况】")
    print("-" * 60)

    work_score = 0
    for i, (question, opt_texts) in enumerate(FATIGUE_WORK, 1):
        print(f"\n{question}")
        # 构建选项
        if len(opt_texts) == 2:
            options = [(opt_texts[0], 0), (opt_texts[1], 1)]
        elif len(opt_texts) == 3:
            options = [(opt_texts[0], 0), (opt_texts[1], 1), (opt_texts[2], 3)]
        else:
            options = [(opt_texts[0], 0), (opt_texts[1], 1)]

        for j, (text, score) in enumerate(options, 1):
            print(f"  {j}. {text} (得分: {score})")

        while True:
            try:
                choice = int(input(f"请选择 (1-{len(options)}): ").strip())
                if 1 <= choice <= len(options):
                    work_score += options[choice - 1][1]
                    break
                else:
                    print(f"输入无效，请输入1-{len(options)}之间的数字。")
            except ValueError:
                print("输入无效，请输入数字。")

    # 计算勤务状况等级
    if work_score == 0:
        work_cat = 'A'
    elif work_score <= 5:
        work_cat = 'B'
    elif work_score <= 11:
        work_cat = 'C'
    else:
        work_cat = 'D'

    print(f"\n>> 勤务状况总分: {work_score} 点 -> 等级: {work_cat}")

    # 综合判定
    fatigue_matrix = {
        'I':   {'A': 0, 'B': 0, 'C': 2, 'D': 4},
        'II':  {'A': 0, 'B': 1, 'C': 3, 'D': 5},
        'III': {'A': 0, 'B': 2, 'C': 4, 'D': 6},
        'IV':  {'A': 1, 'B': 3, 'C': 5, 'D': 7},
    }

    fatigue_value = fatigue_matrix[symptom_cat][work_cat]

    # 更新基准值
    baseline_risk = update_baseline(fatigue_value)

    # 显示结果
    print_header("诊断结果")
    print(f"\n您的疲劳蓄积度点数为: 【{fatigue_value}】 (范围0-7)")
    print(f"对应的风险指数为: 【{baseline_risk}】 (范围0-100)")

    judgments = {
        0: "较低",
        1: "较低",
        2: "偏高",
        3: "偏高",
        4: "较高",
        5: "较高",
        6: "非常高",
        7: "非常高"
    }
    print(f"\n判定结果: 疲劳蓄积度 {judgments[fatigue_value]}")

    if fatigue_value >= 2:
        print("\n【预防对策建议】")
        print("点数在2-7的人，可能已经蓄积了疲劳。")
        print("请检查您在「勤务状况」中得分为1或3的项目。")
        print("- 个人可裁量改善的项目：请自行改善。")
        print("- 个人无法裁量改善的项目：请与上司或产业医等沟通改善勤务状况。")

    return fatigue_value, baseline_risk


def run_daily_check():
    """运行每日简洁问答"""
    print_header("每日风险评估")

    answers = {}

    # 问题1-4: 单选题
    for q in DAILY_QUESTIONS[:4]:
        answers[q['id']] = print_question(q['question'], q['options'])

    # 问题5: 多选题
    answers[DAILY_QUESTIONS[4]['id']] = print_multi_select_question(
        DAILY_QUESTIONS[4]['question'],
        DAILY_QUESTIONS[4]['options']
    )

    # 问题6-7: 单选题
    for q in DAILY_QUESTIONS[5:]:
        answers[q['id']] = print_question(q['question'], q['options'])

    # 计算风险
    current_risk, risk_increase = update_daily_risk(answers)

    # 显示结果
    print_header("评估结果")

    level, level_desc = get_risk_level(current_risk)

    print(f"\n风险指数: {current_risk} / 100")
    print(f"状态: {level}")
    print(f"\n本次风险增量: +{risk_increase}")

    print("\n【建议】")
    for advice in get_risk_advice(current_risk):
        print(f"  - {advice}")

    return current_risk


def show_current_status():
    """显示当前状态"""
    status = get_current_status()

    print_header("当前状态")

    if status['baseline_fatigue'] is None:
        print("\n尚未进行疲劳程度自测，请先完成自测以建立基准值。")
        return False
    else:
        print(f"\n基准疲劳点数: {status['baseline_fatigue']}")
        print(f"基准风险指数: {status['baseline_risk']}")
        print(f"当前风险指数: {status['current_risk']}")
        print(f"最后自测日期: {status['last_assessment']}")
        if status['last_daily_check']:
            print(f"最后每日检查: {status['last_daily_check']}")

        level, level_desc = get_risk_level(status['current_risk'])
        print(f"\n当前状态: {level}")

        print("\n【建议】")
        for advice in get_risk_advice(status['current_risk']):
            print(f"  - {advice}")

        return True


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="猝死风险指数系统")
    parser.add_argument('--status', action='store_true', help='查看当前状态')
    parser.add_argument('--full', action='store_true', help='进行完整的疲劳程度自测')
    parser.add_argument('--daily', action='store_true', help='进行每日简洁问答')
    parser.add_argument('--reset', action='store_true', help='重置所有数据')

    args = parser.parse_args()

    if args.reset:
        confirm = input("确定要重置所有数据吗？(y/n): ")
        if confirm.lower() == 'y':
            reset_data()
            print("数据已重置。")
        return

    if args.status:
        show_current_status()
        return

    # 检查是否有基准值
    status = get_current_status()

    if args.full or status['baseline_fatigue'] is None:
        # 进行完整的疲劳自测
        run_fatigue_assessment()
    elif args.daily:
        # 进行每日问答
        run_daily_check()
    else:
        # 显示当前状态
        show_current_status()
        print("\n请选择操作:")
        print("  1. 进行每日简洁问答")
        print("  2. 重新进行疲劳程度自测")
        print("  3. 查看当前状态")
        print("  4. 退出")

        choice = input("\n请输入选项 (1-4): ").strip()

        if choice == '1':
            run_daily_check()
        elif choice == '2':
            run_fatigue_assessment()
        elif choice == '3':
            show_current_status()
        else:
            print("\n再见！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作已取消。")
