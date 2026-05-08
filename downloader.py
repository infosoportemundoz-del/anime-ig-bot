import json
import logging
import random
import os
import requests
from pathlib import Path
from datetime import datetime
import yt_dlp
from config import DOWNLOADS_DIR, HISTORY_FILE, INSTAGRAM_ACCOUNTS, PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS
logger = logging.getLogger(__name__)

# BÃºsquedas para Dailymotion API
SEARCHES_DRAGON_BALL = [
    "goku dragon ball short",
    "vegeta dragon ball super short",
    "dragon ball z goku short",
    "dragon ball super shorts",
    "goku vegeta fight short",
]

SEARCHES_ONE_PIECE = [
    "luffy one piece short",
    "one piece shorts anime",
    "zoro one piece short",
    "shanks one piece short",
    "gear fifth luffy short",
]

MIN_DURATION = 5
MAX_DURATION = 90


def cargar_historial():
    if not HISTORY_FILE.exists():
        return set()
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f).get("downloaded_ids", []))
    except Exception:
        return set()


def guardar_historial(video_id):
    history = cargar_historial()
    history.add(video_id)
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"downloaded_ids": list(history)}, f, indent=2)


def buscar_videos_dailymotion(query, limite=10):
    logger.info(f"  Buscando en Dailymotion: {query[:40]}...")
    try:
        r = requests.get(
            "https://api.dailymotion.com/videos",
            params={
                "search": query,
                "limit": limite,
                "fields": "id,title,duration",
                "shorter_than": MAX_DURATION + 10,
            },
            timeout=15,
        )
        if not r.ok:
            return []
        videos = r.json().get("list", [])
        validos = [v for v in videos if MIN_DURATION <= v.get("duration", 0) <= MAX_DURATION]
        logger.info(f"  Encontrados {len(validos)} shorts validos")
        return validos
    except Exception as e:
        logger.warning(f"  Error buscando: {e}")
        return []


def descargar_video(video_info, cuenta):
    historial = cargar_historial()
    video_id = video_info.get("id", "")
    if not video_id or video_id in historial:
        return None

    url = f"https://www.dailymotion.com/video/{video_id}"
    cuenta_dir = DOWNLOADS_DIR / cuenta
    cuenta_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_template = str(cuenta_dir / f"{timestamp}_{video_id}.%(ext)s")

    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
            "socket_timeout": 60,
            "http_headers": {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        }
        if PROXY_HOST and PROXY_PORT:
            ydl_opts["proxy"] = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
    }
    try:
        logger.info(f"  Descargando: {video_info.get('title','')[:50]}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        archivos = list(cuenta_dir.glob(f"*{video_id}*"))
        if not archivos:
            return None
        guardar_historial(video_id)
        logger.info(f"  OK: {archivos[0].name}")
        return {"id": video_id, "path": str(archivos[0]), "cuenta": cuenta}
    except Exception as e:
        logger.warning(f"  Error {video_id}: {e}")
        return None


def descargar_para_cuenta(cuenta, cantidad=3):
    logger.info(f"\nDescargando {cantidad} videos para @{cuenta}...")
    config_cuenta = INSTAGRAM_ACCOUNTS.get(cuenta, {})
    tema = config_cuenta.get("tema", "dragon_ball")
    searches = SEARCHES_DRAGON_BALL if tema == "dragon_ball" else SEARCHES_ONE_PIECE
    random.shuffle(searches)
    descargados = []
    for query in searches[:4]:
        if len(descargados) >= cantidad:
            break
        videos = buscar_videos_dailymotion(query)
        random.shuffle(videos)
        for video_info in videos:
            if len(descargados) >= cantidad:
                break
            resultado = descargar_video(video_info, cuenta)
            if resultado:
                descargados.append(resultado)
    logger.info(f"Descargados {len(descargados)} para @{cuenta}")
    return descargados


def descargar_pendientes():
    total = 0
    for cuenta_nombre, config in INSTAGRAM_ACCOUNTS.items():
        if not config.get("ig_user_id", ""):
            continue
        cuenta_dir = DOWNLOADS_DIR / cuenta_nombre
        cuenta_dir.mkdir(parents=True, exist_ok=True)
        pendientes = list(cuenta_dir.glob("*.mp4"))
        if len(pendientes) >= 10:
            logger.info(f"@{cuenta_nombre}: ya tiene {len(pendientes)} videos")
            continue
        descargados = descargar_para_cuenta(cuenta_nombre, cantidad=3)
        total += len(descargados)
    return total


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    descargar_pendientes()
