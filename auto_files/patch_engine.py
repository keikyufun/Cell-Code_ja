import re

# @@ -a,b +c,d @@ の形式を解析するための正規表現
HUNK_HEADER_RE = re.compile(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')

def apply_patch_unified(original_text, diff_text):
    """
    unified diff を元テキストに適用して新しいテキストを返す。
    Git のパッチ形式に対応し、複数の hunk も処理できる。
    """
    original_lines = original_text.splitlines(keepends=True)
    diff_lines = diff_text.splitlines(keepends=True)

    patched_lines = []
    orig_index = 0
    i = 0

    # 先頭の --- と +++ は読み飛ばす
    while i < len(diff_lines):
        if diff_lines[i].startswith('@@'):
            break
        i += 1

    # 各 hunk を順に処理
    while i < len(diff_lines):
        header = diff_lines[i]
        m = HUNK_HEADER_RE.match(header)
        if not m:
            break

        start_old = int(m.group(1))
        count_old = int(m.group(2) or '1')
        start_new = int(m.group(3))

        i += 1

        # hunk 開始位置までの変更されない部分をコピー
        target_index = start_old - 1
        while orig_index < target_index and orig_index < len(original_lines):
            patched_lines.append(original_lines[orig_index])
            orig_index += 1

        # hunk 本体を処理
        while i < len(diff_lines):
            line = diff_lines[i]
            if line.startswith('@@'):
                break
            if line.startswith(' '):
                if orig_index < len(original_lines):
                    patched_lines.append(original_lines[orig_index])
                    orig_index += 1
            elif line.startswith('-'):
                if orig_index < len(original_lines):
                    orig_index += 1
            elif line.startswith('+'):
                patched_lines.append(line[1:])
            else:
                break
            i += 1

    # 残りの元ファイル行をコピー
    while orig_index < len(original_lines):
        patched_lines.append(original_lines[orig_index])
        orig_index += 1

    return ''.join(patched_lines)
