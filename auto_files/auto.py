import subprocess
import json
import os
import sys
from datetime import datetime
from patch_engine import apply_patch_unified as apply_patch

output_buffer = []
_original_print = print

def print(*args, **kwargs):
	text = " ".join(str(a) for a in args)
	output_buffer.append(text)
	_original_print(*args, **kwargs)

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(FILE_DIR)

WORKSPACE = os.path.join(BASE_DIR, "ai-workspace")
LOG_DIR = os.path.join(BASE_DIR, "ai_log")
AI_JSON_DIR = os.path.join(BASE_DIR, "ai_log", "ai_log")
CMD_LOG_DIR = os.path.join(BASE_DIR, "ai_log", "cmd_log")
AI_FILE_LIST = os.path.join(BASE_DIR, "ai_file.txt")
AI_FOLDER_LIST = os.path.join(BASE_DIR, "ai_folder.txt")
READONLY_DIR = os.path.join(BASE_DIR, "ai_readonly")

PROTECTED_FILES = ["schema.json", "executor.py", "ai_request.py", "system_prompt.txt"]

FORBIDDEN = {
	"rm": "危険な削除コマンド",
	"shutdown": "シャットダウンは禁止",
	"reboot": "再起動は禁止",
	"systemctl": "システム操作は禁止",
}

REQUIRES_PERMISSION = {
	"apt": "パッケージインストールは許可制",
	"apt-get": "パッケージインストールは許可制",
	"wget": "勝手なダウンロードは禁止",
	"curl": "勝手な通信は禁止",
	"ping": "ネットワーク攻撃の可能性（許可制）",
}

def save_ai_json(json_data):
	# AI の JSON ログ → ai_log/ai_log/
	os.makedirs(AI_JSON_DIR, exist_ok=True)

	files = [f for f in os.listdir(AI_JSON_DIR) if f.endswith(".txt")]
	num = len(files) + 1

	now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	filename = f"{num:04d}_{now}.txt"

	path = os.path.join(AI_JSON_DIR, filename)
	with open(path, "w", encoding="utf-8") as f:
		f.write(json.dumps(json_data, indent=2, ensure_ascii=False))

	return filename


def save_cmd_log(cmd, output):
	# コマンドログ → ai_log/cmd_log/
	os.makedirs(CMD_LOG_DIR, exist_ok=True)

	name = cmd[0].replace("/", "_")
	now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	filename = f"{name}_{now}.txt"

	path = os.path.join(CMD_LOG_DIR, filename)
	with open(path, "w", encoding="utf-8") as f:
		f.write(output)

	return filename

def is_forbidden(cmd):
	return cmd[0] in FORBIDDEN

def needs_permission(cmd):
	return cmd[0] in REQUIRES_PERMISSION

def is_path_safe(cmd):
	for part in cmd:
		if "../" in part or part.startswith("/"):
			return False
	return True

def touches_protected_file(cmd):
	for part in cmd:
		for protected in PROTECTED_FILES:
			if protected in part:
				return True
	return False

def run_command(cmd, timeout):
	try:
		result = subprocess.run(
			cmd, cwd=WORKSPACE, timeout=timeout,
			capture_output=True, text=True
		)
		return result.stdout + result.stderr
	except Exception as e:
		return str(e)

def normalize_path(path: str) -> str:
	path = path.replace("\\_", "_")
	path = path.replace("\\", "/")
	return path

