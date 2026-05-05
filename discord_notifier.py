import os
import logging
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ── Webhooks ───────────────────────────────────────────────────────────────────
WEBHOOK_CHECKPOINT = os.getenv("DISCORD_WEBHOOK_CHECKPOINT", "")  # score 7-8
WEBHOOK_ALERTAS = os.getenv("DISCORD_WEBHOOK_ALERTAS", "")        # errores
WEBHOOK_EXITO = os.getenv("DISCORD_WEBHOOK_EXITO", "")            # publicado OK

# Colores embed (decimal)
COLOR_CHECKPOINT = 0xF5A623   # naranja
COLOR_ALERTA = 0xE74C3C       # rojo
COLOR_EXITO = 0x2ECC71        # verde

_ACCOUNT_COLORS = {
    "baardock_oficial": 0xF5A623,    # naranja Goku
    "luffyniista": 0x3498DB,         # azul Luffy
    "sr._shanks": 0xE74C3C,          # rojo Shanks
    "toonyy.chopper": 0x9B59B6,      # morado Chopper
}


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _send(webhook_url: str, payload: dict) -> bool:
    if not webhook_url:
        logger.warning("[Discord] Webhook URL no configurada — omitiendo notificación")
        return False
    try:
        r = requests.post(webhook_url, json=payload, timeout=10)
        if r.status_code in (200, 204):
            return True
        logger.error(f"[Discord] Error {r.status_code}: {r.text[:200]}")
        return False
    except Exception as e:
        logger.error(f"[Discord] Excepción: {e}")
        return False


def _score_bar(score: float) -> str:
    filled = round(score)
    return "█" * filled + "░" * (10 - filled) + f"  {score:.1f}/10"


# ── Notificaciones públicas ────────────────────────────────────────────────────

def notify_checkpoint(video_id: str, score: float, dimensions: dict, account: str, caption_preview: str = "") -> bool:
    """
    Score 7-8: el video pasa el filtro pero necesita revisión antes de publicar.
    """
    color = _ACCOUNT_COLORS.get(account, COLOR_CHECKPOINT)
    fields = [
        {"name": "Score global", "value": f"`{_score_bar(score)}`", "inline": False},
        {"name": "Relevancia", "value": f"{dimensions.get('relevancia', 0):.1f}/10", "inline": True},
        {"name": "Viralidad", "value": f"{dimensions.get('viralidad', 0):.1f}/10", "inline": True},
        {"name": "Copyright", "value": f"{dimensions.get('copyright', 0):.1f}/10", "inline": True},
        {"name": "Sensibilidad", "value": f"{dimensions.get('sensibilidad', 0):.1f}/10", "inline": True},
        {"name": "Humor", "value": f"{dimensions.get('humor', 0):.1f}/10", "inline": True},
        {"name": "Engagement", "value": f"{dimensions.get('engagement', 0):.1f}/10", "inline": True},
    ]
    if caption_preview:
        fields.append({"name": "Caption preview", "value": f"```{caption_preview[:200]}```", "inline": False})

    payload = {
        "embeds": [{
            "title": f"⚠️ CHECKPOINT — @{account}",
            "description": f"Video `{video_id}` con score **{score:.1f}** requiere revisión manual.",
            "color": color,
            "fields": fields,
            "footer": {"text": "anime_ig_bot • checkpoint"},
            "timestamp": _ts(),
        }]
    }
    ok = _send(WEBHOOK_CHECKPOINT, payload)
    if ok:
        logger.info(f"[Discord] Checkpoint enviado: @{account} / {video_id} / {score:.1f}")
    return ok


def notify_error(error_msg: str, account: str = "", video_id: str = "", context: str = "") -> bool:
    """
    Error en cualquier etapa del pipeline.
    """
    fields = []
    if account:
        fields.append({"name": "Cuenta", "value": f"@{account}", "inline": True})
    if video_id:
        fields.append({"name": "Video ID", "value": f"`{video_id}`", "inline": True})
    if context:
        fields.append({"name": "Contexto", "value": context, "inline": False})

    payload = {
        "embeds": [{
            "title": "🚨 ERROR — anime_ig_bot",
            "description": f"```{error_msg[:1000]}```",
            "color": COLOR_ALERTA,
            "fields": fields,
            "footer": {"text": "anime_ig_bot • alertas"},
            "timestamp": _ts(),
        }]
    }
    ok = _send(WEBHOOK_ALERTAS, payload)
    if ok:
        logger.info(f"[Discord] Alerta de error enviada: {error_msg[:60]}")
    return ok


def notify_published(video_id: str, score: float, account: str, caption_preview: str = "", media_id: str = "") -> bool:
    """
    Video publicado exitosamente en Instagram.
    """
    color = _ACCOUNT_COLORS.get(account, COLOR_EXITO)
    fields = [
        {"name": "Score", "value": f"`{_score_bar(score)}`", "inline": False},
    ]
    if media_id:
        fields.append({"name": "Media ID", "value": f"`{media_id}`", "inline": True})
    if caption_preview:
        fields.append({"name": "Caption", "value": f"```{caption_preview[:300]}```", "inline": False})

    payload = {
        "embeds": [{
            "title": f"✅ PUBLICADO — @{account}",
            "description": f"Video `{video_id}` publicado correctamente en Instagram.",
            "color": color,
            "fields": fields,
            "footer": {"text": "anime_ig_bot • éxito"},
            "timestamp": _ts(),
        }]
    }
    ok = _send(WEBHOOK_EXITO, payload)
    if ok:
        logger.info(f"[Discord] Notificación de éxito enviada: @{account} / {video_id}")
    return ok


def notify_pipeline_summary(results: list[dict]) -> bool:
    """
    Resumen del ciclo completo: cuántos videos procesados, publicados, rechazados.

    results: lista de dicts con claves account, video_id, score, published (bool)
    """
    total = len(results)
    published = sum(1 for r in results if r.get("published"))
    rejected = total - published
    avg_score = sum(r.get("score", 0) for r in results) / total if total else 0

    fields = [
        {"name": "Total procesados", "value": str(total), "inline": True},
        {"name": "Publicados", "value": str(published), "inline": True},
        {"name": "Rechazados", "value": str(rejected), "inline": True},
        {"name": "Score promedio", "value": f"{avg_score:.1f}/10", "inline": True},
    ]

    color = COLOR_EXITO if published > 0 else COLOR_ALERTA
    payload = {
        "embeds": [{
            "title": "📊 Resumen del pipeline",
            "color": color,
            "fields": fields,
            "footer": {"text": "anime_ig_bot • resumen"},
            "timestamp": _ts(),
        }]
    }
    webhook = WEBHOOK_EXITO or WEBHOOK_CHECKPOINT
    ok = _send(webhook, payload)
    if ok:
        logger.info(f"[Discord] Resumen enviado: {published}/{total} publicados")
    return ok


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dims = {"relevancia": 7.5, "viralidad": 8.0, "copyright": 6.5, "sensibilidad": 9.0, "humor": 7.0, "engagement": 8.5}
    notify_checkpoint("test_video_123", 7.6, dims, "baardock_oficial", "El power level de tu estantería...")
    notify_error("yt-dlp falló: HTTP 403", account="luffyniista", video_id="xyz789", context="descargar_video()")
    notify_published("test_video_456", 8.9, "luffyniista", "EH EH EH! Gear FIVE...", media_id="17890123456")
