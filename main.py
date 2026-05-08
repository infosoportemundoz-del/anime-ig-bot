import argparse
import sys
import logging
from config import LOG_FILE

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ahora", action="store_true")
    parser.add_argument("--continuo", action="store_true")
    parser.add_argument("--descargar", action="store_true")
    parser.add_argument("--editar", action="store_true")
    parser.add_argument("--publicar", action="store_true")
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        args.continuo = True
    
    if args.descargar:
        from downloader import descargar_pendientes
        descargar_pendientes()
        return
    if args.editar:
        from editor import editar_todos_pendientes
        editar_todos_pendientes()
        return
    if args.publicar:
        from publisher import publicar_uno_por_cuenta
        publicar_uno_por_cuenta()
        return
    if args.ahora:
        logger.info("MODO AHORA")
        from downloader import descargar_pendientes
        from editor import editar_todos_pendientes
        from publisher import publicar_uno_por_cuenta
        logger.info("[1/3] Descargando...")
        descargar_pendientes()
        logger.info("[2/3] Editando...")
        editar_todos_pendientes()
        logger.info("[3/3] Publicando...")
        publicar_uno_por_cuenta()
        logger.info("CICLO COMPLETADO")
        return
    if args.continuo:
        from scheduler import iniciar_scheduler
        iniciar_scheduler()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
