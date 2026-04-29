#!/bin/bash
set -e

BASE_DIR="$(cd "$(dirname "$(realpath "$0")")/.." && pwd)"
FILES_DIR="$BASE_DIR/auto_files"

cd "$FILES_DIR"

echo "--------------------------------------"
echo "[info] ゴールを入力してください。"
echo "       入力終了は Ctrl+D です。"
echo "--------------------------------------"

# 複数行入力 → goal.txt
cat > goal.txt

echo "[info] ゴールを受け取りました。 → $(head -n 1 goal.txt)"

# clipboard.txt を生成（auto.txt + goal.txt）
{
    cat "$BASE_DIR/auto.txt"
    echo "以下がゴールです"
    cat goal.txt
} > clipboard.txt
