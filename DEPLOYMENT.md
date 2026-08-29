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
- OPENAI_API_KEY: AI小麦粉検索を実行するための秘密情報
- OPENAI_MODEL: AI検索で使うモデル。既定は `gpt-5.6-luna`
- GitHub: コードだけを管理。`data/` とDB、秘密情報は公開しない

## 1. PythonAnywhereでアカウントを作成

PythonAnywhereにログインしたら、ユーザー名を控える。

```text
https://myusername.pythonanywhere.com
```

## 2. GitHubからコードを取得

PythonAnywhereの `Consoles` → `Bash` を開いて実行する。

```bash
git clone https://github.com/mihara2140-glitch/udon-production-manager.git
cd udon-production-manager
```

更新時は:

```bash
cd ~/udon-production-manager
git pull
```

## 3. 必要ライブラリを入れる

```bash
python -m pip install --user -r requirements.txt
```

AI検索では `openai` と `python-dotenv` も `requirements.txt` から入る。

## 4. SQLiteの実データをアップロード

GitHubには実データを置かない。PC側の:

```text
data/udon_manager.db
```

をPythonAnywhereの次の場所へ置く。

```text
/home/<username>/udon-production-manager/data/udon_manager.db
```

必要ならフォルダを作成する。

```bash
mkdir -p ~/udon-production-manager/data
```

Ver.24以降を初めて起動すると、既存DBに `recipe_flours` テーブルが自動追加される。既存の配合番号・製麺記録はそのまま維持される。

## 5. Web Appを作成

PythonAnywhereの `Web` タブからWebアプリを作成する。

WSGI configuration fileを開き、リポジトリの `pythonanywhere_wsgi.py.example` を参考に設定する。

```python
project_home = "/home/YOUR_USERNAME/udon-production-manager"
os.environ["APP_PASSWORD"] = "自分だけのパスワード"
os.environ["FLASK_SECRET_KEY"] = "長いランダム文字列"
os.environ["UDON_DB_PATH"] = f"{project_home}/data/udon_manager.db"
```

最後は:

```python
from web_app import app as application
```

## 6. AI小麦粉検索を有効にする

AI検索を使う場合だけ、PythonAnywhereのWSGI設定など公開されない場所に次を追加する。

```python
os.environ["OPENAI_API_KEY"] = "自分のOpenAI APIキー"
os.environ["OPENAI_MODEL"] = "gpt-5.6-luna"
```

APIキーはGitHubのソースコード、README、`.env.example` の実値として書かない。

AI検索を使わない場合は `OPENAI_API_KEY` を設定しなくても、製麺記録・配合管理など他の機能は利用できる。

## 7. WebタブでReload

WSGIを保存後、Webタブの `Reload` を押す。

```text
https://<username>.pythonanywhere.com
```

をPCとスマホの両方で開く。

## 8. 公開後の確認

1. ログイン画面が出る
2. APP_PASSWORDでログインできる
3. ダッシュボードが表示される
4. 製麺開始を保存できる
5. 製麺終了・評価を保存できる
6. 製麺記録を検索できる
7. 薄力粉・強力粉なしの配合を登録できる
8. 中力粉を2種類以上追加した配合を登録できる
9. 既存配合・既存製麺記録が残っている
10. OPENAI_API_KEY設定時にAI粉検索が動く
11. ページ再読み込み後もデータが残る

## 更新方法

コード変更後、PythonAnywhereのBashで:

```bash
cd ~/udon-production-manager
git pull
python -m pip install --user -r requirements.txt
```

依存ライブラリが増えていない更新なら `pip install` は省略できる。

その後Webタブで `Reload`。

DBはGitHub管理外なので、通常のコード更新で製麺記録が消えることはない。

## 公開時の安全確認

- `APP_PASSWORD` を必ず設定する
- `FLASK_SECRET_KEY` をGitHubへ書かない
- `OPENAI_API_KEY` をGitHubへ書かない
- `data/` や `.db` をGitHubへ追加しない
- `.env` をGitHubへ追加しない
- ログインせず製麺データが表示されないことを確認する

## SQLiteについて

個人で1人が製麺記録を入力する現在の用途ならSQLiteで十分扱える。
利用者増加・複数人の同時更新・本格サービス化の段階ではPostgreSQLなどへの移行を検討する。
