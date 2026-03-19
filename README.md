# echodm-plugins

Claude Code 插件集合，为程序员打造健康与效率工具。

## 插件列表

### anti-rip 猝死风险评估

通过疲劳自测评估猝死风险指数，守护程序员健康。

**功能**：
- 基于日本厚生劳动省官方疲劳自测问卷
- 评估疲劳蓄积程度，计算猝死风险指数（0-100）
- 风险过高时主动干预提醒

**使用方式**：
```
# Claude Code 中
"猝死风险评估" / "疲劳自测" / "健康风险检查" 或 "/anti-rip"

# 命令行
python3 plugins/anti-rip/skills/anti-rip/scripts/rip.py        # 查看状态
python3 plugins/anti-rip/skills/anti-rip/scripts/rip.py -e     # 检查评估完成
python3 plugins/anti-rip/skills/anti-rip/scripts/rip.py -fa 3  # 设置基准疲劳值
python3 plugins/anti-rip/skills/anti-rip/scripts/rip.py -da 15 # 添加每日风险点
python3 plugins/anti-rip/skills/anti-rip/scripts/rip.py -r      # 重置数据
```

> **提示**：每次启动 Claude Code 时会自动显示当前风险指数

**详情**：见 [plugins/anti-rip/README.md](plugins/anti-rip/README.md)

---

## 开发指南

本项目为 Claude Code 插件集合，每个插件独立管理。

### 添加新插件

在 `plugins/` 目录下创建新插件，结构如下：

```
plugins/
└── your-plugin/
    ├── .claude-plugin/
    │   └── plugin.json      # 插件清单
    └── skills/
        └── your-skill/
            └── SKILL.md    # Skill 定义
```

### 本地测试

插件通过 Claude Code 加载运行，测试方式：
1. 将插件目录链接到 Claude Code 插件目录
2. 在对话中触发 skill 关键词

---
