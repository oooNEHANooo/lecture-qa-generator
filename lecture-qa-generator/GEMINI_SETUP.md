# Google Gemini API セットアップガイド

## 概要

このQAシステムはGoogle Gemini APIを使用してPowerPointファイルから自動的に質問を生成します。
実際に使用するには、Google AI StudioからAPIキーを取得する必要があります。

## セットアップ手順

### 1. Google AI Studio アカウント設定

1. [Google AI Studio](https://aistudio.google.com/app/apikey) にアクセス
2. Googleアカウントでログイン（Googleアカウントが必要）
3. 利用規約に同意

### 2. APIキーの生成

1. 左サイドバーの「Get API key」をクリック
2. 「Create API key」ボタンをクリック
3. プロジェクトを選択（新規プロジェクトでも既存プロジェクトでも可）
4. 生成されたAPIキーをコピーして安全な場所に保存

### 3. 環境変数の設定

`.env`ファイルを編集してAPIキーを設定：

```bash
# .envファイルを編集
nano .env
```

```env
# Google Gemini API設定
GOOGLE_API_KEY=あなたのAPIキーをここに貼り付け
GEMINI_MODEL=gemini-1.5-flash

# その他の設定は変更不要
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000
```

### 4. 動作確認

```bash
# システムのテスト実行
python test_system.py
```

成功すると以下のようなメッセージが表示されます：
```
=== PowerPoint抽出機能のテスト開始 ===
=== QA生成機能のテスト開始 ===
QA生成対象スライド数: 3
生成されたQAセット数: 3
```

## 利用可能なGeminiモデル

- **gemini-1.5-flash** (推奨): 高速で効率的、ほとんどのタスクに適している
- **gemini-1.5-pro**: より高品質だが応答が少し遅い
- **gemini-1.0-pro**: 基本的なタスクに適している

モデルを変更する場合は、`.env`ファイルの`GEMINI_MODEL`を編集してください。

## APIキー利用料金

- Google Gemini APIは一定の無料枠があります
- 詳細な料金については[Google AI Studio料金ページ](https://ai.google.dev/pricing)を確認してください
- 一般的な使用パターンでは無料枠内で収まることが多いです

## トラブルシューティング

### APIキーエラー
```
GOOGLE_API_KEYが設定されていません
```
→ `.env`ファイルにAPIキーが正しく設定されているか確認

### API接続エラー
```
Failed to connect to Gemini API
```
→ インターネット接続とAPIキーの有効性を確認

### 質問生成エラー
```
QA生成エラー
```
→ PowerPointファイルの内容が適切か、APIの利用制限に達していないか確認

## セキュリティ注意事項

1. **APIキーの管理**
   - APIキーは絶対に公開リポジトリにコミットしない
   - `.env`ファイルは`.gitignore`に含まれています
   - APIキーを他人と共有しない

2. **アクセス制限**
   - 必要に応じてAPIキーにIPアドレス制限を設定
   - 定期的にAPIキーをローテーション

## 使用例

APIキーを設定後、以下の手順でシステムを使用できます：

1. サーバー起動: `python main.py`
2. ブラウザで http://localhost:8000 にアクセス
3. PowerPointファイルをアップロード
4. 自動生成された質問を確認

## サポート

問題が発生した場合は、以下を確認してください：

1. APIキーが正しく設定されているか
2. インターネット接続が有効か
3. PowerPointファイルが有効な形式か
4. Gemini APIの利用制限に達していないか

詳細なエラーログは`python main.py`の出力で確認できます。