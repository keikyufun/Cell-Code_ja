#!/bin/bash
set -e

# auto.sh がある sellscripts を基準に BASE_DIR を決定
BASE_DIR="$(cd "$(dirname "$(realpath "$0")")/.." && pwd)"
SCRIPT_DIR="$BASE_DIR/sellscripts"

# venv
if [ -d "$BASE_DIR/venv" ]; then
    echo "[info] venv を有効化しました。"
    source "$BASE_DIR/venv/bin/activate"
fi

# ゴール入力
"$SCRIPT_DIR/step1_prompt.sh"

# 1回目
"$SCRIPT_DIR/step2_clipboard.sh"
"$SCRIPT_DIR/wait_myfile.sh"
"$SCRIPT_DIR/deepthink_cut.sh"
"$SCRIPT_DIR/run_auto_py.sh"

# FINISH までループ
while ! "$SCRIPT_DIR/finish_check.sh"; do
    "$SCRIPT_DIR/step2_clipboard.sh"
    "$SCRIPT_DIR/wait_myfile.sh"
    "$SCRIPT_DIR/deepthink_cut.sh"
    "$SCRIPT_DIR/run_auto_py.sh"
done

# README 生成
"$SCRIPT_DIR/readme_request.sh"

echo ""
echo "[info] 完了しました。"
