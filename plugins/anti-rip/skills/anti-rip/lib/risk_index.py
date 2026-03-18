# -*- coding: utf-8 -*-
"""
猝死风险指数系统 - 核心模块
负责数据持久化和风险指数计算
"""

import json
import os
from datetime import datetime
from pathlib import Path

# 数据文件路径
DATA_FILE = os.path.expanduser("~/.anti-rip-skill/data.json")

# 确保数据目录存在
DATA_DIR = os.path.dirname(DATA_FILE)
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def load_data():
    """加载数据文件"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    return None


def save_data(data):
    """保存数据到文件"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def init_data():
    """初始化数据结构"""
    return {
        "baseline_fatigue": None,
        "baseline_risk": None,
        "current_risk": 0,
        "last_assessment": None,
        "last_daily_check": None,
        "history": []
    }


def get_or_init_data():
    """获取或初始化数据"""
    data = load_data()
    if data is None:
        data = init_data()
        save_data(data)
    return data


def fatigue_to_risk(fatigue_points):
    """
    将疲劳点数（0-7）转换为风险指数（0-100）
    使用非线性映射，高分区间更陡峭
    """
    if fatigue_points <= 1:
        # 0-1分 -> 0-20
        return int(20 * fatigue_points)
    elif fatigue_points <= 3:
        # 2-3分 -> 20-45
        return int(20 + 25 * (fatigue_points - 2))
    elif fatigue_points <= 5:
        # 4-5分 -> 45-75
        return int(45 + 30 * (fatigue_points - 4))
    else:
        # 6-7分 -> 75-100
        return int(75 + 25 * (fatigue_points - 6))


def get_risk_level(risk_index):
    """根据风险指数获取等级和描述"""
    if risk_index <= 20:
        return "低风险", "安全区，请继续保持良好的生活习惯"
    elif risk_index <= 45:
        return "偏高", "需要注意休息，避免过度劳累"
    elif risk_index <= 75:
        return "高危", "危险区，建议尽快安排体检"
    else:
        return "极度危险", "极其危险，请立即休息并考虑就医"


def get_risk_advice(risk_index):
    """根据风险指数获取建议"""
    if risk_index <= 20:
        return [
            "继续保持规律的作息时间",
            "保证充足的睡眠（7-8小时）",
            "适度运动，保持身体健康"
        ]
    elif risk_index <= 45:
        return [
            "注意休息，避免熬夜",
            "增加睡眠时间，争取22点前入睡",
            "减少加班，注意工作节奏",
            "适当进行放松活动"
        ]
    elif risk_index <= 75:
        return [
            "强烈建议近期安排全面体检",
            "立即调整工作强度，保证充足休息",
            "如有不适症状，请及时就医",
            "避免剧烈运动和过度劳累"
        ]
    else:
        return [
            "【紧急】请立即停止工作，充分休息",
            "如有胸闷、胸痛、心悸等症状，请立即就医",
            "联系家人或朋友，确保有人陪伴",
            "避免独自驾车或进行危险活动"
        ]


