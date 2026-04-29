#!/bin/bash
set -e

BASE_DIR="$(cd "$(dirname "$(realpath "$0")")/.." && pwd)"
FILES_DIR="$BASE_DIR/auto_files"

cd "$FILES_DIR"

echo "[info] myfile.txt の生成を待機中..."

while [ ! -s myfile.txt ]; do
    sleep 1
done

echo "[info] myfile.txt を検出しました。"
