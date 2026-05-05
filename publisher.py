import time
import logging
import random
from pathlib import Path
import cloudinary
import cloudinary.uploader
import requests
from config import (
    EDITED_DIR, META_ACCESS_TOKEN, INSTAGRAM_ACCOUNTS,
    CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
)

logger = logging.getLogger(__name__)

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)

GRAPH_API = "https://graph.facebook.com/v25.0"

# Captions por tema - más fuerza de venta y otaku
CAPTIONS_DRAGON_BALL = [
    "El power level de tu estantería necesita subir 👀⚡\nFiguras oficiales en bio 🔥\n\n#DragonBall #DBZ #DBSuper #Goku #Vegeta #Anime #Saiyan #DragonBallZ #AnimeMemes #OtakuEspanol",
    "Bro, ¿tienes esto en tu cuarto o no eres fan de verdad? 😤\nTienda oficial → link en bio\n\n#DragonBall #Goku #Vegeta #DBZ #Anime #Figura #Coleccionismo #OtakuEspanol #AnimeFigures",
    "Tu estantería te está pidiendo esto a gritos 👇\nEnvío a España y LATAM 📦 — link en bio\n\n#DragonBall #DBSuper #SSJ #UltraInstinct #Anime #OtakuEspanol #FigurasAnime #Coleccionismo",
    "La figura del meme existe y es BRUTAL 🔥\n¿La tienes ya? Link en bio 👀\n\n#DragonBall #DBZ #Goku #Vegeta #Anime #AnimeFan #OtakuEspanol #FigurasAnime",
    "Stock limitado. Los fans de verdad ya lo saben 👀\nLink en bio antes de que se acabe ⚡\n\n#DragonBall #DBSuper #Saiyan #Anime #OtakuEspanol #Coleccionismo #FigurasAnime #DragonBallZ",
]

CAPTIONS_ONE_PIECE = [
    "Si eres nakama de verdad, esto tiene que estar en tu cuarto 🏴‍☠️\nTienda oficial → link en bio 👀\n\n#OnePiece #Luffy #Anime #Nakama #Pirates #OtakuEspanol #FigurasAnime #OnePieceMemes",
    "Tu tripulación te espera en la estantería ⚓\nFiguras oficiales — link en bio 🔥\n\n#OnePiece #Luffy #Zoro #Nami #Anime #OtakuEspanol #Coleccionismo #AnimeFigures",
    "El sueño del Rey de los Piratas empieza en tu habitación 👑\nLink en bio 🏴‍☠️\n\n#OnePiece #Luffy #GearFive #Anime #OtakuEspanol #FigurasAnime #Nakama",
    "¿Fan de OP o solo dices que lo eres? 😂\nDemuéstralo — link en bio 🔥\n\n#OnePiece #Anime #Luffy #Shanks #OtakuEspanol #Coleccionismo #FigurasAnime #OnePieceFan",
    "Stock limitado 👀 Los nakamas reales ya están mirando\nLink en bio antes de que vuele ⚓\n\n#OnePiece #Luffy #Anime #OtakuEspanol #FigurasAnime #Pirates #Coleccionismo",
]


def subir_a_cloudinary(video_path):
    try:
        logger.info(f"  Subiendo a Cloudinary: {Path(video_path).name}")
        result = cloudinary.uploader.upload(
            video_path,
            resource_type="video",
            folder="anime_ig_bot"
        )
        return result.get("secure_url")
    except Exception as e:
        logger.error(f"  Error Cloudinary: {e}")
        return None


def generar_caption(cuenta):
    config = INSTAGRAM_ACCOUNTS.get(cuenta, {})
    tema = config.get("tema", "dragon_ball")
    if tema == "dragon_ball":
        return random.choice(CAPTIONS_DRAGON_BALL)
    else:
        return random.choice(CAPTIONS_ONE_PIECE)


def crear_container(ig_user_id, video_url, caption):
    url = f"{GRAPH_API}/{ig_user_id}/media"
    params = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": META_ACCESS_TOKEN
    }
    try:
        r = requests.post(url, params=params, timeout=60)
        data = r.json()
        if "id" in data:
            return data["id"]
        logger.error(f"  Error Meta API: {data}")
        return None
    except Exception as e:
        logger.error(f"  Error: {e}")
        return None


def esperar_procesamiento(creation_id, max_intentos=30):
    url = f"{GRAPH_API}/{creation_id}"
    params = {"fields": "status_code", "access_token": META_ACCESS_TOKEN}
    for intento in range(max_intentos):
        try:
            r = requests.get(url, params=params, timeout=30)
            status = r.json().get("status_code", "")
            logger.info(f"  Estado: {status} (intento {intento+1}/{max_intentos})")
            if status == "FINISHED":
                return True
            if status == "ERROR":
                logger.error("  Meta reportó ERROR en el container")
                return False
            time.sleep(10)
        except Exception as e:
            logger.warning(f"  Error verificando estado: {e}")
            time.sleep(10)
    logger.error("  Timeout esperando procesamiento de Meta")
    return False


def publicar_container(ig_user_id, creation_id):
    url = f"{GRAPH_API}/{ig_user_id}/media_publish"
    params = {"creation_id": creation_id, "access_token": META_ACCESS_TOKEN}
    try:
        r = requests.post(url, params=params, timeout=60)
        data = r.json()
        if "id" in data:
            return data["id"]
        logger.error(f"  Error publicando: {data}")
        return None
    except Exception as e:
        logger.error(f"  Error: {e}")
        return None


def publicar_reel(cuenta, video_path):
    config = INSTAGRAM_ACCOUNTS.get(cuenta, {})
    ig_user_id = config.get("ig_user_id", "")
    if not ig_user_id:
        logger.warning(f"  Sin ig_user_id para @{cuenta}, saltando")
        return False

    logger.info(f"\nPublicando en @{cuenta}: {Path(video_path).name}")

    video_url = subir_a_cloudinary(video_path)
    if not video_url:
        return False

    caption = generar_caption(cuenta)
    logger.info(f"  Caption: {caption[:60]}...")

    creation_id = crear_container(ig_user_id, video_url, caption)
    if not creation_id:
        return False

    logger.info("  Esperando procesamiento Meta...")
    if not esperar_procesamiento(creation_id):
        return False

    media_id = publicar_container(ig_user_id, creation_id)
    if not media_id:
        return False

    logger.info(f"  ✅ PUBLICADO en @{cuenta}! Media ID: {media_id}")
    try:
        Path(video_path).unlink()
        logger.info(f"  🗑️  Video local eliminado")
    except Exception:
        pass
    return True


def publicar_uno_por_cuenta():
    total = 0
    for cuenta in INSTAGRAM_ACCOUNTS.keys():
        config = INSTAGRAM_ACCOUNTS[cuenta]
        if not config.get("ig_user_id", ""):
            logger.info(f"  @{cuenta}: sin ig_user_id, saltando")
            continue
        edited_dir = EDITED_DIR / cuenta
        if not edited_dir.exists():
            logger.info(f"  @{cuenta}: carpeta edited no existe")
            continue
        videos = list(edited_dir.glob("*.mp4"))
        if not videos:
            logger.info(f"  @{cuenta}: sin videos editados listos")
            continue
        if publicar_reel(cuenta, str(videos[0])):
            total += 1
    return total


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    publicar_uno_por_cuenta()
