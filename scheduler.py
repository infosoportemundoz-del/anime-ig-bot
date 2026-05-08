import time
import logging
from datetime import datetime
import pytz
import schedule

logger = logging.getLogger(__name__)

MADRID_TZ = pytz.timezone("Europe/Madrid")
UTC_TZ = pytz.utc

# Horarios en hora de MADRID (el bot convierte a UTC automÃ¡ticamente)
HORARIOS_MADRID = ["09:00", "13:00", "16:00", "19:30", "22:30"]
HORAS_DESCARGA = 6


def madrid_hora_a_utc(hora_str):
    """Convierte HH:MM hora Madrid â HH:MM hora UTC (gestiona DST automÃ¡ticamente)"""
    h, m = map(int, hora_str.split(":"))
    ahora = datetime.now(MADRID_TZ)
    t_madrid = MADRID_TZ.localize(datetime(ahora.year, ahora.month, ahora.day, h, m))
    t_utc = t_madrid.astimezone(UTC_TZ)
    return t_utc.strftime("%H:%M")


def ciclo_descarga():
    logger.info("=" * 70)
    logger.info("CICLO DESCARGA")
    logger.info("=" * 70)
    try:
        from downloader import descargar_pendientes
        descargados = descargar_pendientes()
        logger.info(f"Total descargados: {descargados}")
    except Exception as e:
        logger.error(f"Error descargando: {e}")
    try:
        from editor import editar_todos_pendientes
        editados = editar_todos_pendientes()
        logger.info(f"Total editados: {editados}")
    except Exception as e:
        logger.error(f"Error editando: {e}")


def ciclo_publicacion():
    ahora = datetime.now(MADRID_TZ).strftime("%H:%M:%S")
    logger.info("=" * 70)
    logger.info(f"CICLO PUBLICACION - {ahora} (Madrid)")
    logger.info("=" * 70)
    try:
        from publisher import publicar_uno_por_cuenta
        publicados = publicar_uno_por_cuenta()
        logger.info(f"Total publicados: {publicados}")
    except Exception as e:
        logger.error(f"Error publicando: {e}")


def iniciar_scheduler():
    logger.info("=" * 70)
    logger.info("ANIME IG BOT - SCHEDULER 24/7")
    logger.info("=" * 70)
    logger.info(f"Descarga cada {HORAS_DESCARGA}h")
    logger.info(f"Publicacion (Madrid): {', '.join(HORARIOS_MADRID)}")

    # Convertir todos los horarios Madrid â UTC para Railway
    horarios_utc = []
    for hora_madrid in HORARIOS_MADRID:
        hora_utc = madrid_hora_a_utc(hora_madrid)
        horarios_utc.append(hora_utc)
        logger.info(f"   {hora_madrid} Madrid â {hora_utc} UTC (Railway)")

    logger.info("=" * 70)

    # Ejecutar ciclo inicial
    logger.info("\nEjecutando ciclo inicial de descarga...")
    ciclo_descarga()

    # Programar descarga cada N horas
    schedule.every(HORAS_DESCARGA).hours.do(ciclo_descarga)

    # Programar publicaciones en UTC (que es lo que usa Railway)
    for hora_utc in horarios_utc:
        schedule.every().day.at(hora_utc).do(ciclo_publicacion)

    logger.info(f"\nScheduler activo. Tareas programadas:")
    for job in schedule.jobs:
        logger.info(f"   - {job}")

    while True:
        try:
            schedule.run_pending()
            time.sleep(30)
        except KeyboardInterrupt:
            logger.info("\nBot detenido")
            break
        except Exception as e:
            logger.error(f"Error en scheduler: {e}")
            time.sleep(60)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    iniciar_scheduler()
