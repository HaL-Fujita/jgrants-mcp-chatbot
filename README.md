# Jグランツ補助金検索 MCPサーバー

デジタル庁が運営する補助金電子申請システム「Jグランツ」のAPIをMCP（Model Context Protocol）経由で利用できるようにするサーバーです。Claude DesktopやClaude Codeなどのクライアントから、補助金情報を自然言語で検索・取得できます。

## 機能

このMCPサーバーは以下の3つのツールを提供します：

1. **search_subsidies** - 補助金を検索
   - キーワード検索
   - 募集中のみフィルタリング
   - 地域で絞り込み
   - ソート順の指定

2. **get_subsidy_detail** - 補助金の詳細情報を取得
   - 補助率
   - 概要
   - 注意事項
   - 申請様式の有無

3. **search_active_subsidies** - 現在募集中の補助金を検索（便利関数）
   - 申請期限が近い順に表示

## 必要要件

- Python 3.11以上
- pip

## インストール

1. 依存パッケージをインストール：

```bash
pip3.11 install -r requirements.txt
```

## 使い方

### Claude Desktopでの設定

Claude Desktopの設定ファイル (`~/Library/Application Support/Claude/claude_desktop_config.json`) に以下を追加：

```json
{
  "mcpServers": {
    "jgrants": {
      "command": "/usr/local/bin/python3.11",
      "args": [
        "/Users/apple/jgrants-mcp-chatbot/jgrants_server.py"
      ]
    }
  }
}
```

### Claude Codeでの設定

Claude Codeの設定ファイル (`~/Library/Application Support/Code/User/globalStorage/anthropic.claude-code/settings/mcp_settings.json`) に以下を追加：

```json
{
  "mcpServers": {
    "jgrants": {
      "command": "/usr/local/bin/python3.11",
      "args": [
        "/Users/apple/jgrants-mcp-chatbot/jgrants_server.py"
      ]
    }
  }
}
```

設定後、Claude Desktop/Claude Codeを再起動してください。

## 使用例

### 例1: 東京都の募集中の補助金を検索

```
東京都で現在募集中の中小企業向け補助金を教えてください
```

### 例2: IT関連の補助金を検索

```
IT導入やDX推進に関する補助金を探しています
```

### 例3: 詳細情報の取得

```
補助金ID「xxxx」の詳細情報を教えてください
```

## ツールの仕様

### search_subsidies

**パラメータ:**
- `keyword` (必須): 検索キーワード（2～255文字）
- `acceptance` (オプション): 募集中フィルタ（1: 募集中のみ, 0: 全て）
- `target_area` (オプション): 対象地域（例: 東京都、大阪府など）
- `sort` (オプション): ソート項目（created_date, acceptance_start_datetime, acceptance_end_datetime）
- `order` (オプション): ソート順（ASC, DESC）

**戻り値:**
```json
{
  "success": true,
  "count": 10,
  "subsidies": [
    {
      "id": "...",
      "name": "...",
      "title": "...",
      "target_area": "...",
      "subsidy_max_limit": "...",
      "acceptance_start": "...",
      "acceptance_end": "...",
      "target_employees": "..."
    }
  ]
}
```

### get_subsidy_detail

**パラメータ:**
- `subsidy_id` (必須): 補助金ID

**戻り値:**
```json
{
  "success": true,
  "subsidy": {
    "id": "...",
    "name": "...",
    "title": "...",
    "subsidy_rate": "...",
    "outline": "...",
    "purpose": "...",
    "note": "...",
    "grant_guideline_url": "..."
  }
}
```

### search_active_subsidies

**パラメータ:**
- `keyword` (必須): 検索キーワード
- `target_area` (オプション): 対象地域

**戻り値:**
search_subsidiesと同じ形式で、募集中の補助金が申請期限が近い順に返されます

## トラブルシューティング

### Python 3.11が見つからない

Homebrewでインストールしてください：

```bash
brew install python@3.11
```

### パッケージのインストールエラー

pip を最新版にアップグレードしてください：

```bash
pip3.11 install --upgrade pip
pip3.11 install -r requirements.txt
```

### MCPサーバーが起動しない

1. Python 3.11が正しくインストールされているか確認
2. 依存パッケージがすべてインストールされているか確認
3. 設定ファイルのパスが正しいか確認

## 参考リンク

- [JグランツAPI公式ドキュメント](https://developers.digital.go.jp/documents/jgrants/api/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [デジタル庁によるMCP実装例](https://digital-gov.note.jp/n/n09dfb9fa4e8e)

## ライセンス

MIT License

## 作成者

このプロジェクトは、デジタル庁の公開APIとMCP標準を活用して作成されました。
