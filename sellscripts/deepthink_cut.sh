#!/bin/bash
set -e

BASE_DIR="$(cd "$(dirname "$(realpath "$0")")/.." && pwd)"
FILES_DIR="$BASE_DIR/auto_files"

cd "$FILES_DIR"

# JSON 開始行（スペース許容）
start_line=$(grep -n '^[[:space:]]*[\[{]' myfile.txt | head -n 1 | cut -d: -f1)

# JSON 終了行（スペース許容）
end_line=$(grep -n '^[[:space:]]*[\]}]' myfile.txt | tail -n 1 | cut -d: -f1)

# 開始・終了が見つからない場合は myfile.txt をそのままコピー
if [ -z "$start_line" ] || [ -z "$end_line" ]; then
    cp myfile.txt for_python.txt
    exit 0
fi

# JSON 部分だけ抽出して上書き
sed -n "${start_line},${end_line}p" myfile.txt > myfile_tmp.txt
mv myfile_tmp.txt myfile.txt
