import random
import logging
from supabase_db import log_caption
from hashtag_rotator import get_hashtags_for_today

logger = logging.getLogger(__name__)

# ── Voz de cada cuenta ─────────────────────────────────────────────────────────
# Cada cuenta tiene su propia personalidad, jerga y referencias anime únicas.

_VOICES = {
    # ── @baardock_oficial — Dragon Ball, voz épica/saiyan, motivacional ──────
    "baardock_oficial": {
        "tema": "Dragon Ball",
        "style": "épico saiyan",
        "templates": [
            "Nii-san, si tu power level no está por las nubes, {hook} 😤⚡\n{cta}\n\n{hashtags}",
            "Escucha, kakarot... {hook} 👀🔥\n{cta}\n\n{hashtags}",
            "¿Eres saiyan o qué, bro? {hook} 💪\nIT'S OVER 9000 — {cta} ⚡\n\n{hashtags}",
            "El Ultra Instinct de los fans reales: {hook} 🥶\n{cta}\n\n{hashtags}",
            "KAKAROOOOT— {hook} 😭🔥\n{cta}\n\n{hashtags}",
            "Bro llegó a Super Saiyan 4 antes que tú en {hook} 💀\n{cta} 👇\n\n{hashtags}",
            "No me importa si eres saiyan o freezer simp — {hook} 🧊❄️\n{cta}\n\n{hashtags}",
            "El entrenamiento en la cámara de gravedad que nadie te contó: {hook} 😤\n{cta}\n\n{hashtags}",
        ],
        "hooks": [
            "esto es el Kamehameha de contenido",
            "ni Freezer puede con este nivel",
            "Bulma lloraría de la emoción",
            "Vegeta se pondría celoso",
            "el dios de la destrucción Beerus aprueba este meme",
            "esto rompió el hyperbolic time chamber",
            "Gohan estudió esto antes que la universidad",
            "hasta Mr. Satán lo comparte",
        ],
        "ctas": [
            "Sigue para más momentos saiyan 🐉",
            "Activa la campanilla o perderás el siguiente nivel ⚡",
            "Comparte esto antes de que Zamasu lo borre del timeline 💜",
            "Guarda esto en tu capsule corp 📦",
            "Dale like si tu power level lo aprueba 🔋",
        ],
    },

    # ── @luffyniista — One Piece, voz hype/emocionante, Gear 5 energy ──────
    "luffyniista": {
        "tema": "One Piece",
        "style": "pirata nakama hype",
        "templates": [
            "¡EH EH EH! {hook} 🏴‍☠️🔥\n{cta}\n\n{hashtags}",
            "Los nakamas de verdad saben que {hook} 😤⚓\n{cta}\n\n{hashtags}",
            "Gear FIVE activado porque {hook} 🌀😂\n{cta}\n\n{hashtags}",
            "El Rey de los Piratas no se rinde… tampoco este contenido: {hook} 👑\n{cta}\n\n{hashtags}",
            "¡Yo voy a ser el Rey de los Piratas! Pero primero: {hook} 🍖\n{cta}\n\n{hashtags}",
            "Shanks le dio su sombrero a Luffy, yo te doy {hook} 🎩\n{cta}\n\n{hashtags}",
            "En la Grand Line todos flipan con {hook} ⚓😭\n{cta}\n\n{hashtags}",
            "Joy Boy era fan de {hook}. Confía en el proceso 🌊\n{cta}\n\n{hashtags}",
        ],
        "hooks": [
            "esto es el Gear 5 del contenido otaku",
            "Robin lloraría de la risa",
            "Zoro se perdería buscando esto",
            "Nami ya cobró por verlo",
            "Usopp juraría que él lo inventó",
            "Sanji cocinaría esto con amor",
            "Chopper se curaría con este meme",
            "Franky diría SUPER a esto",
        ],
        "ctas": [
            "Sigue para más clips nakama 🏴‍☠️",
            "Comparte con tu tripulación antes de que los MarineS lo censuren ⚓",
            "Activa notificaciones o te quedas en Loguetown para siempre 😭",
            "Guarda esto como tesoro del One Piece 🗺️",
            "Dale like si eres nakama de verdad 💙",
        ],
    },

    # ── @sr._shanks — One Piece, voz misteriosa/épica, filosofía pirata ────
    "sr._shanks": {
        "tema": "One Piece / Shanks",
        "style": "épico misterioso yonko",
        "templates": [
            "Un Yonko no explica sus movidas. Pero esto sí lo merece: {hook} 🔴⚔️\n{cta}\n\n{hashtags}",
            "El Haki de Rey sin esfuerzo: {hook} 👑\n{cta}\n\n{hashtags}",
            "Shanks cruzaría el Grand Line por {hook} 🌊🔴\n{cta}\n\n{hashtags}",
            "El secreto que los Celestial Dragons no quieren que veas: {hook} 😶‍🌫️\n{cta}\n\n{hashtags}",
            "Esta es la razón por la que Shanks visitó al Gorosei: {hook} 🫢👁️\n{cta}\n\n{hashtags}",
            "Red Hair Shanks solo apparece cuando vale la pena. Esta vez: {hook} 🔴\n{cta}\n\n{hashtags}",
            "Bro perdió el brazo y aun así {hook} 💪❌\n{cta}\n\n{hashtags}",
            "El Conqueror's Haki de este meme: {hook} ⚡🔴\n{cta}\n\n{hashtags}",
        ],
        "hooks": [
            "esto tiene más poder que su Haki de conquista",
            "Ben Beckman apuntaría su rifle por esto",
            "el Gorosei se reunió de emergencia por este clip",
            "Im-Sama tachó esto del mapa pero aquí está",
            "los Marines piden que no lo compartas",
            "esto es el verdadero One Piece",
            "Lucky Roux se comió la mitad pero aquí está lo que quedó",
            "esto tiene más misterio que el cuarto de Im-Sama",
        ],
        "ctas": [
            "Sigue para más lore que los Marines ocultan 🔴",
            "Comparte antes de que los Gorosei lo borren del timeline ⚔️",
            "Activa notificaciones — Shanks aparece raramente, como este contenido 🌊",
            "Guarda esto como el sombrero de paja 🎩",
            "Dale like si el Haki de Rey te llegó a través de la pantalla 👑",
        ],
    },

    # ── @toonyy.chopper — One Piece / Chopper, voz cute/tierna con giros épicos
    "toonyy.chopper": {
        "tema": "One Piece / Chopper",
        "style": "cute tierno con momentos épicos",
        "templates": [
            "¡Esto no me alegra para nada! (me alegra mucho) {hook} 🦌💙\n{cta}\n\n{hashtags}",
            "Diagnóstico del Dr. Chopper: {hook} 🩺🍭\n{cta}\n\n{hashtags}",
            "¡Baka! No es que me guste este contenido, pero… {hook} 😤🌸\n{cta}\n\n{hashtags}",
            "Rumble Ball activado porque {hook} 🟠⚡\n{cta}\n\n{hashtags}",
            "Hiruluk dijo que los cerezos florecen en invierno… y {hook} 🌸❄️\n{cta}\n\n{hashtags}",
            "Monster Point desbloqueado: {hook} 🦌💥\n{cta}\n\n{hashtags}",
            "El reno más kawaii y más épico del Grand Line dice: {hook} 🏴‍☠️🦌\n{cta}\n\n{hashtags}",
            "¡No me llames kawaii! Aunque {hook}... sí, está bien 😭\n{cta}\n\n{hashtags}",
        ],
        "hooks": [
            "este clip me recargó las Rumble Balls",
            "me recuerda por qué soy nakama",
            "Hiruluk estaría orgulloso de esto",
            "esto cura el corazón más roto",
            "Robin-chan se emocionó con esto",
            "Luffy se lo comería si pudiera",
            "ni en Drum Island encontrarías algo tan épico",
            "esto es la medicina que el fandom necesitaba",
        ],
        "ctas": [
            "Sigue para más clips de tu reno favorito 🦌💙",
            "Comparte con alguien que necesite este cure 🩺",
            "Activa notificaciones — ¡y no es porque te lo pida, baka! 🌸",
            "Guarda esto para cuando te sientas mal 💊",
            "Dale like si Chopper merece más respeto 🦌",
        ],
    },
}

