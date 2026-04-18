"""
STEP5: 画像素材取得
商品画像をダウンロードする（方法A: 商品画像そのまま使用）
"""
import os
import requests
import logging
from pathlib import Path
from step1_fetch_products import Product

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TikTokBot/1.0)",
}


def download_product_image(product: Product, output_dir: str, index: int) -> str | None:
    """商品画像をダウンロードしてローカルパスを返す"""
    if not product.image_url:
        logger.warning(f"画像URL未設定: {product.name}")
        return None

    os.makedirs(output_dir, exist_ok=True)
    ext = Path(product.image_url.split("?")[0]).suffix or ".jpg"
    output_path = os.path.join(output_dir, f"product_{index:03d}{ext}")

    try:
        response = requests.get(product.image_url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

        logger.info(f"画像ダウンロード完了: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"画像ダウンロード失敗 ({product.name}): {e}")
        return None


def download_all_images(products: list[Product], output_dir: str) -> list[str | None]:
    """全商品の画像をダウンロードしてパスリストを返す"""
    paths = []
    for i, product in enumerate(products):
        path = download_product_image(product, output_dir, i)
        paths.append(path)
    return paths


def create_product_card_ffmpeg_args(
    image_path: str,
    product_name: str,
    appeal_text: str,
    rank: int,
    output_path: str,
    width: int = 1080,
    height: int = 1920,
) -> list[str]:
    """FFmpegで商品カード画像を生成するコマンド引数を返す"""
    rank_text = f"第{rank}位"
    # テキストのエスケープ（FFmpegのdrawtext用）
    def esc(s: str) -> str:
        return s.replace("'", "\\'").replace(":", "\\:")

    return [
        "ffmpeg", "-y",
        "-i", image_path,
        "-vf", (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black,"
            f"drawtext=fontfile=/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"
            f":text='{esc(rank_text)}':fontcolor=yellow:fontsize=80"
            f":x=(w-text_w)/2:y=100:shadowcolor=black:shadowx=3:shadowy=3,"
            f"drawtext=fontfile=/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"
            f":text='{esc(product_name[:15])}':fontcolor=white:fontsize=50"
            f":x=(w-text_w)/2:y=200:shadowcolor=black:shadowx=2:shadowy=2,"
            f"drawtext=fontfile=/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"
            f":text='{esc(appeal_text[:20])}':fontcolor=white:fontsize=40"
            f":x=(w-text_w)/2:y=h-200:shadowcolor=black:shadowx=2:shadowy=2"
        ),
        "-frames:v", "1",
        output_path,
    ]
