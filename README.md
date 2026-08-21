# 製麺管理アプリ

実際のうどん製麺で使うことを目的に開発している、Python / Flask / SQLite ベースのWebアプリです。

製麺条件・配合・小麦粉銘柄・評価を一か所に記録し、過去データを検索・比較できるようにしています。学習用のサンプルだけで終わらせず、実際に使って感じた不便を機能追加につなげながら改善しています。

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
  - 薄力粉・中力粉・強力粉の配合量、加水率、塩分濃度を保存
- 小麦粉銘柄管理
  - 粉の種類、番号、銘柄名、特徴を登録
- ダッシュボード
  - 作業中件数、完了件数、最新評価、最近の記録、評価推移を表示
- AI小麦粉検索の準備
  - OpenAI APIを利用したWeb検索機能を組み込める構成
  - 現在はAPIキー未設定のため無効化

## 使用技術

| 分類 | 技術 | 用途 |
| --- | --- | --- |
| Backend | Python | アプリ全体の処理 |
| Web | Flask | 画面とPython処理の接続 |
| Frontend | HTML / CSS | UI・スマホ対応 |
| Database | SQLite | 製麺・配合・粉銘柄データの保存 |
| Data | pandas | データ処理・分析用 |
| Visualization | matplotlib | データ可視化用 |
| Version Control | Git / GitHub | ソースコード・変更履歴管理 |
| Hosting | PythonAnywhere | Webアプリ公開 |
| AI integration | OpenAI API | 小麦粉検索機能の拡張用 |

## アプリ構成

```text
udon-production-manager/
├─ web_app.py                 # Flaskアプリ・ルーティング
├─ services/                  # DB・記録・配合などの処理
├─ web/                       # Flask用HTML/CSS
├─ screens/                   # Tkinter版の画面
├─ docs/                      # ポートフォリオページ
├─ requirements.txt
└─ DEPLOYMENT.md              # PythonAnywhere公開手順
```

Web版では、画面表示やHTTPリクエストを `web_app.py` が担当し、SQLiteへのアクセスや記録処理を `services` に分けています。

## データベース

主に以下のテーブルを使用しています。

- `flours`
  - 小麦粉銘柄
- `recipes`
  - 粉配合、加水率、塩分濃度
- `seimen_records`
  - 製麺条件、熟成時間、茹で時間、評価、メモ、状態

以前はCSVで管理していましたが、検索・更新・データ同士の関連付けをしやすくするためSQLiteへ移行しました。

## 開発の流れ

このアプリは次の順番で発展させています。

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
```

最初から完成形を作るのではなく、実際の製麺で使いながら「入力しづらい」「過去記録を探しづらい」「結果を比較したい」といった問題を見つけ、その都度改善しています。

## この開発で取り組んだこと

- Pythonの関数分割とファイル構成
- CRUD処理
- SQLiteとSQL
- Flaskのルーティング、GET / POST処理
- 入力値の検証とエラー表示
- セッションを使った簡易ログイン
- 環境変数による公開環境とローカル環境の切り替え
- Git / GitHubを使ったブランチ・Pull Request運用
- PythonAnywhereへのデプロイ
- 外部APIを追加できる構成

## セキュリティ・公開時の考慮

公開環境では、パスワードや秘密鍵、DB保存先などを環境変数で設定できるようにしています。

```text
APP_PASSWORD
FLASK_SECRET_KEY
UDON_DB_PATH
OPENAI_API_KEY
```

実際のデータベースや秘密情報はGitHubへコミットしない構成にしています。

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

- 蓄積した製麺データの分析強化
- 条件と評価の関係を見つける機能
- AI検索と自分の製麺データを組み合わせた小麦粉・配合提案
- 実際の使用を通したUI改善

---

このリポジトリは、Pythonを使った業務ツール・データ管理・Webアプリ開発の学習と実践を兼ねて継続的に改善しています。
