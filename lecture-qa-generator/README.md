# 講義内容の確認QAの作成システム

プロジェクトの詳細は、所定のドキュメントを確認すること。

### アーキテクチャ構成
- **バックエンド**: FastAPI + SQLAlchemy
- **LLM連携**: LangChain + Google Gemini API
- **データベース**: SQLite（開発用）/ PostgreSQL（本番用）
- **フロントエンド**: FastAPI + Jinja2テンプレート
- **コンテンツ抽出**: python-pptx（PowerPointファイル処理）

### 実装タスク一覧

#### 高優先度タスク
1. **プロジェクト構成とアーキテクチャ設計**
   - ディレクトリ構造の設定
   - 基本的な設定ファイルの作成

2. **PPTXファイルからのコンテンツ抽出機能の実装**
   - python-pptxを使用してPowerPointからテキスト抽出
   - スライド構造の解析と内容の構造化

3. **LLMを使用したQA自動生成機能の実装**
   - LangChainとGoogle Gemini APIの統合
   - プロンプトテンプレートの設計
   - 選択式・記述式の質問生成ロジック

4. **難易度調整機能の実装**
   - プロンプトエンジニアリングによる難易度制御
   - 難易度別の質問生成パラメータ調整

#### 中優先度タスク
5. **QA管理用のデータベース設計と実装**
   - テーブル設計（質問、回答、学生回答記録等）
   - SQLAlchemyモデルの実装
   - マイグレーション設定

6. **WebUIの実装（QA管理インターフェース）**
   - FastAPIでのAPI実装
   - 管理画面の作成
   - QAの作成・編集・削除機能

7. **学生理解度分析・可視化機能の実装**
   - 回答データの集計・分析ロジック
   - Plotlyを使用したダッシュボード作成
   - リアルタイム更新機能

#### 低優先度タスク
8. **改善提案機能の実装**
   - 分析結果に基づく改善点の自動抽出
   - LLMを活用した提案文生成

### 技術スタック詳細
- **Python 3.13**: メイン開発言語
- **FastAPI**: RESTful API開発
- **LangChain**: LLM統合フレームワーク
- **Google Gemini API**: 質問生成エンジン
- **SQLAlchemy**: ORM
- **Plotly**: データ可視化
- **python-pptx**: PowerPointファイル処理

### 開発環境セットアップ

#### 1. Google Gemini APIキーの取得
1. [Google AI Studio](https://aistudio.google.com/app/apikey) にアクセス
2. Googleアカウントでログイン
3. 「Create API Key」をクリックしてAPIキーを生成
4. APIキーをコピーして保存

#### 2. 環境設定
```bash
# 仮想環境の作成
python -m venv .venv

# 仮想環境の有効化
source .venv/bin/activate  # Mac/Linux
# または
.venv\Scripts\activate  # Windows

# 依存関係のインストール
pip install -r requirements.txt

# 環境変数ファイルの設定
cp .env.example .env
# .envファイルを編集してGOOGLE_API_KEYを設定
```

#### 3. 起動
```bash
# サーバー起動
python main.py

# ブラウザで http://localhost:8000 にアクセス
```

## 7. 実装結果・成果

### 実装成果

#### 生成品質の検証結果
- **処理対象**: 10スライド（全103スライド中）から16問の高品質な問題を生成
- **生成効率**: スライドあたり平均1.6問、処理時間約2分
- **質問の多様性**: 
  - 選択式（multiple_choice）: 13問
  - 記述式（essay）: 2問
  - 短答式（short_answer）: 1問
- **難易度分布**: 
  - 基礎レベル（easy）: 7問
  - 中級レベル（medium）: 8問
  - 上級レベル（hard）: 1問

#### 技術的改善点

**1. 柔軟なJSON解析システム**
- Gemini API特有のレスポンス形式に対応
- 4つのパターンでJSON抽出を実現:
  - ```json...``` ブロック形式
  - 汎用 ```...``` ブロック形式
  - 直接 {...} オブジェクト抽出
  - 全体テキストとしてのJSON判定

**2. プロンプト最適化**
- システムメッセージの明確化
- JSON形式での出力指示の強化
- 難易度別の質問生成指示の詳細化

**3. 処理負荷の軽減**
- スライド処理上限: 10枚（`MAX_SLIDES_FOR_QA=10`）
- スライドあたり質問数: 1問（`QA_PER_SLIDE=1`）
- 大量スライド処理時のタイムアウト対策

#### 生成品質の具体例

**基礎レベル（Easy）の質問例**:

**質問1** [短答式]
> **Q**: 「Attention is All You Need」論文で提案されたモデルの中心となる機構は何ですか？  
> **正解**: Self-Attention  
> **解説**: 2017年の論文「Attention is All You Need」で提案されたTransformerモデルの中核となる機構はSelf-Attentionです。  
> **キーワード**: Transformer, Self-Attention, 論文

**質問2** [4択選択式]
> **Q**: ニューラル言語モデルの学習において、尤度を最大化するために用いられる手法はどれですか？  
> **選択肢**: 1) 勾配降下法  2) 誤差逆伝播法  3) 確率的勾配降下法  4) Adam最適化  
> **正解**: 誤差逆伝播法  
> **解説**: ニューラル言語モデルは、尤度を最大化するように誤差逆伝播法を用いて訓練されます。これにより、モデルのパラメータが最適化されます。  
> **キーワード**: ニューラル言語モデル, 尤度最大化, 誤差逆伝播法

**各質問の構成要素**:
- 明確で具体的な質問文
- 紛らわしい選択肢を含む4択（選択式の場合）
- 詳細で教育的な解説
- 関連キーワードの整理

### アーキテクチャの完成

#### 実装済み主要コンポーネント
- **PPTXExtractor**: PowerPoint content extraction service
- **QAGenerator**: Google Gemini-based question generation
- **DifficultyAdjuster**: Prompt-based difficulty control
- **FastAPI REST API**: Complete lecture and question management
- **SQLAlchemy Models**: Database schema for lectures, questions, answers
- **Web Interface**: Bootstrap-based management dashboard

#### 技術スタック確定
- **Python 3.13** + **FastAPI** (RESTful API)
- **Google Gemini API (gemini-1.5-flash)** (Question generation)
- **LangChain** (LLM integration framework)
- **SQLAlchemy** + **SQLite** (Data persistence)
- **python-pptx** (PowerPoint processing)
- **Bootstrap 5** + **Jinja2** (Web interface)

### 今後の展開可能性

#### 実装済み基盤
✅ **QA自動生成機能**: 講義資料からの自動質問生成  
✅ **難易度調整機能**: 3段階の難易度制御  
✅ **QA管理機能**: Web インターフェースでの管理  
✅ **ファイル処理**: PowerPoint ファイルのアップロードと解析  

#### 今後実装可能な機能
🔄 **学生理解度分析・可視化機能**: Plotlyダッシュボード  
🔄 **改善提案機能**: LLM活用の講義改善提案  