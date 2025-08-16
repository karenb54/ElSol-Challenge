"""
Configuration module for ElSol Challenge
Manages application settings and environment variables
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Whisper configuration (local, free)
WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large

# Azure OpenAI configuration (for future chatbot)
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
AZURE_OPENAI_API_ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Application configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.flac'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# FFmpeg configuration (path where it's installed)
FFMPEG_PATH = r"C:\Program Files\ffmpeg\ffmpeg-master-latest-win64-gpl-shared\ffmpeg-master-latest-win64-gpl-shared\bin"