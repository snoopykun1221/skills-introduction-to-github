"""
STEP6: 動画生成
FFmpegで音声・画像・テキストを合成してTikTok動画を作る
"""
import os
import subprocess
import logging
from pathlib import Path
import config
from step1_fetch_products import Product
from step5_get_images import create_product_card_ffmpeg_args

logger = logging.getLogger(__name__)


def get_audio_duration(audio_path: str) -> float:
    """FFprobeで音声の長さを取得"""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "csv=p=0",
                audio_path,
            ],
            capture_output=True, text=True, timeout=10,
        )
        return float(result.stdout.strip())
    except Exception:
        return config.VIDEO_DURATION_PER_PRODUCT


def create_product_segment(
    image_path: str,
    audio_path: str,
    product: Product,
    rank: int,
    appeal: str,
    output_path: str,
) -> bool:
    """商品1件分の動画セグメントを生成"""
    try:
        duration = get_audio_duration(audio_path)

        def esc(s: str) -> str:
            return s.replace("'", "\\'").replace(":", "\\:").replace("\\", "\\\\")

        rank_text = f"第{rank}位"
        name_short = product.name[:18] + "…" if len(product.name) > 18 else product.name
        appeal_short = appeal[:22] + "…" if len(appeal) > 22 else appeal

        drawtext = (
            f"drawtext=fontfile=/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"
            f":text='{esc(rank_text)}':fontcolor=yellow:fontsize=90"
            f":x=(w-text_w)/2:y=80"
            f":shadowcolor=black:shadowx=4:shadowy=4,"

            f"drawtext=fontfile=/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"
            f":text='{esc(name_short)}':fontcolor=white:fontsize=55"
            f":x=(w-text_w)/2:y=h-280"
            f":shadowcolor=black:shadowx=3:shadowy=3,"

            f"drawtext=fontfile=/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"
            f":text='{esc(appeal_short)}':fontcolor=white:fontsize=42"
            f":x=(w-text_w)/2:y=h-180"
            f":shadowcolor=black:shadowx=2:shadowy=2"
        )

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", image_path,
            "-i", audio_path,
            "-filter_complex", (
                f"[0:v]scale={config.VIDEO_WIDTH}:{config.VIDEO_HEIGHT}"
                f":force_original_aspect_ratio=decrease,"
                f"pad={config.VIDEO_WIDTH}:{config.VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2:black,"
                f"fps={config.VIDEO_FPS},{drawtext}[v]"
            ),
            "-map", "[v]",
            "-map", "1:a",
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            "-shortest",
            output_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            logger.error(f"FFmpeg失敗: {result.stderr[-500:]}")
            return False

        logger.info(f"セグメント生成: {output_path} ({duration:.1f}秒)")
        return True

    except Exception as e:
        logger.error(f"セグメント生成エラー: {e}")
        return False


def concatenate_segments(segment_paths: list[str], bgm_path: str | None, output_path: str) -> bool:
    """セグメントを結合してBGMを追加"""
    try:
        concat_list = os.path.join(os.path.dirname(output_path), "concat_list.txt")
        with open(concat_list, "w") as f:
            for p in segment_paths:
                f.write(f"file '{os.path.abspath(p)}'\n")

        # セグメント結合
        merged = output_path.replace(".mp4", "_merged.mp4")
        cmd_concat = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", concat_list,
            "-c", "copy",
            merged,
        ]
        result = subprocess.run(cmd_concat, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            logger.error(f"結合失敗: {result.stderr[-300:]}")
            return False

        # BGMなしの場合はそのまま
        if not bgm_path or not os.path.exists(bgm_path):
            os.rename(merged, output_path)
            logger.info(f"動画完成（BGMなし）: {output_path}")
            return True

        # BGMミックス
        cmd_bgm = [
            "ffmpeg", "-y",
            "-i", merged,
            "-i", bgm_path,
            "-filter_complex",
            f"[1:a]volume={config.BGM_VOLUME}[bgm];[0:a][bgm]amix=inputs=2:duration=first[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac",
            output_path,
        ]
        result = subprocess.run(cmd_bgm, capture_output=True, text=True, timeout=120)
        os.remove(merged)
        os.remove(concat_list)

        if result.returncode != 0:
            logger.error(f"BGMミックス失敗: {result.stderr[-300:]}")
            return False

        logger.info(f"動画完成（BGMあり）: {output_path}")
        return True

    except Exception as e:
        logger.error(f"動画結合エラー: {e}")
        return False


def generate_video(
    products: list[Product],
    script: dict,
    image_paths: list[str | None],
    audio_paths: list[str],
    bgm_path: str | None,
    output_path: str,
) -> bool:
    """フル動画を生成する"""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    segments_dir = os.path.join(os.path.dirname(output_path), "segments")
    os.makedirs(segments_dir, exist_ok=True)

    sorted_products = sorted(script["products"], key=lambda x: x["rank"])
    segment_paths = []

    for i, (sp, product, image_path) in enumerate(zip(sorted_products, products, image_paths)):
        if not image_path or not os.path.exists(image_path):
            logger.warning(f"画像なし: {product.name}")
            continue

        # 対応する音声ファイルを探す（rank順のナレーション）
        audio_index = 1 + i * 2  # hook=0, rank音声=1,3,5...
        if audio_index >= len(audio_paths):
            continue

        segment_path = os.path.join(segments_dir, f"segment_{i:03d}.mp4")
        success = create_product_segment(
            image_path=image_path,
            audio_path=audio_paths[audio_index],
            product=product,
            rank=sp["rank"],
            appeal=sp["appeal"],
            output_path=segment_path,
        )
        if success:
            segment_paths.append(segment_path)

    if not segment_paths:
        logger.error("有効なセグメントなし")
        return False

    return concatenate_segments(segment_paths, bgm_path, output_path)
