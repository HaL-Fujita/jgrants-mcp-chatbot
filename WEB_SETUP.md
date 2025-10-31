# Jグランツ補助金検索チャットシステム - セットアップガイド

Web版のJグランツ補助金検索チャットシステムのセットアップ手順です。

## システム構成

- **バックエンド**: FastAPI (Python)
- **フロントエンド**: Next.js (React + TypeScript)
- **AI**: Claude API + OpenAI API（並列処理）

## 必要な環境

- Python 3.11以上
- Node.js 18以上
- npm または yarn

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/HaL-Fujita/jgrants-mcp-chatbot.git
cd jgrants-mcp-chatbot
```

### 2. バックエンドのセットアップ

#### 2.1 依存関係のインストール

```bash
cd backend
pip install -r requirements.txt
```

#### 2.2 環境変数の設定

`.env.example`を`.env`にコピーして、APIキーを設定します：

```bash
cp .env.example .env
```

`.env`ファイルを編集：

```bash
# LLM API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
PORT=8000
HOST=0.0.0.0
```

**APIキーの取得方法:**
- Anthropic API Key: https://console.anthropic.com/
- OpenAI API Key: https://platform.openai.com/api-keys

#### 2.3 バックエンドサーバーの起動

```bash
python main.py
```

または

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

サーバーが起動したら、ブラウザで http://localhost:8000/docs にアクセスして API ドキュメントを確認できます。

### 3. フロントエンドのセットアップ

新しいターミナルウィンドウを開いて：

#### 3.1 依存関係のインストール

```bash
cd frontend
npm install
```

または

```bash
yarn install
```

#### 3.2 環境変数の設定

`.env.local.example`を`.env.local`にコピー：

```bash
cp .env.local.example .env.local
```

必要に応じて編集（デフォルトで問題ない場合はそのまま）：

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 3.3 開発サーバーの起動

```bash
npm run dev
```

または

```bash
yarn dev
```

ブラウザで http://localhost:3000 にアクセスします。

## 使い方

1. ブラウザで http://localhost:3000 を開く
2. 上部のボタンでClaudeとChatGPTの表示を切り替え可能
3. 下部の入力欄に補助金に関する質問を入力
4. 両方のAIが並列で回答を返す

### 質問の例

- 「東京都で現在募集中のIT関連の補助金を教えてください」
- 「大阪府の製造業向け補助金はありますか？」
- 「中小企業向けのDX推進補助金を探しています」

## トラブルシューティング

### バックエンドが起動しない

- Python 3.11以上がインストールされているか確認
- すべての依存パッケージがインストールされているか確認
- APIキーが正しく設定されているか確認

```bash
python --version
pip list
```

### フロントエンドが起動しない

- Node.js 18以上がインストールされているか確認
- `node_modules`を削除して再インストール

```bash
rm -rf node_modules
npm install
```

### APIエラーが発生する

- バックエンドサーバーが起動しているか確認
- `.env`ファイルのAPIキーが正しいか確認
- ブラウザのコンソールでエラーメッセージを確認

```bash
# バックエンドのヘルスチェック
curl http://localhost:8000/api/health
```

### CORSエラーが発生する

`backend/main.py`のCORS設定を確認してください：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンドのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 本番環境へのデプロイ

### バックエンド

- Railway, Render, AWS EC2などにデプロイ可能
- 環境変数を本番環境に設定
- `HOST=0.0.0.0`、`PORT`は環境に応じて設定

### フロントエンド

- Vercel（推奨）、Netlify、AWS Amplifyなどにデプロイ可能
- `NEXT_PUBLIC_API_URL`を本番バックエンドのURLに設定

```bash
# Vercelへのデプロイ例
cd frontend
npm install -g vercel
vercel
```

## 開発のヒント

### バックエンドの変更

- `backend/api/jgrants.py`: JグランツAPI連携
- `backend/api/chat.py`: LLM統合（Claude + OpenAI）
- `backend/main.py`: FastAPIルート定義

### フロントエンドの変更

- `frontend/src/components/ChatInterface.tsx`: メインのチャットUI
- `frontend/src/components/ChatMessage.tsx`: メッセージ表示
- `frontend/src/components/SubsidyCard.tsx`: 補助金カード表示
- `frontend/src/lib/api.ts`: APIクライアント

## ライセンス

MIT License

## サポート

問題が発生した場合は、GitHubのIssuesで報告してください。