def _execute_one(json_data):
	try:
		t = json_data.get("type")

		#  TXT 出力 
		if t == "txt":
			if "content_lines" in json_data:
				return {"kind": "txt", "content_lines": json_data["content_lines"]}
			else:
				return {"kind": "txt", "content": json_data.get("content", "")}

		#  BOT 
		if t == "bot":
			return {"kind": "txt", "content": json_data["message"]}

		#  ERROR 
		if t == "error":
			return {"kind": "txt", "content": f"エラー: {json_data['message']}"}

		#  READ FILE 
		if t == "read_file":
			path = json_data["path"]
			if "../" in path or path.startswith("/"):
				return {"kind": "txt", "content": "危険なパスです。"}

			candidates = [READONLY_DIR, WORKSPACE]
			full_path = None
			for base in candidates:
				p = os.path.join(base, path)
				if os.path.exists(p):
					full_path = p
					break

			if full_path is None:
				return {"kind": "txt", "content": f"ファイルが存在しません: {path}"}

			with open(full_path, "r", encoding="utf-8") as f:
				content = f.read()

			return {"kind": "read_file", "path": path, "content": content}

		#  MKDIR 
		if t == "mkdir":
			path = json_data["path"]
			full_path = os.path.join(WORKSPACE, path)
			os.makedirs(full_path, exist_ok=True)
			with open(AI_FOLDER_LIST, "a", encoding="utf-8") as f:
				f.write(path + "\n")
			return {"kind": "mkdir", "path": path}

		#  DELETE FOLDER 
		if t == "delete_folder":
			path = json_data["path"]
			if not os.path.exists(AI_FOLDER_LIST):
				return {"kind": "txt", "content": "フォルダ記録がありません。"}

			with open(AI_FOLDER_LIST, "r", encoding="utf-8") as f:
				folders = [line.strip() for line in f.readlines()]

			if path not in folders:
				return {"kind": "txt", "content": f"AI が作ったフォルダではありません: {path}"}

			full_path = os.path.join(WORKSPACE, path)
			os.rmdir(full_path)

			folders.remove(path)
			with open(AI_FOLDER_LIST, "w", encoding="utf-8") as f:
				for item in folders:
					f.write(item + "\n")

			return {"kind": "delete_folder", "path": path}

		#  FILE WRITE 
		if t == "file":
			path = json_data["path"]

			if "content_lines" in json_data:
				content = "\n".join(json_data["content_lines"])
			else:
				content = json_data.get("content", "")

			if "../" in path or path.startswith("/"):
				return {"kind": "txt", "content": "危険なパスです。"}

			for protected in PROTECTED_FILES:
				if protected in path:
					return {"kind": "txt", "content": "重要ファイルは書き換え禁止です。"}

			full_path = os.path.join(WORKSPACE, path)
			with open(full_path, "w", encoding="utf-8") as f:
				f.write(content)

			with open(AI_FILE_LIST, "a", encoding="utf-8") as f:
				f.write(path + "\n")

			return {"kind": "file", "path": path, "content": content}

		#  DELETE FILE 
		if t == "delete_file":
			path = json_data["path"]
			if not os.path.exists(AI_FILE_LIST):
				return {"kind": "txt", "content": "ファイル記録がありません。"}

			with open(AI_FILE_LIST, "r", encoding="utf-8") as f:
				files = [line.strip() for line in f.readlines()]

			if path not in files:
				return {"kind": "txt", "content": f"AI が作ったファイルではありません: {path}"}

			full_path = os.path.join(WORKSPACE, path)
			os.remove(full_path)

			files.remove(path)
			with open(AI_FILE_LIST, "w", encoding="utf-8") as f:
				for item in files:
					f.write(item + "\n")

			return {"kind": "delete_file", "path": path}

		#  CMD 
		if t == "cmd":
			cmd = json_data["cmd"]
			timeout = json_data["timeout"]

			if is_forbidden(cmd):
				return {"kind": "txt", "content": f"🛡️禁止コマンドです: {cmd[0]}"}
			if needs_permission(cmd):
				return {"kind": "txt", "content": f"🛡️許可が必要なコマンドです: {' '.join(cmd)}"}
			if not is_path_safe(cmd):
				return {"kind": "txt", "content": "🛡️危険なパスを検知しました。"}
			if touches_protected_file(cmd):
				return {"kind": "txt", "content": "🛡️重要ファイルへのアクセスは禁止です。"}

			output = run_command(cmd, timeout)
			logfile = save_cmd_log(cmd, output)

			return {"kind": "cmd", "cmd": cmd, "output": output, "log": logfile}

		#  PATCH 
		if t == "patch":
			path = json_data["path"]

			if "diff_base64" in json_data:
				import base64
				diff_text = base64.b64decode(json_data["diff_base64"]).decode("utf-8")
			else:
				diff_text = json_data["diff"]

			full_path = os.path.join(WORKSPACE, path)
			if not os.path.exists(full_path):
				return {"kind": "txt", "content": f"ファイルが存在しません: {path}"}

			with open(full_path, "r", encoding="utf-8") as f:
				original = f.read()

			new_content = apply_patch(original, diff_text)

			with open(full_path, "w", encoding="utf-8") as f:
				f.write(new_content)

			return {"kind": "patch", "path": path}

		#  FINISH 
		if t == "finish":
			return {"kind": "finish", "message": json_data.get("message", "done")}

		#  UNKNOWN TYPE 
		return {"kind": "txt", "content": "不明な type です。"}

	except Exception as e:
		return {
			"kind": "txt",
			"content_lines": [
				"【analog.py 内部エラー】",
				str(e)
			]
		}

def executor(json_data):
	try:
		# actions を持つ dict
		if isinstance(json_data, dict) and "actions" in json_data:
			return [_execute_one(item) for item in json_data["actions"]]

		# list の場合
		if isinstance(json_data, list):
			return [_execute_one(item) for item in json_data]

		# 単体の action
		return _execute_one(json_data)

	except Exception as e:
		# executor 自体のエラーも txt として返す
		return {
			"kind": "txt",
			"content_lines": [
				"【executor 内部エラー】",
				str(e)
			]
		}

