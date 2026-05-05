import os
from pathlib import Path

EN_RAILWAY = os.getenv("RAILWAY_ENVIRONMENT") is not None

if EN_RAILWAY:
    BASE_DIR = Path("/app")
    FFMPEG_PATH = "ffmpeg"
else:
    BASE_DIR = Path("C:/Users/Javi/Desktop/anime_ig_bot")
    FFMPEG_PATH = "C:/ffmpeg/bin/ffmpeg.exe"

DOWNLOADS_DIR = BASE_DIR / "downloads"
EDITED_DIR = BASE_DIR / "edited"
WATERMARK_DIR = BASE_DIR / "watermarks"
LOGS_DIR = BASE_DIR / "logs"
DB_DIR = BASE_DIR / "db"

for d in [DOWNLOADS_DIR, EDITED_DIR, WATERMARK_DIR, LOGS_DIR, DB_DIR]:
    d.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_DIR / "bot.log"
HISTORY_FILE = DB_DIR / "downloaded.json"

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
META_APP_ID = "1260355622921916"

INSTAGRAM_ACCOUNTS = {
    "baardock_oficial": {
        "ig_user_id": "17841455645544000",
        "facebook_page_id": "1083647138155740",
        "watermark": str(WATERMARK_DIR / "baardock_watermark.png"),
        "tema": "dragon_ball",
        "hashtags": "#DragonBall #DBSuper #Goku #Vegeta #Anime #DBZ",
    },
    "luffyniista": {
        "ig_user_id": "17841467685696752",
        "facebook_page_id": "676544802214875",
        "watermark": str(WATERMARK_DIR / "luffyniista_watermark.png"),
        "tema": "one_piece",
        "hashtags": "#OnePiece #Luffy #Anime #Pirates",
    },
}

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "dkigsrmae")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "926917235239482")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "-5bvJlprF-PYItTAVs1FP2-CtjI")