def calculate_daily_risk(answers):
    """
    根据每日问答答案计算风险增量
    answers: 包含7个问题答案的字典
    """
    risk_increase = 0

    # 问题1: 睡眠时长
    sleep_hours = answers.get('sleep_hours', '>7h')
    sleep_scores = {
        '<5h': 15,
        '5-6h': 8,
        '6-7h': 3,
        '>7h': 0
    }
    risk_increase += sleep_scores.get(sleep_hours, 0)

    # 问题2: 上床时间
    bed_time = answers.get('bed_time', '<24点')
    bed_scores = {
        '>2点': 30,
        '1-2点': 20,
        '0-1点': 10,
        '<24点': 5
    }
    risk_increase += bed_scores.get(bed_time, 0)

    # 问题3: 工作时长
    work_hours = answers.get('work_hours', '<8h')
    work_scores = {
        '>12h': 25,
        '10-12h': 15,
        '8-10h': 5,
        '<8h': 0
    }
    risk_increase += work_scores.get(work_hours, 0)

    # 问题4: 久坐时长
    sit_hours = answers.get('sit_hours', '<2h')
    sit_scores = {
        '>8h': 20,
        '4-8h': 10,
        '2-4h': 5,
        '<2h': 0
    }
    risk_increase += sit_scores.get(sit_hours, 0)

    # 问题5: 症状（P0级直接100，P1级+25）
    symptoms = answers.get('symptoms', [])
    p0_symptoms = ['胸闷', '胸痛', '压迫感', '心悸', '心跳不规律', '眼前发黑', '晕厥', '剧烈头痛']
    p1_symptoms = ['极度疲乏', '一身冷汗']

    # 检查是否有P0级症状
    has_p0 = any(s in p0_symptoms for s in symptoms)
    has_p1 = any(s in p1_symptoms for s in symptoms)

    if has_p0:
        return 100  # 直接返回100
    elif has_p1:
        return 25  # P1级直接返回25，不再累加其他分数

    # 问题6: 咖啡因摄入
    caffeine = answers.get('caffeine', '正常')
    caffeine_scores = {
        '正常': 0,
        '较多': 5,
        '过量': 15
    }
    risk_increase += caffeine_scores.get(caffeine, 0)

    # 问题7: 情绪状态
    emotion = answers.get('emotion', '平稳')
    emotion_scores = {
        '平稳': 0,
        '易怒': 5,
        '麻木/低落': 10
    }
    risk_increase += emotion_scores.get(emotion, 0)

    return risk_increase


