"""
STEP4: 音声生成
gTTS（無料・APIキー不要）/ VOICEVOX / ElevenLabs で音声を生成する
"""
import os
import subprocess
import requests
import logging
from pathlib import Path
import config

logger = logging.getLogger(__name__)


def generate_voice_gtts(text: str, output_path: str) -> bool:
    """gTTS（Google TTS）で音声生成 - 無料・APIキー不要"""
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="ja", slow=False)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        mp3_path = output_path.replace(".wav", ".mp3")
        tts.save(mp3_path)

        # mp3 → wav に変換（FFmpegで統一フォーマット）
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", mp3_path, "-ar", "44100", "-ac", "1", output_path],
            capture_output=True, timeout=30,
        )
        os.remove(mp3_path)

        if result.returncode == 0:
            logger.info(f"gTTS音声生成: {output_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"gTTS失敗: {e}")
        return False


def generate_voice_voicevox(text: str, output_path: str) -> bool:
    """VOICEVOXでテキストを音声に変換（無料・日本語特化）"""
    try:
        query_response = requests.post(
            f"{config.VOICEVOX_URL}/audio_query",
            params={"text": text, "speaker": config.VOICEVOX_SPEAKER_ID},
            timeout=30,
        )
        query_response.raise_for_status()
        query = query_response.json()
        query["speedScale"] = 1.2
        query["intonationScale"] = 1.1

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
        logger.warning("VOICEVOXサーバー未起動。gTTSにフォールバック")
        return False
    except Exception as e:
        logger.error(f"VOICEVOX失敗: {e}")
        return False


def generate_voice_elevenlabs(text: str, output_path: str) -> bool:
    """ElevenLabsでテキストを音声に変換"""
    if not config.ELEVENLABS_API_KEY:
        return False

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{config.ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": config.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8},
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


def generate_voice_espeak(text: str, output_path: str) -> bool:
    """espeakでオフライン音声生成（デモ用・日本語非対応→英語読み上げ）"""
    import subprocess
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["espeak", "-v", "en", "-s", "150", "-p", "50", text, "-w", output_path],
            capture_output=True, timeout=30,
        )
        if result.returncode == 0 and os.path.exists(output_path):
            logger.info(f"espeak音声生成: {output_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"espeak失敗: {e}")
        return False


def generate_voice_silent(duration: float, output_path: str) -> bool:
    """指定秒数の無音WAVを生成（最終フォールバック）"""
    import subprocess
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
                "-t", str(duration),
                "-c:a", "pcm_s16le",
                output_path,
            ],
            capture_output=True, timeout=30,
        )
        return result.returncode == 0
    except Exception as e:
        logger.error(f"無音生成失敗: {e}")
        return False


def generate_voice(text: str, output_path: str) -> bool:
    """優先順位: VOICEVOX → ElevenLabs → gTTS → espeak → 無音"""
    if config.VOICE_ENGINE == "voicevox":
        if generate_voice_voicevox(text, output_path):
            return True
    if config.VOICE_ENGINE == "elevenlabs" or config.ELEVENLABS_API_KEY:
        if generate_voice_elevenlabs(text, output_path):
            return True
    if generate_voice_gtts(text, output_path):
        return True
    if generate_voice_espeak(text, output_path):
        return True
    # 絶対フォールバック: 無音3秒
    logger.warning(f"全TTS失敗。無音で代替: {text}")
    return generate_voice_silent(3.0, output_path)


def generate_all_voices(narration_lines: list[str], output_dir: str) -> list[str]:
    """全ナレーション行の音声ファイルを生成"""
    os.makedirs(output_dir, exist_ok=True)
    audio_paths = []

    for i, line in enumerate(narration_lines):
        output_path = os.path.join(output_dir, f"narration_{i:03d}.wav")
        if generate_voice(line, output_path):
            audio_paths.append(output_path)
        else:
            logger.error(f"音声生成失敗: {line}")

    logger.info(f"音声生成完了: {len(audio_paths)}/{len(narration_lines)}件")
    return audio_paths
