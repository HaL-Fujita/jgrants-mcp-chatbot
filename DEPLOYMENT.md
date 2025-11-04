# デプロイ手順書

## 🚀 無料でデプロイする方法

このアプリケーションは以下の無料サービスでデプロイできます：
- **フロントエンド**: Vercel（無料）
- **バックエンド**: Render（無料）

---

## 事前準備

### 必要なアカウント
1. **GitHubアカウント**（既にある前提）
2. **Vercelアカウント**
   - https://vercel.com/signup
   - GitHubでサインアップ
3. **Renderアカウント**
   - https://render.com/register
   - GitHubでサインアップ

### APIキーの準備
- **Anthropic API Key**: https://console.anthropic.com/
- **OpenAI API Key**: https://platform.openai.com/api-keys

---

## ステップ1: GitHubへプッシュ

```bash
# リポジトリディレクトリへ移動
cd /mnt/c/Users/bestg/codes/jgrants-mcp-chatbot

# Gitユーザー設定（初回のみ）
git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"

# ステージング
git add .gitignore backend/ frontend/ render.yaml WEB_SETUP.md

# コミット
git commit -m "Add web frontend and backend with deployment configuration"

# プッシュ
git push origin main
```

---

## ステップ2: バックエンドをRenderにデプロイ

### 2-1. Renderダッシュボードへアクセス
https://dashboard.render.com/

### 2-2. New Web Service を作成
1. **「New +」** ボタン → **「Web Service」** を選択
2. **GitHubリポジトリを接続**
   - `jgrants-mcp-chatbot` リポジトリを選択
3. **設定を入力**:
   - **Name**: `jgrants-backend`（任意）
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./backend/Dockerfile`
   - **Docker Build Context Directory**: `./backend`
   - **Plan**: `Free`

### 2-3. 環境変数を設定
「Environment」タブで以下の環境変数を追加：

| Key | Value |
|-----|-------|
| `ANTHROPIC_API_KEY` | あなたのAnthropic APIキー |
| `OPENAI_API_KEY` | あなたのOpenAI APIキー |
| `PORT` | `8000` |
| `HOST` | `0.0.0.0` |
| `ALLOWED_ORIGINS` | 後で設定（VercelのURLを取得後） |

### 2-4. デプロイ開始
- **「Create Web Service」** ボタンをクリック
- デプロイ完了まで数分待つ

### 2-5. バックエンドURLを取得
- デプロイ完了後、`https://jgrants-backend-xxxx.onrender.com` のようなURLが表示される
- このURLをメモしておく

---

## ステップ3: フロントエンドをVercelにデプロイ

### 3-1. Vercelダッシュボードへアクセス
https://vercel.com/dashboard

### 3-2. New Project を作成
1. **「Add New...」** → **「Project」** を選択
2. **GitHubリポジトリをインポート**
   - `jgrants-mcp-chatbot` リポジトリを選択
3. **設定を入力**:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`（自動検出）
   - **Output Directory**: `.next`（自動検出）

### 3-3. 環境変数を設定
「Environment Variables」セクションで以下を追加：

| Name | Value | 説明 |
|------|-------|------|
| `NEXT_PUBLIC_API_URL` | RenderのバックエンドURL（例: `https://jgrants-backend-xxxx.onrender.com`） | **必須**: バックエンドAPIのURL |

**重要**: この環境変数を設定しないと、フロントエンドはlocalhostへアクセスしようとしてエラーになります。

### 3-4. デプロイ開始
- **「Deploy」** ボタンをクリック
- デプロイ完了まで数分待つ

### 3-5. フロントエンドURLを取得
- デプロイ完了後、`https://your-project-name.vercel.app` のようなURLが表示される

---

## ステップ4: CORS設定を更新

### 4-1. RenderでALLOWED_ORIGINSを更新
1. Renderダッシュボードに戻る
2. バックエンドサービスの **「Environment」** タブを開く
3. `ALLOWED_ORIGINS` 環境変数を追加/更新:
   ```
   https://your-project-name.vercel.app
   ```
4. **「Save Changes」** をクリック
5. 自動的に再デプロイされる

---

## ✅ 完了！

フロントエンドURL（`https://your-project-name.vercel.app`）にアクセスして動作確認してください。

---

## 🔧 トラブルシューティング

### バックエンドが起動しない場合
- Renderのログを確認: **「Logs」** タブ
- 環境変数が正しく設定されているか確認
- Dockerビルドが成功しているか確認