# Cuentas de One Piece secundarias sin config propia usan luffyniista como fallback
_FALLBACK_VOICE = "luffyniista"


def _build_caption(account: str, video_id: str | None = None) -> tuple[str, str]:
    """
    Genera caption + hashtags para la cuenta indicada.

    Returns:
        (caption, hashtags)
    """
    voice = _VOICES.get(account, _VOICES[_FALLBACK_VOICE])
    template = random.choice(voice["templates"])
    hook = random.choice(voice["hooks"])
    cta = random.choice(voice["ctas"])

    hashtag_info = get_hashtags_for_today(account)
    hashtags = hashtag_info["hashtags"]

    caption = template.format(hook=hook, cta=cta, hashtags=hashtags)

    if video_id:
        log_caption(video_id, caption, account)

    logger.info(f"[CaptionGen] @{account} → {caption[:80]}...")
    return caption, hashtags


def generate_caption(account: str, video_id: str | None = None) -> dict:
    """
    Punto de entrada principal.

    Args:
        account: nombre de cuenta sin @
        video_id: ID del video (para logging en Supabase)

    Returns:
        {
            "caption": str,
            "hashtags": str,
            "account": str,
            "voice_style": str,
            "preset_name": str,
        }
    """
    voice = _VOICES.get(account, _VOICES[_FALLBACK_VOICE])
    caption, hashtags = _build_caption(account, video_id)
    hashtag_info = get_hashtags_for_today(account)

    return {
        "caption": caption,
        "hashtags": hashtags,
        "account": account,
        "voice_style": voice["style"],
        "preset_name": hashtag_info["preset_name"],
    }


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    for acc in _VOICES:
        result = generate_caption(acc, video_id=f"test_{acc}")
        print(f"\n=== @{acc} [{result['voice_style']}] ===")
        print(result["caption"])
