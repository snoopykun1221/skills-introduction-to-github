"""
STEP1: 商品データ取得（トレンド）
Amazon/楽天ランキングから商品情報を取得する
"""
import requests
from bs4 import BeautifulSoup
import time
import random
import logging
from dataclasses import dataclass
from typing import Optional
import config

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja-JP,ja;q=0.9",
}


@dataclass
class Product:
    name: str
    price: str
    rating: float
    review_count: int
    image_url: str
    product_url: str
    category: str
    one_liner: str = ""
    source: str = "amazon"


def fetch_amazon_bestsellers(category_url: str = "https://www.amazon.co.jp/gp/bestsellers") -> list[Product]:
    """Amazonベストセラーから商品をスクレイピング"""
    products = []
    try:
        time.sleep(random.uniform(1, 3))
        response = requests.get(category_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        items = soup.select("#gridItemRoot .p13n-sc-uncoverable-faceout")[:config.MAX_PRODUCTS_TO_FETCH]
        for item in items:
            try:
                name_el = item.select_one(".p13n-sc-truncate-desktop-type2, ._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")
                price_el = item.select_one(".p13n-sc-price")
                rating_el = item.select_one(".a-icon-alt")
                review_el = item.select_one(".a-size-small")
                image_el = item.select_one("img.a-dynamic-image")
                link_el = item.select_one("a.a-link-normal")

                if not name_el:
                    continue

                name = name_el.get_text(strip=True)
                price = price_el.get_text(strip=True) if price_el else "価格不明"
                rating_text = rating_el.get_text() if rating_el else "0"
                rating = float(rating_text.split("つ星")[0]) if "つ星" in rating_text else 0.0
                review_text = review_el.get_text(strip=True) if review_el else "0"
                review_count = int("".join(filter(str.isdigit, review_text))) if review_text else 0
                image_url = image_el.get("src", "") if image_el else ""
                product_url = "https://www.amazon.co.jp" + link_el.get("href", "") if link_el else ""

                products.append(Product(
                    name=name,
                    price=price,
                    rating=rating,
                    review_count=review_count,
                    image_url=image_url,
                    product_url=product_url,
                    category="amazon_bestseller",
                    source="amazon",
                ))
            except Exception as e:
                logger.warning(f"商品パース失敗: {e}")
                continue

    except Exception as e:
        logger.error(f"Amazon取得失敗: {e}")

    logger.info(f"Amazon: {len(products)}件取得")
    return products


def fetch_rakuten_ranking(genre_id: str = "0") -> list[Product]:
    """楽天ランキングAPIから商品を取得"""
    products = []
    if not config.RAKUTEN_APP_ID:
        logger.warning("RAKUTEN_APP_ID未設定。楽天APIをスキップ")
        return products

    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Ranking/20220601"
    params = {
        "applicationId": config.RAKUTEN_APP_ID,
        "genreId": genre_id,
        "hits": 30,
        "format": "json",
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        for item in data.get("Items", []):
            item = item.get("Item", {})
            products.append(Product(
                name=item.get("itemName", "")[:50],
                price=f"¥{item.get('itemPrice', 0):,}",
                rating=float(item.get("reviewAverage", 0)),
                review_count=int(item.get("reviewCount", 0)),
                image_url=item.get("mediumImageUrls", [{}])[0].get("imageUrl", ""),
                product_url=item.get("itemUrl", ""),
                category=item.get("genreName", ""),
                source="rakuten",
            ))
    except Exception as e:
        logger.error(f"楽天API失敗: {e}")

    logger.info(f"楽天: {len(products)}件取得")
    return products


DEMO_PRODUCTS = [
    Product(
        name="電動歯ブラシ 音波式",
        price="¥3,980",
        rating=4.6,
        review_count=8420,
        image_url="https://images-na.ssl-images-amazon.com/images/I/51UiRVpDvLL._AC_SL1000_.jpg",
        product_url="https://www.amazon.co.jp/",
        category="美容・ヘルスケア",
        source="demo",
    ),
    Product(
        name="折りたたみ収納ボックス 6個セット",
        price="¥2,499",
        rating=4.5,
        review_count=5130,
        image_url="https://images-na.ssl-images-amazon.com/images/I/71d4BEnFCzL._AC_SL1500_.jpg",
        product_url="https://www.amazon.co.jp/",
        category="収納・インテリア",
        source="demo",
    ),
    Product(
        name="ポータブル充電器 20000mAh",
        price="¥4,280",
        rating=4.7,
        review_count=12300,
        image_url="https://images-na.ssl-images-amazon.com/images/I/61LJhxHDELL._AC_SL1000_.jpg",
        product_url="https://www.amazon.co.jp/",
        category="スマホ・ガジェット",
        source="demo",
    ),
]


def fetch_all_products(use_demo_fallback: bool = True) -> list[Product]:
    """全ソースから商品を取得してまとめる。失敗時はデモデータを使用"""
    products = []
    products.extend(fetch_amazon_bestsellers())
    products.extend(fetch_rakuten_ranking())

    if not products and use_demo_fallback:
        logger.warning("商品取得失敗。デモデータを使用します")
        return DEMO_PRODUCTS

    logger.info(f"合計: {len(products)}件取得")
    return products
