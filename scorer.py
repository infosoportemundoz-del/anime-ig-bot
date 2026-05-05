import os
import json
import logging
from pathlib import Path
import anthropic
from dotenv import load_dotenv
from supabase_db import log_score

load_dotenv()
logger = logging.getLogger(__name__)

# ── Pesos de cada dimensión (deben sumar 1.0) ─────────────────────────────────
DIMENSION_WEIGHTS = {
    "relevancia":    0.20,
    "viralidad":     0.25,
    "copyright":     0.20,
    "sensibilidad":  0.15,
    "humor":         0.15,
    "engagement":    0.05,
}

# Score mínimo para publicar directamente (sin revisión manual)
PUBLISH_THRESHOLD = 8.5
# Score de checkpoint (revisión recomendada)
CHECKPOINT_THRESHOLD = 7.0

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY no está configurada en .env")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def _build_prompt(video_path: str, caption: str, audio_name: str, account_name: str) -> str:
    filename = Path(video_path).name
    return f"""Eres un experto en marketing de contenido anime para Instagram.
Analiza este video de meme/clip anime y devuelve SOLO un JSON válido con el siguiente formato exacto.

Contexto del video:
- Archivo: {filename}
- Cuenta destino: @{account_name}
- Audio/música: {audio_name}
- Caption propuesto: {caption[:300]}

Evalúa cada dimensión del 0 al 10 según estos criterios:

1. relevancia (0-10): ¿El contenido encaja con el tema de la cuenta y el fandom objetivo?
   - 9-10: Clip icónico perfectamente relacionado con el tema de la cuenta
   - 7-8: Buen contenido relacionado pero no el más representativo
   - 5-6: Relacionado pero genérico, no específico de la cuenta
   - 0-4: Poco o nada relacionado con el tema

2. viralidad (0-10): ¿Tiene potencial de hacerse viral en Instagram Reels?
   - 9-10: Meme trending, audio viral, momento icónico muy compartido
   - 7-8: Buen potencial, reconocible, entretenido
   - 5-6: Correcto pero sin factor viral obvio
   - 0-4: Contenido plano, sin gancho

3. copyright (0-10): ¿Qué tan seguro es en términos de derechos de autor? (10 = muy seguro)
   - 9-10: Audio original/libre, clip transformativo claro, edición propia
   - 7-8: Riesgo bajo, es un meme o clip corto ampliamente compartido
   - 5-6: Riesgo moderado, audio oficial o clip largo
   - 0-4: Alto riesgo: audio oficial de Toei/Funimation, escenas sin transformar

4. sensibilidad (0-10): ¿Es apropiado para todas las audiencias? (10 = completamente seguro)
   - 9-10: Contenido apto para todo público, humor limpio
   - 7-8: Algún elemento de humor adulto pero nada ofensivo
   - 5-6: Contenido que algunos podrían encontrar cuestionable
   - 0-4: Violencia explícita, lenguaje muy ofensivo, contenido inapropiado

5. humor (0-10): ¿Qué tan gracioso o entretenido es?
   - 9-10: Muy gracioso, genera reacción inmediata, meme perfecto
   - 7-8: Divertido, la mayoría lo apreciará
   - 5-6: Tiene gracia pero es predecible
   - 0-4: No tiene humor notable

6. engagement (0-10): ¿Genera interacción (comentarios, shares, guardados)?
   - 9-10: Provoca debate, ganas de comentar, compartir con amigos
   - 7-8: Buen engagement esperado
   - 5-6: Engagement normal
   - 0-4: Poco probable que genere interacción

Devuelve SOLO este JSON (sin markdown, sin texto adicional):
{{
  "relevancia": <número>,
  "viralidad": <número>,
  "copyright": <número>,
  "sensibilidad": <número>,
  "humor": <número>,
  "engagement": <número>,
  "reasoning": "<explicación breve de 1-2 oraciones sobre la puntuación global>"
}}"""


def score_video(
    video_path: str,
    caption: str,
    audio_name: str,
    account_name: str,
    video_id: str | None = None,
) -> dict:
    """
    Puntúa un video usando Claude y lo registra en Supabase.

    Args:
        video_path: ruta local al video
        caption: caption generado para el video
        audio_name: nombre del audio/música del video
        account_name: nombre de la cuenta destino (sin @)
        video_id: ID del video para logging (si None, usa el nombre del archivo)

    Returns:
        {
            "score": float (0-10),
            "dimensions": dict,
            "reasoning": str,
            "should_publish": bool,
            "needs_review": bool,
            "account": str,
            "video_id": str,
        }
    """
    if video_id is None:
        video_id = Path(video_path).stem

    logger.info(f"[Scorer] Evaluando {video_id} para @{account_name}...")

    try:
        client = _get_client()
        prompt = _build_prompt(video_path, caption, audio_name, account_name)

        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = message.content[0].text.strip()

        # Limpiar posible markdown si el modelo lo añade
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        data = json.loads(raw)

    except json.JSONDecodeError as e:
        logger.error(f"[Scorer] JSON inválido de Claude: {e} — raw: {raw[:200]}")
        return _fallback_score(video_id, account_name, error=str(e))
    except Exception as e:
        logger.error(f"[Scorer] Error llamando a Claude: {e}")
        return _fallback_score(video_id, account_name, error=str(e))

    dimensions = {
        dim: float(data.get(dim, 5.0))
        for dim in DIMENSION_WEIGHTS
    }
    reasoning = data.get("reasoning", "")

    # Score ponderado
    score = sum(dimensions[dim] * weight for dim, weight in DIMENSION_WEIGHTS.items())
    score = round(min(max(score, 0.0), 10.0), 2)

    log_score(video_id, score, dimensions, account_name)

    result = {
        "score": score,
        "dimensions": dimensions,
        "reasoning": reasoning,
        "should_publish": score >= PUBLISH_THRESHOLD,
        "needs_review": CHECKPOINT_THRESHOLD <= score < PUBLISH_THRESHOLD,
        "account": account_name,
        "video_id": video_id,
    }

    level = "PUBLICAR" if result["should_publish"] else ("REVISAR" if result["needs_review"] else "RECHAZAR")
    logger.info(f"[Scorer] @{account_name} / {video_id} → {score:.2f}/10 [{level}] — {reasoning[:80]}")
    return result


def _fallback_score(video_id: str, account_name: str, error: str = "") -> dict:
    """Score neutro cuando Claude falla, para no bloquear el pipeline."""
    dims = {dim: 5.0 for dim in DIMENSION_WEIGHTS}
    score = 5.0
    log_score(video_id, score, dims, account_name)
    return {
        "score": score,
        "dimensions": dims,
        "reasoning": f"Score fallback por error: {error[:100]}",
        "should_publish": False,
        "needs_review": True,
        "account": account_name,
        "video_id": video_id,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = score_video(
        video_path="downloads/baardock_oficial/test_video.mp4",
        caption="Bro, ¿tienes esto en tu cuarto o no eres fan de verdad? 😤",
        audio_name="Dragon Ball Z OST - Gohan vs Cell",
        account_name="baardock_oficial",
        video_id="test_manual_001",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
