import json
import re
import sys

# 入力ファイル（myfile.txt）
input_path = "myfile.txt"
# 出力ファイル（for_python.txt）
output_path = "for_python.txt"

def load_raw_text():
    with open(input_path, "r", encoding="utf-8") as f:
        return f.read()

def remove_deepthink(text):
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        if "考え中…" in line:
            continue
        if "自分の考えを整理し、計画を作成する" in line:
            continue
        cleaned.append(line)
    return "\n".join(cleaned)

def extract_json(text):
    match = re.search(r"[\{\[]", text)
    if not match:
        raise ValueError("JSON の開始位置が見つかりません")
    start = match.start()
    return text[start:]

def fix_broken_content_lines(text):
    lines = text.splitlines()
    out = []
    in_block = False
    buffer = None

    for line in lines:
        stripped = line.strip()

        # content_lines 開始検出（改行ありにも対応）
        if not in_block and stripped.startswith('"content_lines"'):
            in_block = True
            out.append(line)
            continue

        # content_lines 終了
        if in_block and stripped == ']':
            if buffer is not None:
                out.append(buffer)
                buffer = None
            out.append(line)
            in_block = False
            continue

        # ブロック外
        if not in_block:
            out.append(line)
            continue

        # ブロック内
        if stripped.startswith('"'):
            # 正常行
            if buffer is not None:
                out.append(buffer)
            buffer = line
        else:
            # 壊れた行 → 前の行に結合
            if buffer is None:
                out.append(line)
            else:
                buffer = buffer.rstrip() + " " + stripped.lstrip()

    if buffer is not None:
        out.append(buffer)

    return "\n".join(out)

# ★★★ JSON を壊さずにそのままパース ★★★
def try_parse_json(text):
    text = text.replace("\r", "").strip()

    try:
        return json.loads(text)
    except Exception as e:
        print("JSON パース失敗:", e)
        print("---- 整形後のテキスト ----")
        print(text)
        sys.exit(1)

def save_json(obj):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def main():
    raw = load_raw_text()
    cleaned = remove_deepthink(raw)
    json_text = extract_json(cleaned)

    # ★ content_lines の途切れ修復
    json_text = fix_broken_content_lines(json_text)

    parsed = try_parse_json(json_text)
    save_json(parsed)
    print("[info] JSON 整形完了 → for_python.txt に保存しました")

if __name__ == "__main__":
    main()
