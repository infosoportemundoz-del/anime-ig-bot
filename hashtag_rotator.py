from datetime import date
import logging
from supabase_db import log_hashtag_rotation

logger = logging.getLogger(__name__)

# 5 presets por cuenta — rotación lunes(0)…viernes(4), fin de semana usa preset5
HASHTAG_PRESETS = {
    "baardock_oficial": [
        {
            "name": "db_power",
            "tags": "#DragonBall #DBZ #DragonBallSuper #Goku #Vegeta #Saiyan #SuperSaiyan #KamehamehaFriday #AnimeEspanol #OtakuEspanol",
        },
        {
            "name": "db_meme",
            "tags": "#DragonBallMemes #AnimeMemes #DBZMemes #GokuMeme #VegetaMeme #OtakuMeme #AnimeHumor #FandomAnime #DBZFan #AnimeFan",
        },
        {
            "name": "db_fandom",
            "tags": "#DragonBallCommunity #DBZCommunity #GokuFan #VegetaFan #GohanFan #TrunksDBZ #BeerusGod #UIGoku #MasteredUI #AnimeLatino",
        },
        {
            "name": "db_hype",
            "tags": "#DBSuperHero #DragonBallGT #XenoverseFans #DragonBallLegends #SaiyanBeyond #GokuVsVegeta #FusionAnime #GogentaDBZ #ViralAnime #TrendingAnime",
        },
        {
            "name": "db_mix",
            "tags": "#Anime #AnimeClips #AnimeCommunity #OtakuWorld #AnimeViral #ShortAnime #AnimeTikTok #AnimeFunny #TopAnime #AnimeAddicts",
        },
    ],
    "luffyniista": [
        {
            "name": "op_power",
            "tags": "#OnePiece #Luffy #GearFifth #Nakama #PirateKing #MonkeyDLuffy #OnePieceFan #AnimeEspanol #OtakuEspanol #OnePieceAnime",
        },
        {
            "name": "op_meme",
            "tags": "#OnePieceMemes #AnimeMemes #LuffyMeme #ZoroMeme #NamiMeme #OtakuMeme #AnimeHumor #StrawHatMeme #OnePieceFunny #SanjiFan",
        },
        {
            "name": "op_fandom",
            "tags": "#OnePieceCommunity #StrawHatPirates #ZoroFan #NamiFan #SanjiFan #RobinFan #ChopperFan #FrankyFan #BrookFan #AnimeLatino",
        },
        {
            "name": "op_hype",
            "tags": "#GearFive #JoyBoy #ImuSama #OnePieceEgghead #OnePieceWano #BigMom #Kaido #Shanks #OnePieceViral #TopAnime",
        },
        {
            "name": "op_mix",
            "tags": "#Anime #AnimeClips #AnimeCommunity #OtakuWorld #AnimeViral #ShortAnime #AnimeFunny #ViralAnime #AnimeAddicts #AnimeReels",
        },
    ],
    "sr._shanks": [
        {
            "name": "shanks_power",
            "tags": "#Shanks #OnePiece #RedHairShanks #EmperorShanks #YonkoShanks #RedHairPirates #AnimeEspanol #OtakuEspanol #OnePieceFan #ShanksFan",
        },
        {
            "name": "shanks_meme",
            "tags": "#ShanksMeme #OnePieceMemes #AnimeMemes #OtakuMeme #AnimeHumor #ShanksYonko #HakiShanks #ConquerorHaki #OnePieceFunny #AnimeFan",
        },
        {
            "name": "shanks_fandom",
            "tags": "#OnePieceCommunity #ShanksFan #YonkoCrew #RedHairCrew #BenBeckman #LuckyRoux #YasosCaptain #ShanksMoment #AnimeLatino #OtakuLatino",
        },
        {
            "name": "shanks_hype",
            "tags": "#ShanksVsGorosei #ShanksSecret #ImuShanks #GodShanks #OnePieceEgghead #ShanksTheory #OnePieceViral #TopAnime #ViralAnime #AnimeReels",
        },
        {
            "name": "shanks_mix",
            "tags": "#Anime #AnimeClips #AnimeCommunity #OtakuWorld #AnimeViral #ShortAnime #AnimeFunny #OnePieceClips #AnimeAddicts #PirateAnime",
        },
    ],
    "toonyy.chopper": [
        {
            "name": "chopper_power",
            "tags": "#Chopper #TonyTonyChopper #OnePiece #RumbleBall #MonsterPoint #StrawHatPirates #AnimeEspanol #OtakuEspanol #ChopperFan #OnePieceFan",
        },
        {
            "name": "chopper_meme",
            "tags": "#ChopperMeme #OnePieceMemes #AnimeMemes #OtakuMeme #AnimeHumor #ChopperCute #ChopperFunny #OnePieceFunny #AnimeCute #AnimeWaifu",
        },
        {
            "name": "chopper_fandom",
            "tags": "#OnePieceCommunity #ChopperFan #DrHiruluk #DoctorinaTonTon #ChopperMoment #AnimeLatino #OtakuLatino #AnimeFandom #StrawHatCrew #NakamaCrew",
        },
        {
            "name": "chopper_hype",
            "tags": "#ChopperViral #ChopperMonster #OnePieceClips #AnimeReels #TopAnime #ViralAnime #AnimeViral #OtakuWorld #AnimeAddicts #AnimeCommunity",
        },
        {
            "name": "chopper_mix",
            "tags": "#Anime #AnimeClips #AnimeCommunity #OtakuWorld #AnimeViral #ShortAnime #AnimeFunny #AnimeCute #AnimeAddicts #PirateAnime",
        },
    ],
}

# Fallback si la cuenta no tiene presets definidos
_DEFAULT_PRESETS = HASHTAG_PRESETS["luffyniista"]

# Mapeo día-semana ISO (lunes=0) → índice de preset (0-4)
# Sábado(5) y domingo(6) reutilizan preset4 (índice 4)
_DAY_TO_PRESET_INDEX = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 4, 6: 4}


def get_hashtags_for_today(account: str, today: date | None = None) -> dict:
    """
    Retorna el preset de hashtags correspondiente al día actual.

    Returns:
        {
            "preset_name": str,
            "hashtags": str,
            "day_of_week": int,   # 0=lunes
            "week_number": int,
        }
    """
    if today is None:
        today = date.today()

    presets = HASHTAG_PRESETS.get(account, _DEFAULT_PRESETS)
    day_index = _DAY_TO_PRESET_INDEX[today.weekday()]
    preset = presets[day_index]
    week_number = today.isocalendar().week

    log_hashtag_rotation(account, preset["name"], week_number)

    result = {
        "preset_name": preset["name"],
        "hashtags": preset["tags"],
        "day_of_week": today.weekday(),
        "week_number": week_number,
    }
    logger.info(f"[HashtagRotator] @{account} → preset '{preset['name']}' (día {today.weekday()}, semana {week_number})")
    return result


def get_all_presets(account: str) -> list:
    return HASHTAG_PRESETS.get(account, _DEFAULT_PRESETS)


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    for acc in HASHTAG_PRESETS:
        info = get_hashtags_for_today(acc)
        print(f"@{acc}: [{info['preset_name']}] {info['hashtags'][:60]}...")
