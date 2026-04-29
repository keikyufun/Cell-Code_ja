#!/bin/bash
set -e

BASE_DIR="$(cd "$(dirname "$(realpath "$0")")/.." && pwd)"
FILES_DIR="$BASE_DIR/auto_files"

cd "$FILES_DIR"

# JSON 整形（引数なし）
python3 json_format.py

echo "[info] JSON 整形完了 → for_python.txt に保存しました"

# auto.py 実行（引数なし）
python3 auto.py for_python.txt