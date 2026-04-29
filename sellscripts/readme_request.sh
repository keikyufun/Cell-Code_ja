#!/bin/bash
set -e

BASE_DIR="$(cd "$(dirname "$(realpath "$0")")/.." && pwd)"
FILES_DIR="$BASE_DIR/auto_files"

cd "$FILES_DIR"

# Copilot への README 生成リクエスト
README_PROMPT="日本語版のREADME_ja.mdと英語版のREADME.mdをつくってください。"

echo "$README_PROMPT" > clipboard.txt
python3 copy_clipboard.py

# run_clip.ps1 の Windows パスを安全に生成
WIN_PS1_PATH=$(printf '%s\n' "$BASE_DIR/run_clip.ps1" | wslpath -w)

# clipboard.exe の Windows パス
WIN_CLIP_EXE=$(printf '%s\n' "$FILES_DIR/clipboard.exe" | wslpath -w)

# 実行
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$WIN_PS1_PATH" "$WIN_CLIP_EXE"

# JSON 抽出
awk 'f{print} /[\[\{]/{f=1}' myfile.txt > for_python.txt

# Python 実行
python3 "$FILES_DIR/auto.py" "$FILES_DIR/for_python.txt"