### フロントエンドでAPIエラーが出る場合

#### 1. 環境変数が設定されているか確認
Vercelダッシュボード → プロジェクト → Settings → Environment Variables で以下を確認:
- `NEXT_PUBLIC_API_URL` が設定されているか
- 値が正しいバックエンドURL（例: `https://jgrants-backend-xxxx.onrender.com`）か

#### 2. 環境変数変更後は再デプロイが必要
環境変数を追加・変更した場合:
1. Deployments タブへ移動
2. 最新のデプロイメントの「...」メニューから「Redeploy」を選択

#### 3. バックエンドの動作確認
- RenderのバックエンドURLに `/api/health` をつけてアクセス
- 例: `https://jgrants-backend-xxxx.onrender.com/api/health`
- `{"status":"healthy","api_keys":{...}}` が返ってくればOK

#### 4. CORSエラーの確認
- ブラウザの開発者ツール（F12）でConsoleタブを開く
- `Access-Control-Allow-Origin` エラーが出ている場合:
  - Renderのバックエンドで `ALLOWED_ORIGINS` 環境変数を確認
  - VercelのフロントエンドURL（例: `https://your-app.vercel.app`）が含まれているか確認
  - または `ALLOWED_ORIGINS` を `*` に設定（開発時のみ推奨）

### Renderの無料プランの制限
- **15分間アクセスがないとスリープ**
  - 次回アクセス時に数秒の起動時間がかかる
  - 本番運用には有料プラン（$7/月）を推奨

---

## 📊 運用コスト

| サービス | プラン | 月額 |
|---------|-------|------|
| Vercel | Free | $0 |
| Render | Free | $0 |
| **合計** | | **$0** |

**制限**:
- Vercel: 月100GB帯域幅、100GBビルド時間
- Render: 750時間/月（常時稼働可能）、15分でスリープ

---

## 🔐 セキュリティ

### APIキーの管理
- **絶対にGitHubにコミットしない**
- `.env` ファイルは `.gitignore` に含まれている
- Render/Vercelの環境変数機能を使用する

### 本番環境での推奨事項
- APIレート制限の実装
- 認証機能の追加
- ログ監視の設定

---

## 📝 更新方法

コードを更新してGitHubにプッシュすると、Vercel/Renderが自動的に再デプロイします：

```bash
git add .
git commit -m "Update feature"
git push origin main
```

- **Vercel**: 自動デプロイ（約1-2分）
- **Render**: 自動デプロイ（約3-5分）

---

## 🚨 Vercelデプロイエラー対処法

### エラー: "API connection failed" / "localhost:8000" にアクセスしようとする

**原因**: `NEXT_PUBLIC_API_URL` 環境変数が未設定

**解決方法**:
1. Vercelダッシュボードを開く: https://vercel.com/dashboard
2. プロジェクトを選択
3. **Settings** → **Environment Variables** へ移動
4. 以下を追加:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://jgrants-backend-xxxx.onrender.com`（あなたのRender URL）
   - **Target**: Production, Preview, Development すべて選択
5. **Save** をクリック
6. **Deployments** タブへ移動
7. 最新デプロイメントを **Redeploy** する

### エラー: "CORS policy" / "Access-Control-Allow-Origin"

**原因**: バックエンドがVercelからのアクセスを許可していない

**解決方法**:
1. Renderダッシュボードを開く: https://dashboard.render.com/
2. バックエンドサービスを選択
3. **Environment** タブへ移動
4. `ALLOWED_ORIGINS` を追加/更新:
   - **Key**: `ALLOWED_ORIGINS`
   - **Value**: `https://your-app.vercel.app` または `*`（開発時）
5. **Save Changes** をクリック（自動的に再デプロイされる）

### デプロイIDが表示される場合の確認方法

デプロイID（例: `hnd1::bzd2c-...`）が表示された場合:

1. Vercelダッシュボードで **Deployments** タブを開く
2. 該当するデプロイメントをクリック
3. **Build Logs** でエラー内容を確認
4. **Function Logs** でランタイムエラーを確認

よくある問題:
- ビルドは成功するがランタイムで動作しない → 環境変数が未設定
- CORS エラー → バックエンドの `ALLOWED_ORIGINS` を確認
- 502 Bad Gateway → バックエンドがスリープ中（Renderの無料プラン）または起動失敗