def update_baseline(fatigue_points):
    """更新基准值"""
    data = get_or_init_data()

    baseline_risk = fatigue_to_risk(fatigue_points)

    data['baseline_fatigue'] = fatigue_points
    data['baseline_risk'] = baseline_risk
    data['current_risk'] = baseline_risk
    data['last_assessment'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_data(data)

    return baseline_risk


def update_risk(risk_score, is_daily=False):
    data = get_or_init_data()
    data['current_risk'] = risk_score
    data['last_assessment'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if is_daily:
        data['last_daily_check'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_data(data)

    return data['current_risk']


def update_daily_risk(answers):
    """更新每日风险指数"""
    data = get_or_init_data()

    # 计算风险增量
    risk_increase = calculate_daily_risk(answers)

    # 如果是P0级症状，直接设为100
    if risk_increase == 100:
        data['current_risk'] = 100
    else:
        # 风险指数只增不减
        data['current_risk'] = min(100, data['current_risk'] + risk_increase)

    # 记录历史
    history_entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "risk_increase": risk_increase,
        "current_risk": data['current_risk'],
        "answers": answers
    }
    data['history'].append(history_entry)
    data['last_daily_check'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_data(data)

    return data['current_risk'], risk_increase


def get_current_status():
    """获取当前状态"""
    data = get_or_init_data()

    return {
        'baseline_fatigue': data.get('baseline_fatigue'),
        'baseline_risk': data.get('baseline_risk'),
        'current_risk': data.get('current_risk'),
        'last_assessment': data.get('last_assessment'),
        'last_daily_check': data.get('last_daily_check')
    }


def reset_data():
    """重置所有数据"""
    data = init_data()
    save_data(data)
    return data


# 每日问题定义
DAILY_QUESTIONS = [
    {
        "id": "sleep_hours",
        "question": "昨晚睡眠时长？",
        "options": [
            ("< 5小时", "<5h"),
            ("5-6小时", "5-6h"),
            ("6-7小时", "6-7h"),
            ("> 7小时", ">7h")
        ]
    },
    {
        "id": "bed_time",
        "question": "今晚上床时间？",
        "options": [
            ("> 凌晨2点", ">2点"),
            ("凌晨1-2点", "1-2点"),
            ("0-1点", "0-1点"),
            ("< 24点", "<24点")
        ]
    },
    {
        "id": "work_hours",
        "question": "今天工作时数？",
        "options": [
            ("> 12小时", ">12h"),
            ("10-12小时", "10-12h"),
            ("8-10小时", "8-10h"),
            ("< 8小时", "<8h")
        ]
    },
    {
        "id": "sit_hours",
        "question": "连续久坐时长？",
        "options": [
            ("> 8小时", ">8h"),
            ("4-8小时", "4-8h"),
            ("2-4小时", "2-4h"),
            ("< 2小时", "<2h")
        ]
    },
    {
        "id": "symptoms",
        "question": "是否有以下症状？（可多选）",
        "options": [
            ("无", "无"),
            ("胸闷/胸痛/压迫感 (P0)", "胸闷"),
            ("心悸/心跳不规律 (P0)", "心悸"),
            ("眼前发黑/晕厥 (P0)", "眼前发黑"),
            ("剧烈头痛 (P0)", "剧烈头痛"),
            ("极度疲乏 (P1)", "极度疲乏"),
            ("一身冷汗 (P1)", "一身冷汗")
        ]
    },
    {
        "id": "caffeine",
        "question": "今日咖啡因摄入？",
        "options": [
            ("正常", "正常"),
            ("较多 (咖啡3杯以上/奶茶2杯以上)", "较多"),
            ("过量 (明显心慌手抖)", "过量")
        ]
    },
    {
        "id": "emotion",
        "question": "今日情绪状态？",
        "options": [
            ("平稳", "平稳"),
            ("易怒/烦躁", "易怒"),
            ("麻木/低落", "麻木/低落")
        ]
    }
]


# 疲劳自测问题定义（14项自觉症状 + 13项勤务状况）
FATIGUE_SYMPTOMS = [
    "烦躁易怒",
    "感到不安",
    "无法静下心来",
    "感到忧郁",
    "睡眠不好",
    "身体状态不佳",
    "无法集中注意力",
    "做事经常出错",
    "工作中受到强烈的睡意侵袭",
    "提不起劲，没有干劲",
    "筋疲力尽（不含运动后）",
    "早上起床时感到极其疲惫",
    "相比以前，更容易疲劳",
    "感觉没有食欲"
]

FATIGUE_WORK = [
    ("1个月的劳动时间（含加班、休息日工作时间）", ["适当", "多", "非常多"]),
    ("2. 不规则的勤务（预定变更、突发工作）", ["少", "多"]),
    ("3. 出差带来的负担（频率、拘束时间、时差等）", ["没有或较小", "较大"]),
    ("4. 深夜勤务带来的负担", ["没有或较小", "较大", "非常大"]),
    ("5. 休息・假寐的时间及设施", ["适当", "不适当"]),
    ("6. 工作上的身体负担（肉体劳动或冷热环境）", ["较小", "较大", "非常大"]),
    ("7. 工作上的精神负担", ["较小", "较大", "非常大"]),
    ("8. 职场・顾客等人际关系带来的负担", ["较小", "较大", "非常大"]),
    ("9. 规定时间内处理不完的工作量", ["少", "多", "非常多"]),
    ("10. 无法按自己的节奏进行的工作", ["少", "多", "非常多"]),
    ("11. 下班后也总是挂念工作", ["几乎没有", "有时有", "经常有"]),
    ("12. 工作日的睡眠时间", ["充足", "稍微不足", "不足"]),
    ("13. 从下班到下一次上班之间的休息时间（勤务间歇）", ["充足", "稍微不足", "不足"])
]


if __name__ == "__main__":
    # 测试用
    print("猝死风险指数系统 - 测试")
    print("=" * 50)

    # 测试非线性映射
    print("\n疲劳点数 -> 风险指数映射测试：")
    for i in range(8):
        risk = fatigue_to_risk(i)
        print(f"  疲劳点数 {i} -> 风险指数 {risk}")

    print("\n风险等级测试：")
    for r in [10, 30, 50, 80, 100]:
        level, desc = get_risk_level(r)
        print(f"  风险指数 {r} -> {level}: {desc}")

    print("\n数据初始化测试:")
    data = get_or_init_data()
    print(f"  当前风险: {data['current_risk']}")
