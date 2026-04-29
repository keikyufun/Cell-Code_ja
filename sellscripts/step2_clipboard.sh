#!/bin/bash
set -e

echo "===== step2_clipboard.sh DEBUG ====="

# BASE_DIR を絶対パスで取得
BASE_DIR="$(cd "$(dirname "$(realpath "$0")")/.." && pwd)"
echo "BASE_DIR = '$BASE_DIR'"

# run_clip.ps1 のパス
PS1_PATH="$BASE_DIR/run_clip.ps1"
echo "PS1_PATH (Linux) = '$PS1_PATH'"

# wslpath に渡す値を表示
echo "wslpath input = '$PS1_PATH'"

# wslpath 実行
WIN_PS1_PATH=$(wslpath -w "$PS1_PATH" 2>&1)
echo "wslpath output = '$WIN_PS1_PATH'"

echo "===== END DEBUG ====="
