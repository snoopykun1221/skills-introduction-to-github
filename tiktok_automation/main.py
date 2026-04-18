"""
TikTok Shop 完全自動化システム
商品取得 → フィルタ → 台本生成 → 音声 → 動画 → 投稿
"""
import os
import logging
import argparse
from datetime import datetime
import config
from step1_fetch_products import fetch_all_products
from step2_filter_products import filter_products
from step3_generate_script import generate_script, script_to_narration
from step4_generate_voice import generate_all_voices
from step5_get_images import download_all_images
from step6_generate_video import generate_video
from step7_post_tiktok import post_with_scheduler, generate_optimal_schedule

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def setup_dirs():
    """出力ディレクトリを作成"""
    for d in [config.OUTPUT_DIR, config.AUDIO_DIR, config.IMAGE_DIR, config.VIDEO_DIR]:
        os.makedirs(d, exist_ok=True)


def run_pipeline(
    posts_per_day: int = 3,
    bgm_path: str | None = None,
    dry_run: bool = False,
) -> str | None:
    """
    フルパイプラインを実行して動画ファイルパスを返す。
    dry_run=True の場合は投稿をスキップ。
    """
    setup_dirs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info("=" * 50)
    logger.info("TikTok Shop 自動化パイプライン開始")
    logger.info("=" * 50)

    # STEP1: 商品取得
    logger.info("[STEP1] 商品データ取得中...")
    products = fetch_all_products()
    if not products:
        logger.error("商品取得失敗。終了")
        return None

    # STEP2: フィルタリング
    logger.info("[STEP2] フィルタリング中...")
    top_products = filter_products(products)
    if not top_products:
        logger.error("有効な商品なし。終了")
        return None

    logger.info(f"選出商品:")
    for i, p in enumerate(top_products):
        logger.info(f"  {i+1}. {p.name} ({p.rating}★, {p.review_count}件)")

    # STEP3: 台本生成
    logger.info("[STEP3] 台本生成中...")
    script = generate_script(top_products)
    narration_lines = script_to_narration(script)
    logger.info(f"台本: {len(narration_lines)}行")

    # STEP4: 音声生成
    logger.info("[STEP4] 音声生成中...")
    audio_paths = generate_all_voices(narration_lines, config.AUDIO_DIR)
    if not audio_paths:
        logger.error("音声生成失敗。終了")
        return None

    # STEP5: 画像ダウンロード
    logger.info("[STEP5] 商品画像取得中...")
    image_paths = download_all_images(top_products, config.IMAGE_DIR)

    # STEP6: 動画生成
    logger.info("[STEP6] 動画生成中...")
    output_video = os.path.join(config.VIDEO_DIR, f"tiktok_{timestamp}.mp4")
    success = generate_video(
        products=top_products,
        script=script,
        image_paths=image_paths,
        audio_paths=audio_paths,
        bgm_path=bgm_path,
        output_path=output_video,
    )
    if not success:
        logger.error("動画生成失敗。終了")
        return None

    logger.info(f"動画完成: {output_video}")

    # STEP7: 投稿
    if dry_run:
        logger.info("[STEP7] DRY RUN - 投稿をスキップ")
    else:
        logger.info("[STEP7] TikTok投稿中...")
        title = f"Amazonでバズってる商品TOP3 #{timestamp[:8]}"
        hashtags = ["Amazon", "バズり商品", "おすすめ", "TikTokShop", "買って良かった"]
        schedule = generate_optimal_schedule(posts_per_day)
        post_with_scheduler(output_video, title, hashtags, schedule)

    logger.info("=" * 50)
    logger.info("パイプライン完了")
    logger.info("=" * 50)
    return output_video


def main():
    parser = argparse.ArgumentParser(description="TikTok Shop 自動化システム")
    parser.add_argument("--posts-per-day", type=int, default=3, help="1日の投稿数 (default: 3)")
    parser.add_argument("--bgm", type=str, default=None, help="BGMファイルパス (.mp3/.wav)")
    parser.add_argument("--dry-run", action="store_true", help="投稿せずに動画生成のみ")
    args = parser.parse_args()

    run_pipeline(
        posts_per_day=args.posts_per_day,
        bgm_path=args.bgm,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
