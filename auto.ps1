$BASE_WIN  = $PSScriptRoot
$BASE_LINUX = "/mnt/c" + $BASE_WIN.Substring(2).Replace("\","/")

$SCRIPT_DIR_LINUX = "$BASE_LINUX/sellscripts"
$FILES_DIR_WIN    = "$BASE_WIN/auto_files"
$MYFILE_WIN       = "$FILES_DIR_WIN/myfile.txt"

# 1. ゴール入力（WSL）
wsl bash "$SCRIPT_DIR_LINUX/step1_prompt.sh"

# 2. 1回目
wsl python3 "$BASE_LINUX/auto_files/copy_clipboard.py"
Start-Sleep -Milliseconds 100

Start-Process "$FILES_DIR_WIN/clipboard.exe" -Wait

while (!(Test-Path $MYFILE_WIN)) { Start-Sleep -Milliseconds 200 }

wsl bash "$SCRIPT_DIR_LINUX/deepthink_cut.sh"
wsl bash "$SCRIPT_DIR_LINUX/run_auto_py.sh"

# 3. FINISH までループ
while (-not (wsl bash "$SCRIPT_DIR_LINUX/finish_check.sh")) {

    if (Test-Path $MYFILE_WIN) { Remove-Item $MYFILE_WIN }

    Start-Process "$FILES_DIR_WIN/clipboard.exe" -Wait

    while (!(Test-Path $MYFILE_WIN)) { Start-Sleep -Milliseconds 200 }

    wsl bash "$SCRIPT_DIR_LINUX/deepthink_cut.sh"
    wsl bash "$SCRIPT_DIR_LINUX/run_auto_py.sh"
    Start-Sleep -Milliseconds 3000
    $resultText = Get-Content "$BASE_WIN/auto_result.txt" -Raw
    if ($resultText.Length -gt 10000) {
        # 「続けて」をクリップボードに入れる
        Set-Content "$FILES_DIR_WIN/clipboard.txt" "続けて" -Encoding UTF8

        # WSL → Windows クリップボードへコピー
        wsl python3 "$BASE_LINUX/auto_files/copy_clipboard.py"

        continue
    }
}

# 4. README 生成
wsl bash "$SCRIPT_DIR_LINUX/readme_request.sh"

Write-Host ""
Write-Host "[info] finish"