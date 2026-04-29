import subprocess
import os

def copy_file_to_clipboard(path="clipboard.txt"):
    # 相対パスなら auto_files の絶対パスに変換
    if not os.path.isabs(path):
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, path)

    # ファイルを読む（元のロジックそのまま）
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # PowerShell（元のロジックそのまま）
    ps_command = f"$text = @'\n{content}\n'@; Set-Clipboard $text"

    subprocess.run([
        "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
        "-Command",
        ps_command
    ])

if __name__ == "__main__":
    copy_file_to_clipboard()
