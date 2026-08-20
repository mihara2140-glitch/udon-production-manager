# 製麺管理アプリ Web公開メモ

## 現在の構成

- Flask: Web画面とPython処理の接続
- SQLite: 製麺・配合・粉銘柄データ
- Gunicorn: 公開サーバーでFlaskを動かすためのWSGIサーバー
- APP_PASSWORD: 公開時の簡易ログイン
- FLASK_SECRET_KEY: ログイン状態を安全に管理するための秘密鍵
- UDON_DB_PATH: 公開先でSQLiteの保存場所を切り替える設定

## 公開前に必ず設定するもの

実際の値はGitHubへ書かず、公開サービス側の環境変数・設定画面に入れる。

- `APP_PASSWORD`: 自分だけが知っているログイン用パスワード
- `FLASK_SECRET_KEY`: 長いランダム文字列
- `COOKIE_SECURE=1`: HTTPS公開時にCookieをHTTPSだけで送る
- `UDON_DB_PATH`: SQLiteを永続保存できる場所

`.env.example` は設定例だけで、実際の秘密情報は入れない。

## 最初の公開候補

### PythonAnywhere

現在のSQLite構成を大きく変えずに公開する第一候補。

大まかな流れ:

1. PythonAnywhereのアカウントを作る
2. BashコンソールからGitHubリポジトリを取得する
3. `pip install -r requirements.txt` で必要ライブラリを入れる
4. Web AppをFlaskとして作成する
5. WSGI設定から `web_app.app` を読み込む
6. 公開先で `APP_PASSWORD`、`FLASK_SECRET_KEY`、`UDON_DB_PATH` を設定する
7. ReloadしてURLから確認する
8. PCとスマホの両方でログイン・保存・再表示を確認する

### Renderなどの一般的なホスティング

`Procfile` の `gunicorn web_app:app` で起動できる準備は済んでいる。
ただしSQLiteを使う場合、公開先のファイルシステムが再起動で消えないか必ず確認する。
永続ディスクがないサービスではSQLiteの製麺データ保存には使わない。

## 公開時の確認チェック

- ログインしないと製麺データが見られない
- 製麺開始が保存できる
- 製麺終了・評価が保存できる
- ページ再読み込み後も記録が残る
- サーバー再起動後も記録が残る
- スマホから画面が崩れず操作できる
- GitHubに `data/`、SQLite DB、パスワードが入っていない

## 将来

利用者が増える、複数端末から同時に大量更新する、一般向けサービスにする段階になったら、SQLiteからPostgreSQLなどのサーバー型DBへの移行を検討する。
