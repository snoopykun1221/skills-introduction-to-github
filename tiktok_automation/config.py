"""
TikTok Shop Automation - Configuration
"""
import os

# OpenAI GPT settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GPT_MODEL = "gpt-4o-mini"

# ElevenLabs settings (voice generation)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

# VOICEVOX settings (free Japanese TTS)
VOICEVOX_URL = os.getenv("VOICEVOX_URL", "http://localhost:50021")
VOICEVOX_SPEAKER_ID = 3  # ずんだもん

# Amazon Product Advertising API
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY", "")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY", "")
AMAZON_PARTNER_TAG = os.getenv("AMAZON_PARTNER_TAG", "")

# Rakuten API
RAKUTEN_APP_ID = os.getenv("RAKUTEN_APP_ID", "")

# TikTok API (unofficial)
TIKTOK_SESSION_ID = os.getenv("TIKTOK_SESSION_ID", "")

# Video settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
VIDEO_DURATION_PER_PRODUCT = 7  # seconds per product
BGM_VOLUME = 0.3

# Output directories
OUTPUT_DIR = "output"
AUDIO_DIR = f"{OUTPUT_DIR}/audio"
IMAGE_DIR = f"{OUTPUT_DIR}/images"
VIDEO_DIR = f"{OUTPUT_DIR}/videos"

# Product filter thresholds
MIN_REVIEW_COUNT = 100
MIN_RATING = 3.5
MAX_PRODUCTS_TO_FETCH = 50
TOP_PRODUCTS_COUNT = 3

# Voice engine: "voicevox" or "elevenlabs"
VOICE_ENGINE = os.getenv("VOICE_ENGINE", "voicevox")
