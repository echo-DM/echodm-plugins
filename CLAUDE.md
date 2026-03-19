# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin for **anti-sudden-death health assessment** (程序员防猝死), part of the `echodm-plugins` collection.

## Commands

### Running the Risk Assessment

```bash
# View current risk status (run from project root)
python3 plugins/anti-rip/skills/anti-rip/scripts/rip.py

# Set baseline fatigue level (0-7) after full assessment: -fa <points>
python3 plugins/anti-rip/skills/anti-rip/scripts/rip.py -fa 3

# Add daily risk points after daily assessment: -da <points>
python3 plugins/anti-rip/skills/anti-rip/scripts/rip.py -da 15

# Reset all data (clear fatigue history): -r
python3 plugins/anti-rip/skills/anti-rip/scripts/rip.py -r
```

### Development

This is a Claude Code plugin, not a traditional project. To develop/test:
- The skill is invoked via `/anti-rip` or keywords like "猝死风险评估", "疲劳自测" when Claude Code is running with this plugin
- Tests run via direct execution of `rip.py`

## Architecture

```
echodm-plugins/                          # Plugin collection root
├── plugins/
│   └── anti-rip/                       # Anti-sudden-death plugin
│       ├── .claude-plugin/plugin.json # Plugin manifest
│       └── skills/
│           └── anti-rip/
│               ├── SKILL.md             # Skill definition and usage guide
│               ├── lib/risk_index.py    # Core risk calculation & data persistence
│               ├── scripts/rip.py        # CLI tool for risk management
│               ├── references/          # Questionnaires (Japanese labor standards)
│               │   ├── full_assessment_questions.md
│               │   └── daily_assessment_questions.md
│               ├── hooks/
│               │   ├── hooks.json       # SessionStart hook config
│               │   └── show_risk.sh    # Hook script to show risk on session start
│               └── assets/              # Documentation and PDFs
```

### Key Components

- **`skills/anti-rip/lib/risk_index.py`**: Core module with risk calculation algorithms. Data persisted to `~/.anti-rip-skill/data.json`
- **`skills/anti-rip/scripts/rip.py`**: CLI interface for viewing/updating risk scores
- **`skills/anti-rip/hooks/show_risk.sh`**: Runs on Claude Code session start to display current risk

### Risk Calculation

- Baseline risk (0-100) derived from 27-item fatigue assessment (fatigue points 0-7)
- Daily risk accumulation from questionnaire
- Risk levels: 0-20 (低风险), 21-45 (偏高), 46-75 (高危), 76-100 (极度危险)
- P0 symptoms (胸闷/胸痛/心悸/etc.) immediately set risk to 100

### Modifying the Plugin

- **Adding questions**: Edit `references/full_assessment_questions.md` or `daily_assessment_questions.md`
- **Risk algorithm changes**: Modify `lib/risk_index.py` (data at `~/.anti-rip-skill/data.json`)
- **Plugin manifest**: `.claude-plugin/plugin.json` defines commands, skills, and hooks
- **Skill invocation**: `/anti-rip` or keywords trigger the skill when Claude Code has this plugin loaded
