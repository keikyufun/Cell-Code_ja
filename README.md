# Cell-Code(VSCEdition)

Cell-CodeはAIをOSの一部として扱うことを目的とした自律型AI実行環境です。
依存ライブラリを排除しPowerShell・WSL・Pythonの三層構造で安定したAI制御を実現します。
本リポジトリはVisualStudioCode上で動作するCell-Codeの実装です。

## 特徴

- 依存ゼロ構造  
- PowerShell/WSL/Pythonの三位一体実行ループ  
- JSON行配列方式による壊れないデータ構造  
- 自動JSON修復エンジン  
- AIログ体系(ai_log/cmd_log)  
- finish制御による安全なループ終了  
- WSL経由のWindowsクリップボード連携  
- VisualStudioCode運用前提の構成  

## ディレクトリ構成と役割

- auto.ps1  
AI実行ループを制御するPowerShellスクリプト

- auto.txt  
AIへの入力テンプレート

- LICENSE  
プロジェクト全体のMITライセンス

- README.md  
本ドキュメント

- auto_files/  
Cell-Codeの自動処理に必要な実行ファイル群を格納するディレクトリ

- auto_files/clipboard.exe  
Windowsクリップボード操作用バイナリ

- auto_files/copy_clipboard.py  
WSL経由でWindowsクリップボードへ安全に書き込むPythonスクリプト

- auto_files/clipboard.txt  
クリップボードへ送る内容を一時保存するファイル

- sellscripts/  
補助的なシェルスクリプト群を格納するディレクトリ

- ai_log/  
AIの出力ログを保存するディレクトリ

- ai_log/ai_log/  
AI応答の生ログを保存

- ai_log/cmd_log/  
実行コマンドのログを保存

- ai-workspace/  
AIが生成したファイルや作業内容を保存するワークスペース

## 必要環境

- Windows10/11  
- WSL2(Ubuntu推奨)  
- Python3.x  
- PowerShell  
- VisualStudioCode  

## セットアップ手順

1.このリポジトリをクローンします。 
```terminal:Ubuntu
git clone https://github.com/keikyufun/Cell-Code_ja.git
```
2.WSL上でPython3が動作することを確認します。  
3.PowerShellの実行ポリシーを許可します。  
4.VisualStudioCodeでクローンしたフォルダを開きます。  
5.管理者権限のPowerSellでauto.ps1を実行するとCell-Codeが起動します。 
```terminal:PowerSell（管理者権限）
./auto.ps1
```
## 動作の仕組み

1.PowerShellがWSLとPythonを連携させAI実行ループを開始します。  
2.AIの出力はJSON行配列として保存され必要に応じて自動修復されます。  
3.WindowsクリップボードはWSL経由で安全に制御されます。  
4.finishコマンドを受信するとループが安全に終了します。  

## サードパーティコンポーネント

本プロジェクトには以下の[外部バイナリ](https://github.com/keikyufun/auto_ai_c)が含まれます。 
必ず、[https://github.com/keikyufun/auto_ai_c/blob/main/README_ja.md](https://github.com/keikyufun/auto_ai_c/blob/main/README_ja.md)をお読みください。
- clipboard.exe  
ライセンスはauto_files/clipboard_LICENSE.txtを参照してください。  

## ライセンス

本プロジェクトはMITLicenseの下で公開されています。詳細はLICENSEファイルを参照してください。
