"""
STEP3: 台本生成（GPT）
商品データからTikTok動画の台本を自動生成する
"""
import json
import logging
from openai import OpenAI
import config
from step1_fetch_products import Product

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """あなたはTikTokのバズる動画台本を書く専門家です。
以下のルールで台本を書いてください：
- 15〜30秒で読める長さ
- カウントダウン形式（第3位→第2位→第1位）
- 各商品: 商品名（短く）＋一言メリット
- 最後に「プロフからチェック」で締める
- 話し言葉・口語体
- 驚き・共感を引き出す表現を使う
- 一言メリットは「これ、〇〇が一瞬でできる」の形式
"""


def generate_script(products: list[Product]) -> dict:
    """商品リストからTikTok台本を生成"""
    if not config.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY未設定。サンプル台本を使用")
        return _generate_sample_script(products)

    client = OpenAI(api_key=config.OPENAI_API_KEY)

    product_info = "\n".join([
        f"商品{i+1}: {p.name}（{p.price}、評価{p.rating}、レビュー{p.review_count}件）"
        for i, p in enumerate(products)
    ])

    prompt = f"""以下の商品TOP3でTikTokランキング動画の台本を作ってください。

{product_info}

出力はJSON形式で:
{{
  "hook": "冒頭フック（1文）",
  "products": [
    {{"rank": 3, "name": "商品名", "appeal": "一言メリット", "duration": 秒数}},
    {{"rank": 2, "name": "商品名", "appeal": "一言メリット", "duration": 秒数}},
    {{"rank": 1, "name": "商品名", "appeal": "一言メリット", "duration": 秒数}}
  ],
  "cta": "締めの言葉",
  "comment_bait": "コメント誘導文"
}}"""

    try:
        response = client.chat.completions.create(
            model=config.GPT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.8,
        )
        script = json.loads(response.choices[0].message.content)
        logger.info("GPT台本生成完了")
        return script
    except Exception as e:
        logger.error(f"GPT台本生成失敗: {e}")
        return _generate_sample_script(products)


def _generate_sample_script(products: list[Product]) -> dict:
    """APIなしで動作するサンプル台本"""
    product_scripts = []
    for i, p in enumerate(products):
        rank = len(products) - i
        short_name = p.name[:20] + "…" if len(p.name) > 20 else p.name
        product_scripts.append({
            "rank": rank,
            "name": short_name,
            "appeal": f"これ、毎日の生活が一瞬で変わる",
            "duration": 5 + (2 if rank == 1 else 0),
        })

    return {
        "hook": "Amazonでバズってる商品TOP3、知らないと損するよ",
        "products": sorted(product_scripts, key=lambda x: x["rank"]),
        "cta": "気になる人はプロフのリンクからチェックしてね！",
        "comment_bait": "どれが気になった？コメントで教えて！",
    }


def script_to_narration(script: dict) -> list[str]:
    """台本をナレーション行リストに変換"""
    lines = [script["hook"]]
    for p in sorted(script["products"], key=lambda x: x["rank"]):
        lines.append(f"第{p['rank']}位、{p['name']}！")
        lines.append(p["appeal"])
    lines.append(script["cta"])
    return lines
