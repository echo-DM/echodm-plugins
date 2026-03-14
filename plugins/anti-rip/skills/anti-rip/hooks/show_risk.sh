#!/bin/bash
set -euo pipefail

DATA_FILE="$HOME/.anti-rip-skill/data.json"

# Check if data file exists
if [ ! -f "$DATA_FILE" ]; then
  echo '{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "未找到猝死风险数据文件"}}'
  exit 0
fi

# Extract current_risk value
current_risk=$(jq -r '.current_risk // 0' "$DATA_FILE")
echo "当前猝死风险指数: $current_risk"

# Output in the required format
# echo "{\"hookSpecificOutput\": {\"hookEventName\": \"SessionStart\", \"additionalContext\": \"当前猝死风险指数: $current_risk\, 在每个开头显示这个指数"}}"
cat << EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "每次你输出文本的时候都以\n\"尊敬的阁下，您当前 RIP progress 为 ${current_risk}%\"开头，并用 ASCII 画出进度条。"
  }
}
EOF

exit 0
