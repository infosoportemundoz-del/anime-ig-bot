import os
import logging
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ripgqgphiwoxyrrmshprg.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}


def _post(table: str, payload: dict) -> bool:
    if not SUPABASE_KEY:
        logger.warning("SUPABASE_KEY no configurada — saltando log")
        return False
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/{table}",
            json=payload,
            headers=HEADERS,
            timeout=10,
        )
        if r.status_code in (200, 201):
            return True
        logger.error(f"Supabase {table} error {r.status_code}: {r.text[:200]}")
        return False
    except Exception as e:
        logger.error(f"Supabase {table} excepción: {e}")
        return False


def _get(table: str, params: dict) -> list:
    if not SUPABASE_KEY:
        return []
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/{table}",
            params=params,
            headers={**HEADERS, "Prefer": ""},
            timeout=10,
        )
        if r.status_code == 200:
            return r.json()
        logger.error(f"Supabase GET {table} error {r.status_code}: {r.text[:200]}")
        return []
    except Exception as e:
        logger.error(f"Supabase GET {table} excepción: {e}")
        return []


# ── hashtag_state ──────────────────────────────────────────────────────────────

def log_hashtag_rotation(account: str, preset: str, week: int) -> bool:
    """Registra qué preset de hashtags se usó esta semana para la cuenta."""
    payload = {
        "account": account,
        "preset": preset,
        "week_number": week,
        "rotated_at": datetime.now(timezone.utc).isoformat(),
    }
    ok = _post("hashtag_state", payload)
    if ok:
        logger.info(f"[Supabase] hashtag_state logged: {account} / {preset} / week {week}")
    return ok


def get_hashtag_state(account: str) -> list:
    return _get("hashtag_state", {"account": f"eq.{account}", "order": "rotated_at.desc", "limit": "10"})


# ── caption_log ────────────────────────────────────────────────────────────────

def log_caption(video_id: str, caption: str, account: str) -> bool:
    """Registra la caption generada para un video."""
    payload = {
        "video_id": video_id,
        "caption": caption,
        "account": account,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    ok = _post("caption_log", payload)
    if ok:
        logger.info(f"[Supabase] caption_log logged: {account} / {video_id}")
    return ok


def get_caption_log(account: str, limit: int = 20) -> list:
    return _get("caption_log", {"account": f"eq.{account}", "order": "created_at.desc", "limit": str(limit)})


# ── meme_scoring_log ───────────────────────────────────────────────────────────

def log_score(video_id: str, score: float, dimensions: dict, account: str) -> bool:
    """Registra el score calculado para un video con sus dimensiones."""
    payload = {
        "video_id": video_id,
        "score": round(score, 2),
        "account": account,
        "relevancia": dimensions.get("relevancia"),
        "viralidad": dimensions.get("viralidad"),
        "copyright": dimensions.get("copyright"),
        "sensibilidad": dimensions.get("sensibilidad"),
        "humor": dimensions.get("humor"),
        "engagement": dimensions.get("engagement"),
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }
    ok = _post("meme_scoring_log", payload)
    if ok:
        logger.info(f"[Supabase] meme_scoring_log logged: {account} / {video_id} / score {score}")
    return ok


def get_scores(account: str, limit: int = 50) -> list:
    return _get("meme_scoring_log", {"account": f"eq.{account}", "order": "scored_at.desc", "limit": str(limit)})
