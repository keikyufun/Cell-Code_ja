#!/bin/bash
set -e

BASE_DIR="$(cd "$(dirname "$(realpath "$0")")/.." && pwd)"
FILES_DIR="$BASE_DIR/auto_files"

cd "$FILES_DIR"

python3 python3 json_format.py

echo "[info] JSON 整形完了 → for_python.txt に保存しました"
