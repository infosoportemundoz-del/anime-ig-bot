import logging
import subprocess
import traceback
from pathlib import Path
from config import DOWNLOADS_DIR, EDITED_DIR, FFMPEG_PATH, INSTAGRAM_ACCOUNTS

logger = logging.getLogger(__name__)

def editar_video(input_path, output_path, watermark_path=None):
    input_path = str(input_path)
    output_path = str(output_path)
    if watermark_path and Path(watermark_path).exists():
        filter_complex = "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[vid];[1:v]scale=200:-1[wm];[vid][wm]overlay=W-w-30:30[out]"
        cmd = [FFMPEG_PATH, "-y", "-i", input_path, "-i", str(watermark_path), "-filter_complex", filter_complex, "-map", "[out]", "-map", "0:a?", "-t", "60", "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", "-b:a", "128k", output_path]
    else:
        cmd = [FFMPEG_PATH, "-y", "-i", input_path, "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", "-t", "60", "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", "-b:a", "128k", output_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.returncode == 0
    except Exception as e:
logger.error(f"\u274c ERROR CRÍTICO editando video: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            logger.error("\u274c Este video NO será publicado")return False

def editar_videos_cuenta(cuenta):
    download_dir = DOWNLOADS_DIR / cuenta
    edited_dir = EDITED_DIR / cuenta
    edited_dir.mkdir(parents=True, exist_ok=True)
    if not download_dir.exists():
        return 0
    config = INSTAGRAM_ACCOUNTS.get(cuenta, {})
    watermark = config.get("watermark", "")
    watermark_path = Path(watermark) if watermark and Path(watermark).exists() else None
    pendientes = list(download_dir.glob("*.mp4"))
    if not pendientes:
        return 0
    logger.info(f"\nEditando {len(pendientes)} videos de @{cuenta}...")
    editados = 0
    for video in pendientes:
        output = edited_dir / video.name
        if output.exists():
            continue
        logger.info(f"  Editando {video.name}...")
        if editar_video(video, output, watermark_path):
            editados += 1
            try:
                video.unlink()
            except Exception:
                pass
    logger.info(f"Editados {editados} videos de @{cuenta}")
    return editados

def editar_todos_pendientes():
    total = 0
    for cuenta in INSTAGRAM_ACCOUNTS.keys():
        config = INSTAGRAM_ACCOUNTS[cuenta]
        ig_id = config.get("ig_user_id", "")
        if not ig_id:
            continue
        total += editar_videos_cuenta(cuenta)
    return total

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    editar_todos_pendientes()
