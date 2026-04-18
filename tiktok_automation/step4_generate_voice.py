"""
STEP4: 音声生成
VOICEVOX（無料）またはElevenLabsで音声を生成する
"""
import os
import requests
import logging
from pathlib import Path
import config

logger = logging.getLogger(__name__)


def generate_voice_voicevox(text: str, output_path: str) -> bool:
    """VOICEVOXでテキストを音声に変換（無料・日本語特化）"""
    try:
        # 音声クエリ生成
        query_response = requests.post(
            f"{config.VOICEVOX_URL}/audio_query",
            params={"text": text, "speaker": config.VOICEVOX_SPEAKER_ID},
            timeout=30,
        )
        query_response.raise_for_status()
        query = query_response.json()

        # 読み上げ速度調整（TikTok向けに少し速め）
        query["speedScale"] = 1.2
        query["intonationScale"] = 1.1

        # 音声合成
        synth_response = requests.post(
            f"{config.VOICEVOX_URL}/synthesis",
            params={"speaker": config.VOICEVOX_SPEAKER_ID},
            json=query,
            timeout=60,
        )
        synth_response.raise_for_status()

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(synth_response.content)

        logger.info(f"VOICEVOX音声生成: {output_path}")
        return True

    except requests.ConnectionError:
        logger.warning("VOICEVOXサーバー未起動。ElevenLabsにフォールバック")
        return False
    except Exception as e:
        logger.error(f"VOICEVOX失敗: {e}")
        return False


def generate_voice_elevenlabs(text: str, output_path: str) -> bool:
    """ElevenLabsでテキストを音声に変換（自然・英語も可）"""
    if not config.ELEVENLABS_API_KEY:
        logger.warning("ELEVENLABS_API_KEY未設定")
        return False

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{config.ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": config.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.3,
            "use_speaker_boost": True,
        },
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)

        logger.info(f"ElevenLabs音声生成: {output_path}")
        return True

    except Exception as e:
        logger.error(f"ElevenLabs失敗: {e}")
        return False


def generate_voice(text: str, output_path: str) -> bool:
    """設定に応じた音声エンジンで音声生成"""
    if config.VOICE_ENGINE == "voicevox":
        success = generate_voice_voicevox(text, output_path)
        if not success:
            return generate_voice_elevenlabs(text, output_path)
        return success
    else:
        return generate_voice_elevenlabs(text, output_path)


def generate_all_voices(narration_lines: list[str], output_dir: str) -> list[str]:
    """全ナレーション行の音声ファイルを生成し、パスリストを返す"""
    os.makedirs(output_dir, exist_ok=True)
    audio_paths = []

    for i, line in enumerate(narration_lines):
        output_path = os.path.join(output_dir, f"narration_{i:03d}.wav")
        success = generate_voice(line, output_path)
        if success:
            audio_paths.append(output_path)
        else:
            logger.error(f"音声生成失敗: {line}")

    logger.info(f"音声生成完了: {len(audio_paths)}/{len(narration_lines)}件")
    return audio_paths
