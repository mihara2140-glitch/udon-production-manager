import os

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()


def search_flour_recommendations(query: str) -> str:
    """希望する特徴をもとにWeb検索し、うどん向け小麦粉を提案する。"""
    query = (query or "").strip()
    if not query:
        raise ValueError("欲しい小麦粉の特徴を入力してください。")

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "AI検索を使うには OPENAI_API_KEY の設定が必要です。"
            "ローカルでは .env、PythonAnywhereでは公開環境の設定にAPIキーを追加してください。"
        )

    try:
        from openai import OpenAI
    except ImportError as error:
        raise RuntimeError(
            "AI検索用ライブラリ openai を読み込めません。"
            "python -m pip install -r requirements.txt を実行してください。"
        ) from error

    # Web検索対応かつコストを抑えやすいモデルを既定にする。
    # OPENAI_MODEL を設定すれば公開環境ごとに変更できる。
    model = os.environ.get("OPENAI_MODEL", "gpt-5.6-luna").strip()
    client = OpenAI(api_key=api_key, timeout=60.0)

    prompt = f"""
あなたは、うどん製麺用の小麦粉を調査するアシスタントです。
ユーザーの希望条件に合う、日本で購入・入手を検討できる小麦粉をWeb検索してください。

希望条件:
{query}

次のルールで日本語で回答してください。
- おすすめを最大3件、順位付きで出す
- 商品名・メーカー/製粉会社が確認できる場合は書く
- 薄力粉/中力粉/強力粉など種類を書く
- たんぱく質・灰分など数値は、信頼できる情報源で確認できた場合だけ書く
- コシ、もち感、香り、吸水・扱いやすさなど、うどん製麺の観点で特徴を説明する
- 「なぜ今回の条件に合うか」を各候補に書く
- メーカー公式・製粉会社・信頼できる販売情報を優先する
- 推測と確認できた事実を混同しない
- 根拠が弱い商品を無理におすすめしない
- 最後に「比較まとめ」と「主な参照元」を短く付ける
"""

    try:
        response = client.responses.create(
            model=model,
            tools=[
                {
                    "type": "web_search",
                    "search_context_size": "medium",
                    "user_location": {
                        "type": "approximate",
                        "country": "JP",
                        "timezone": "Asia/Tokyo",
                    },
                }
            ],
            reasoning={"effort": "low"},
            max_output_tokens=1800,
            input=prompt,
        )
    except Exception as error:
        raise RuntimeError(
            f"AI検索に失敗しました。APIキー・利用上限・モデル設定を確認してください。詳細: {error}"
        ) from error

    result = (response.output_text or "").strip()
    if not result:
        raise RuntimeError("AI検索は完了しましたが、回答を取得できませんでした。")

    return result
