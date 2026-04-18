"""
STEP7: TikTok投稿
動画をTikTokにスケジュール投稿する
"""
import os
import json
import logging
import requests
from datetime import datetime, timedelta
import config

logger = logging.getLogger(__name__)


class TikTokPoster:
    """TikTok Content Posting API クライアント"""

    BASE_URL = "https://open.tiktokapis.com/v2"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        }

    def init_upload(self, video_size: int) -> dict | None:
        """動画アップロードを初期化し、upload_urlを取得"""
        url = f"{self.BASE_URL}/post/publish/video/init/"
        payload = {
            "post_info": {
                "title": "",
                "privacy_level": "SELF_ONLY",
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": video_size,
                "chunk_size": min(video_size, 64 * 1024 * 1024),
                "total_chunk_count": 1,
            },
        }
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("data")
        except Exception as e:
            logger.error(f"アップロード初期化失敗: {e}")
            return None

    def upload_chunk(self, upload_url: str, video_path: str) -> bool:
        """動画ファイルをアップロード"""
        try:
            file_size = os.path.getsize(video_path)
            with open(video_path, "rb") as f:
                response = requests.put(
                    upload_url,
                    data=f,
                    headers={
                        "Content-Type": "video/mp4",
                        "Content-Length": str(file_size),
                        "Content-Range": f"bytes 0-{file_size - 1}/{file_size}",
                    },
                    timeout=300,
                )
            response.raise_for_status()
            logger.info(f"動画アップロード完了: {video_path}")
            return True
        except Exception as e:
            logger.error(f"アップロード失敗: {e}")
            return False

    def publish_video(
        self,
        publish_id: str,
        title: str,
        hashtags: list[str],
        schedule_time: datetime | None = None,
    ) -> bool:
        """アップロード済み動画を投稿"""
        url = f"{self.BASE_URL}/post/publish/status/fetch/"
        description = title + " " + " ".join(f"#{tag}" for tag in hashtags)

        payload = {"publish_id": publish_id}
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            data = response.json()
            status = data.get("data", {}).get("status")
            if status == "PUBLISH_COMPLETE":
                logger.info(f"投稿完了: {title}")
                return True
            logger.info(f"投稿状態: {status}")
            return False
        except Exception as e:
            logger.error(f"投稿確認失敗: {e}")
            return False

    def post_video(
        self,
        video_path: str,
        title: str,
        hashtags: list[str] | None = None,
        schedule_time: datetime | None = None,
    ) -> bool:
        """動画のアップロードから投稿まで一括実行"""
        if hashtags is None:
            hashtags = ["Amazon", "おすすめ", "バズり商品", "TikTokShop"]

        file_size = os.path.getsize(video_path)
        init_data = self.init_upload(file_size)
        if not init_data:
            return False

        upload_url = init_data.get("upload_url")
        publish_id = init_data.get("publish_id")

        if not self.upload_chunk(upload_url, video_path):
            return False

        return self.publish_video(publish_id, title, hashtags, schedule_time)


def post_with_scheduler(
    video_path: str,
    title: str,
    hashtags: list[str],
    post_times: list[datetime],
) -> bool:
    """スケジューラーを使って複数時間帯に投稿（コピー動画を微調整して再投稿）"""
    if not config.TIKTOK_SESSION_ID:
        logger.warning("TIKTOK_SESSION_ID未設定。手動投稿が必要です")
        schedule_file = video_path.replace(".mp4", "_schedule.json")
        schedule_data = {
            "video": video_path,
            "title": title,
            "hashtags": hashtags,
            "schedule": [t.isoformat() for t in post_times],
        }
        with open(schedule_file, "w", encoding="utf-8") as f:
            json.dump(schedule_data, f, ensure_ascii=False, indent=2)
        logger.info(f"スケジュールファイル保存: {schedule_file}")
        logger.info("TikTok Studioから手動投稿してください")
        return True

    poster = TikTokPoster(config.TIKTOK_SESSION_ID)
    return poster.post_video(video_path, title, hashtags, post_times[0])


def generate_optimal_schedule(posts_per_day: int = 3) -> list[datetime]:
    """TikTokエンゲージメントが高い時間帯のスケジュールを生成"""
    # 高エンゲージメント時間帯: 7時、12時、19時
    peak_hours = [7, 12, 19][:posts_per_day]
    now = datetime.now()
    base_date = now.date() + timedelta(days=1)

    return [
        datetime(base_date.year, base_date.month, base_date.day, h, 0)
        for h in peak_hours
    ]
