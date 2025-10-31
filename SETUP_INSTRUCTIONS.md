# セットアップ手順

## 設定ファイルの配置方法

### Claude Desktopの場合

1. Claude Desktopがインストールされていることを確認
2. 設定ディレクトリを作成（存在しない場合）：

```bash
mkdir -p ~/Library/Application\ Support/Claude/
```

3. 設定ファイルをコピー：

```bash
cp /Users/apple/jgrants-mcp-chatbot/claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

4. Claude Desktopを再起動

### Claude Codeの場合

1. VSCodeでClaude Code拡張機能がインストールされていることを確認
2. 設定ディレクトリを作成（存在しない場合）：

```bash
mkdir -p ~/Library/Application\ Support/Code/User/globalStorage/anthropic.claude-code/settings/
```

3. 設定ファイルをコピー：

```bash
cp /Users/apple/jgrants-mcp-chatbot/mcp_settings.json ~/Library/Application\ Support/Code/User/globalStorage/anthropic.claude-code/settings/mcp_settings.json
```

4. VSCodeを再起動

## 既存の設定ファイルがある場合

既に設定ファイルが存在する場合は、以下の内容を既存のファイルの `mcpServers` セクションに追加してください：

```json
"jgrants": {
  "command": "/usr/local/bin/python3.11",
  "args": [
    "/Users/apple/jgrants-mcp-chatbot/jgrants_server.py"
  ]
}
```

例：

```json
{
  "mcpServers": {
    "existing-server": {
      ...
    },
    "jgrants": {
      "command": "/usr/local/bin/python3.11",
      "args": [
        "/Users/apple/jgrants-mcp-chatbot/jgrants_server.py"
      ]
    }
  }
}
```

## 動作確認

設定後、Claude DesktopまたはClaude Codeで以下のような質問をしてみてください：

- 「東京都で現在募集中の補助金を教えてください」
- 「IT導入に関する補助金を探しています」
- 「中小企業向けのDX推進補助金はありますか？」

## トラブルシューティング

### MCPサーバーが認識されない場合

1. Python 3.11のパスを確認：

```bash
which python3.11
```

2. パスが `/usr/local/bin/python3.11` と異なる場合は、設定ファイル内の `command` を実際のパスに変更してください

3. スクリプトが実行可能であることを確認：

```bash
chmod +x /Users/apple/jgrants-mcp-chatbot/jgrants_server.py
```

4. 依存パッケージがインストールされていることを確認：

```bash
pip3.11 install -r /Users/apple/jgrants-mcp-chatbot/requirements.txt
```

### 手動でテスト実行

MCPサーバーが正常に動作するか直接テストする場合：

```bash
python3.11 /Users/apple/jgrants-mcp-chatbot/test_api.py
```

成功すれば、JグランツAPIから補助金情報が取得できます。
