import os

from openai import OpenAI


def search_flour_recommendations(query: str) -> str:
    """希望する特徴をもとにWeb検索し、うどん向け小麦粉を提案する。"""
    query = (query or "").strip()
    if not query:
        raise ValueError("欲しい小麦粉の特徴を入力してください。")

    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "AI検索は現在準備中です。検索ページは利用できますが、OpenAI APIはまだ有効化していません。"
        )

    client = OpenAI()
    model = os.environ.get("OPENAI_MODEL", "gpt-5.4-mini")

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
- 最後に「比較まとめ」を短く付ける
- 根拠が弱い商品を無理におすすめしない
"""

    response = client.responses.create(
        model=model,
        tools=[{"type": "web_search", "search_context_size": "medium"}],
        reasoning={"effort": "low"},
        max_output_tokens=1800,
        input=prompt,
    )
    return response.output_text.strip()
