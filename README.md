# 製麺管理アプリ

実際のうどん製麺で使うことを目的に開発している、Python / Flask / SQLite ベースのWebアプリです。

製麺条件・配合・小麦粉銘柄・評価を一か所に記録し、過去データを検索・比較できます。学習用サンプルで終わらせず、実際に使って感じた不便を機能追加につなげながら改善しています。

## ポートフォリオ

- ポートフォリオページ: https://mihara2140-glitch.github.io/udon-production-manager/
- 公開アプリ: https://mihara2140.pythonanywhere.com
  - 公開アプリはログイン制限を設定している場合があります。

## 主な機能

- 製麺開始
  - 日付、気温、湿度、使用する配合を記録
- 製麺終了
  - 常温・冷蔵熟成時間、茹で時間、メモを記録
  - ツル感、モチ感、コシ、のど越し、くっつき、タレとの相性を各10点で評価
  - 6項目から60点満点の総合点を自動計算
- 製麺記録一覧
  - 製麺番号、配合番号、日付などで検索
  - 状態や評価、加水率、塩分濃度などで並び替え
- 配合管理
  - 薄力粉・中力粉・強力粉、加水率、塩分濃度を保存
  - 薄力粉・強力粉を使わない配合に対応
  - 中力粉を複数銘柄組み合わせる配合に対応
- 小麦粉銘柄管理
  - 粉の種類、番号、銘柄名、特徴を登録
- AI小麦粉検索
  - 欲しい食感・特徴を自然文で入力
  - OpenAI Responses APIのWeb検索で候補を調査
  - メーカー・製粉会社など信頼できる情報を優先して比較
- ダッシュボード / データ分析
  - 作業中件数、完了件数、最近の評価推移
  - 平均・最高評価、評価項目別平均
  - 加水率別・湿度別の評価分析

## 使用技術

| 分類 | 技術 | 用途 |
| --- | --- | --- |
| Backend | Python | アプリ全体の処理 |
| Web | Flask | 画面とPython処理の接続 |
| Frontend | HTML / CSS / JavaScript | UI・スマホ対応・可変入力 |
| Database | SQLite | 製麺・配合・粉銘柄データの保存 |
| Data | pandas | データ処理・分析用 |
| Visualization | matplotlib | データ可視化用 |
| Version Control | Git / GitHub | ソースコード・変更履歴管理 |
| Hosting | PythonAnywhere | Webアプリ公開 |
| AI integration | OpenAI Responses API / Web search | 小麦粉候補の検索・比較 |

## アプリ構成

```text
udon-production-manager/
├─ web_app.py                 # Flaskアプリ・ルーティング
├─ services/                  # DB・記録・配合・AI検索などの処理
├─ web/                       # Flask用HTML/CSS
├─ screens/                   # Tkinter版の画面
├─ docs/                      # ポートフォリオページ
├─ requirements.txt
└─ DEPLOYMENT.md              # PythonAnywhere公開手順
```

## データベース

主に以下のテーブルを使用しています。

- `flours`
  - 小麦粉銘柄
- `recipes`
  - 配合番号、加水率、塩分濃度と旧画面互換用の代表値
- `recipe_flours`
  - 1つの配合で実際に使用する小麦粉と量
  - 1配合に複数の中力粉を持てるよう正規化
- `seimen_records`
  - 製麺条件、熟成時間、茹で時間、評価、メモ、状態

Ver.24では、従来の「薄力粉1・中力粉1・強力粉1」の固定構成を残しつつ、`recipe_flours` を追加しました。既存配合は起動時に自動で明細へ移行するため、過去の配合番号や製麺記録を維持したまま拡張できます。

## AI小麦粉検索の設定

AI検索を使う場合はOpenAI APIキーを環境変数に設定します。APIキーはGitHubへコミットしません。

ローカルでは `.env.example` を参考に `.env` を作成します。

```text
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-5.6-luna
```

公開先では同じ値を環境変数として設定します。

## 開発の流れ

```text
CSVで記録
    ↓
TkinterでGUI化
    ↓
SQLiteへ移行
    ↓
データ分析・可視化
    ↓
FlaskでWebアプリ化
    ↓
PythonAnywhereで公開
    ↓
配合DBの正規化・AI Web検索
```

## この開発で取り組んだこと

- Pythonの関数分割とファイル構成
- CRUD処理
- SQLiteとSQL
- 既存データを残したDBスキーマ移行
- 1対多のリレーションを使った配合設計
- Flaskのルーティング、GET / POST処理
- JavaScriptによる可変フォーム
- 入力値の検証とエラー表示
- セッションを使った簡易ログイン
- 環境変数による公開環境とローカル環境の切り替え
- Git / GitHubを使ったブランチ・Pull Request運用
- PythonAnywhereへのデプロイ
- OpenAI APIとWeb検索ツールの連携

## セキュリティ・公開時の考慮

公開環境では、パスワードや秘密鍵、DB保存先、APIキーを環境変数で設定します。

```text
APP_PASSWORD
FLASK_SECRET_KEY
UDON_DB_PATH
OPENAI_API_KEY
OPENAI_MODEL
```

実際のデータベースや秘密情報はGitHubへコミットしない構成です。

## ローカルでの起動

```bash
python -m pip install -r requirements.txt
python web_app.py
```

ブラウザで以下を開きます。

```text
http://127.0.0.1:5000
```

## 今後

- 過去の製麺データとAIを組み合わせた配合提案
- 条件と評価の関係を見つける分析強化
- 自動テスト / CI
- 初めて製麺する人でも迷わず使える初心者向け版の開発

---

このリポジトリは、Pythonを使った業務ツール・データ管理・Webアプリ開発の学習と実践を兼ねて継続的に改善しています。