def format_output(results):
	if not isinstance(results, list):
		results = [results]

	lines = []

	for r in results:
		k = r["kind"]

		if k == "txt":
			if "content_lines" in r:
				for line in r["content_lines"]:
					lines.append(line)
			else:
				lines.append(r["content"])

		elif k == "read_file":
			lines.append(f"📖読み込み: {r['path']} ")
			lines.append(r["content"])

		elif k == "mkdir":
			lines.append(f"📁フォルダを作成しました: {r['path']}")

		elif k == "delete_folder":
			lines.append(f"❎フォルダを削除しました: {r['path']}")

		elif k == "file":
			lines.append(f"📘ファイルを作成しました: {r['path']}\n")
			lines.append("内容：\n" + r["content"])

		elif k == "delete_file":
			lines.append(f"❎ファイルを削除しました: {r['path']}")

		elif k == "cmd":
			cmd_str = " ".join(r["cmd"])
			lines.append(f"⌨️「{cmd_str}」を実行しました。\n")
			lines.append("実行結果：\n" + r["output"])
			lines.append(f"📗ログファイル: {r['log']}")

		elif k == "patch":
			lines.append(f"🔧patch を適用しました: {r['path']}")
		
		elif k == "finish":
			lines.append(f"✅finishコマンドを受信しました。終了します。")

	return "\n".join(lines)

import re

def sanitize_json(text):
	# Markdown の自動エスケープ除去
	text = text.replace("\\_", "_")
	text = text.replace("\\#", "#")
	text = text.replace("\\!", "!")
	text = text.replace("\\:", ":")
	text = text.replace("\\-", "-")
	text = text.replace("\\<", "<")
	text = text.replace("\\>", ">")

	# JSON の文字列部分だけを抽出して改行をエスケープ
	def escape_string(match):
		s = match.group(0)
		# 先頭と末尾の " を除いて内部だけ処理
		inner = s[1:-1]
		inner = inner.replace("\r", "\\r")
		inner = inner.replace("\n", "\\n")
		inner = inner.replace("\t", "\\t")
		# 制御文字を全部エスケープ
		inner = "".join(
			c if ord(c) >= 32 else "\\u%04x" % ord(c)
			for c in inner
		)
		return '"' + inner + '"'

	# "..." の部分だけを置換
	text = re.sub(r'"(?:[^"\\]|\\.)*"', escape_string, text)

	return text

def main():
	#  ファイルパスで JSON を渡された場合 
	if len(sys.argv) == 2 and sys.argv[1].endswith(".txt"):
		with open(sys.argv[1], "r", encoding="utf-8") as f:
			json_text = f.read()

		json_text = sanitize_json(json_text)
		with open("collect_json.txt", "w", encoding="utf-8") as f:
			f.write(json_text)

		try:
			data = json.loads(json_text)
		except Exception as e:
			formatted = f"JSON パースエラー: {e}"
			output_buffer.append(formatted)
			print(formatted)
			return formatted

		result = executor(data)
		save_ai_json(data)
		formatted = format_output(result)

		result_path = os.path.join(BASE_DIR, "auto_result.txt")
		with open(result_path, "w", encoding="utf-8") as f:
			f.write(formatted)

		output_buffer.append(formatted)

		print(formatted)
		return formatted

	#  標準入力に JSON が流れてきた場合 
	if not sys.stdin.isatty():
		json_text = sys.stdin.read()
		json_text = sanitize_json(json_text)
		with open("collect_json.txt", "w", encoding="utf-8") as f:
			f.write(json_text)

		try:
			data = json.loads(json_text)
		except Exception as e:
			formatted = f"JSON パースエラー: {e}"
			output_buffer.append(formatted)
			print(formatted)
			return formatted

		result = executor(data)
		formatted = format_output(result)

		result_path = os.path.join(BASE_DIR, "auto_result.txt")
		with open(result_path, "w", encoding="utf-8") as f:
			f.write(formatted)

		output_buffer.append(formatted)

		print(formatted)
		return formatted

	#  対話モード未実装 
	formatted = "対話モードは未実装です。"
	output_buffer.append(formatted)
	print(formatted)
	return formatted

def load_prompt_for_clipboard():
	try:
		path = os.path.join(BASE_DIR, "auto.txt")
		with open(path, "r", encoding="utf-8") as f:
			prompt_text = f.read()

		output_buffer.append("===== cell-codeマニュアル =====")
		output_buffer.append(prompt_text)
		output_buffer.append("===== RESULT =====")

	except Exception as e:
		output_buffer.append(f"[auto.txt 読み込みエラー] {e}")

def flush_to_clipboard():
	if not output_buffer:
		return

	final_output = "\n".join(output_buffer)

	ps_command = f"$text = @'\n{final_output}\n'@; Set-Clipboard $text"

	subprocess.run([
		"/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
		"-Command",
		ps_command
	])

import traceback

if __name__ == "__main__":
	try:
		# まず auto.txt を読み込んでヘッダを積む
		load_prompt_for_clipboard()

		# main() を実行して実行結果を受け取る
		output = main()

		# 実行結果をバッファに積む
		if output:
			output_buffer.append(str(output))

	except Exception:
		tb = traceback.format_exc()
		output_buffer.append(tb)
		print(tb)

	# 最後にクリップボードへ送信
	flush_to_clipboard()

