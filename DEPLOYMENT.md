# 製麺管理アプリ Web公開メモ

## 目標

PC内の `127.0.0.1:5000` ではなく、スマホからも開ける
`https://<username>.pythonanywhere.com` のURLで製麺管理アプリを使えるようにする。

## 現在の構成

- Flask: Web画面とPython処理の接続
- SQLite: 製麺・配合・粉銘柄データ
- APP_PASSWORD: 公開時の簡易ログイン
- FLASK_SECRET_KEY: ログイン状態を安全に管理する秘密鍵
- UDON_DB_PATH: 公開先でSQLiteの保存場所を切り替える設定
- GitHub: コードだけを管理。`data/` とDBは公開しない

## PythonAnywhereを最初の公開先にする理由

現在のSQLite構成を大きく変えずに公開できるため。
無料アカウントでもWebアプリ1つとSQLiteを置けるファイル領域が使える。

> 注意: 無料Webアプリには有効期限があり、継続利用時はPythonAnywhere側で定期的に延長操作が必要。

## 1. PythonAnywhereでBeginnerアカウントを作成

PythonAnywhereにログインしたら、ユーザー名を控える。
このユーザー名が公開URLにも使われる。

例:

```text
https://myusername.pythonanywhere.com
```

## 2. GitHubからコードを取得

PythonAnywhereの `Consoles` → `Bash` を開いて実行する。

```bash
git clone https://github.com/mihara2140-glitch/udon-production-manager.git
cd udon-production-manager
```

更新時は以後このフォルダで:

```bash
git pull
```

## 3. 必要ライブラリを入れる

Bashコンソールで:

```bash
python -m pip install --user -r requirements.txt
```

## 4. SQLiteの実データをアップロード

GitHubには実データを置かない。
PC側の製麺管理アプリにある:

```text
data/udon_manager.db
```

をPythonAnywhereの `Files` 画面から、次の場所へアップロードする。

```text
/home/<username>/udon-production-manager/data/udon_manager.db
```

`data` フォルダが無ければFiles画面またはBashで作る。

```bash
mkdir -p ~/udon-production-manager/data
```

## 5. Web Appを作成

PythonAnywhereの `Web` タブから `Add a new web app` を選択する。
Flaskを選ぶか、Manual configurationでWSGIアプリを作成する。

PythonAnywhereが作ったWSGI configuration fileを開き、
リポジトリにある `pythonanywhere_wsgi.py.example` を参考に設定する。

必ず次の3か所を自分用に変更する。

```python
project_home = "/home/YOUR_USERNAME/udon-production-manager"
os.environ["APP_PASSWORD"] = "自分だけのパスワード"
os.environ["FLASK_SECRET_KEY"] = "長いランダム文字列"
```

`UDON_DB_PATH` は次を指定する。

```python
os.environ["UDON_DB_PATH"] = f"{project_home}/data/udon_manager.db"
```

最後は:

```python
from web_app import app as application
```

## 6. WebタブでReload

WSGIを保存後、Webタブの `Reload` を押す。

その後:

```text
https://<username>.pythonanywhere.com
```

をPCとスマホの両方で開く。

## 7. スマホで確認

1. ログイン画面が出る
2. APP_PASSWORDでログインできる
3. ダッシュボードが表示される
4. 製麺開始を保存できる
5. 製麺終了・評価を保存できる
6. 製麺記録を検索できる
7. 配合・粉銘柄を確認できる
8. ページ再読み込み後もデータが残る

## 更新方法

コード変更後、PythonAnywhereのBashで:

```bash
cd ~/udon-production-manager
git pull
```

その後Webタブで `Reload`。

DBはGitHub管理外なので、コード更新で製麺記録が消えることはない。

## 公開時の安全確認

- `APP_PASSWORD` を必ず設定する
- `FLASK_SECRET_KEY` をGitHubへ書かない
- `data/` や `.db` をGitHubへ追加しない
- `.env` をGitHubへ追加しない
- ログインせず製麺データが表示されないことを確認する

## SQLiteについて

個人で1人が製麺記録を入力する現在の用途なら、まずSQLiteで公開を体験する。
利用者増加・複数人の同時更新・本格サービス化の段階ではPostgreSQLなどへ移行する。
