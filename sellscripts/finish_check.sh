#!/bin/bash

BASE_DIR="$(cd "$(dirname "$(realpath "$0")")/.." && pwd)"
FILES_DIR="$BASE_DIR/auto_files"

cd "$FILES_DIR"

# JSON の "type": "finish" 検出
if grep -Eqi '"type"[[:space:]]*:[[:space:]]*"finish"' for_python.txt; then
    exit 0
else
    exit 1
fi