"""薄包装：调用 cover-brand-bar 脚本，把 EMOJI_DIR 重定向到工作区资产目录。

skill 包内 assets/ 缺失（头像/emoji 不在包内），工作区有备份：
- emoji: /Coze/Drive/自媒体运营达人/所有对话/主对话/assets/emoji/
- avatar: 通过 config bar.avatar 显式指定
"""
import os
import sys

SCRIPT_DIR = "/Coze/Drive/自媒体运营达人/所有对话/主对话/.skills/skill_cover-brand-bar/scripts"
WORKSPACE_EMOJI = "/Coze/Drive/自媒体运营达人/所有对话/主对话/assets/emoji"

sys.path.insert(0, SCRIPT_DIR)
import brand_bar  # noqa: E402

brand_bar.EMOJI_DIR = WORKSPACE_EMOJI
brand_bar.main()
