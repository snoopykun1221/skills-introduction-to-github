"""
STEP2: フィルタリング
不適切な商品を除外し、TikTok向けにスコアリングする
"""
import logging
import config
from step1_fetch_products import Product

logger = logging.getLogger(__name__)

# 除外キーワード（見た目でわからない商品）
EXCLUDE_KEYWORDS = [
    "サプリ", "薬", "医薬", "処方", "保険", "証券", "金融",
    "ギフト券", "ポイント", "クーポン",
]

# 高スコアカテゴリ（TikTokで映えやすい）
HIGH_VALUE_CATEGORIES = [
    "キッチン", "美容", "ガジェット", "スマホ", "アウトドア",
    "収納", "インテリア", "フィットネス", "ペット",
]


def score_product(product: Product) -> float:
    """商品のTikTok適性スコアを計算（0〜100）"""
    score = 0.0

    # レビュー数（信頼性）: 最大30点
    if product.review_count >= 1000:
        score += 30
    elif product.review_count >= 500:
        score += 20
    elif product.review_count >= config.MIN_REVIEW_COUNT:
        score += 10

    # 評価（品質）: 最大20点
    if product.rating >= 4.5:
        score += 20
    elif product.rating >= 4.0:
        score += 15
    elif product.rating >= config.MIN_RATING:
        score += 5

    # カテゴリ（映えやすさ）: 最大20点
    for cat in HIGH_VALUE_CATEGORIES:
        if cat in product.category or cat in product.name:
            score += 20
            break

    # 画像あり: 10点
    if product.image_url:
        score += 10

    # 名前の短さ（理解しやすさ）: 最大10点
    name_len = len(product.name)
    if name_len <= 15:
        score += 10
    elif name_len <= 30:
        score += 5

    # 価格帯（利益が出る範囲: 1,000〜30,000円）: 10点
    price_digits = "".join(filter(str.isdigit, product.price))
    if price_digits:
        price = int(price_digits)
        if 1000 <= price <= 30000:
            score += 10

    return min(score, 100.0)


def is_excluded(product: Product) -> bool:
    """除外対象かチェック"""
    text = product.name + product.category
    return any(kw in text for kw in EXCLUDE_KEYWORDS)


def filter_products(products: list[Product]) -> list[Product]:
    """フィルタリングとスコアリングを実行し、上位商品を返す"""
    # 基本条件でフィルタ
    filtered = [
        p for p in products
        if p.review_count >= config.MIN_REVIEW_COUNT
        and p.rating >= config.MIN_RATING
        and p.image_url
        and not is_excluded(p)
    ]

    # スコアリング
    scored = [(p, score_product(p)) for p in filtered]
    scored.sort(key=lambda x: x[1], reverse=True)

    result = [p for p, _ in scored[:config.TOP_PRODUCTS_COUNT]]
    logger.info(f"フィルタ後: {len(filtered)}件 → TOP{len(result)}件選出")
    return result
