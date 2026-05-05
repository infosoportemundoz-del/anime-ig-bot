# 🚀 ANIME IG BOT — PASOS A SEGUIR

## ✅ PASO 1: Copia los archivos a C:\Users\Dani\Desktop\anime_ig_bot

```
config.py → C:\Users\Dani\Desktop\anime_ig_bot\config.py
publisher.py → C:\Users\Dani\Desktop\anime_ig_bot\publisher.py
scheduler.py → C:\Users\Dani\Desktop\anime_ig_bot\scheduler.py
get_ig_user_ids.py → C:\Users\Dani\Desktop\anime_ig_bot\get_ig_user_ids.py
main.py → C:\Users\Dani\Desktop\anime_ig_bot\main.py
```

## ✅ PASO 2: Rellenar config.py

### 2.1 Meta / Token
```python
META_APP_SECRET = "Copia de developers.facebook.com/apps/AnimeBot/settings/basic"
META_ACCESS_TOKEN = "Token de developers.facebook.com/tools/explorer (App: AnimeBot, Permisos: instagram_basic, instagram_content_publish)"
```

### 2.2 Cloudinary (gratis)
```
1. Ve a https://cloudinary.com/users/register/free
2. Regístrate → Te da CLOUD_NAME, API_KEY, API_SECRET
3. En config.py:
   CLOUDINARY_CLOUD_NAME = "tu_cloud_name"
   CLOUDINARY_API_KEY = "tu_api_key"
   CLOUDINARY_API_SECRET = "tu_api_secret"
```

### 2.3 Telegram (Opcional, para alertas)
```
1. Ve a @BotFather en Telegram
2. /newbot → te da TELEGRAM_BOT_TOKEN
3. Abre el bot y obtén tu TELEGRAM_CHAT_ID (ve a @userinfobot)
4. En config.py:
   TELEGRAM_ENABLED = True
   TELEGRAM_BOT_TOKEN = "token"
   TELEGRAM_CHAT_ID = "tu_id"
```

## ✅ PASO 3: Obtener IG User IDs faltantes

```bash
cd C:\Users\Dani\Desktop\anime_ig_bot
python get_ig_user_ids.py
```

Output:
```
luffyniista → ig_id: 17841XXXXXXXXX
toonyy.chopper → ⚠️ No vinculada (resolver en Meta Business Suite)
sr._shanks → ⚠️ No vinculada (crear página Facebook)
```

Si faltan:
1. Ve a Meta Business Suite → https://business.facebook.com
2. Configura → Cuentas de Instagram
3. Vincula @toonyy.chopper y @sr._shanks
4. Copia los IDs en config.py

## ✅ PASO 4: Prueba 1 ciclo completo

```bash
python main.py --ahora
```

Esto:
- Descarga vídeos de TikTok
- Los edita (9:16, watermark, 60s)
- Publica 1 en cada cuenta

Si todo funciona → ✅

## ✅ PASO 5: Inicia el Scheduler 24/7

```bash
python main.py --continuo
```

Esto publica automáticamente:
- 5 veces/día por cuenta (20 posts diarios totales)
- Horarios: 9:00, 12:00, 17:00, 20:00, 23:00
- Descarga vídeos cada 2 horas
- Edita cada 3 horas

---

## 🔧 COMANDOS ÚTILES

| Comando | Qué hace |
|---------|----------|
| `python main.py --ahora` | 1 ciclo completo (descarga + edita + publica) |
| `python main.py --descargar` | Solo descarga de TikTok |
| `python main.py --editar` | Solo edita vídeos descargados |
| `python main.py --obtener-ids` | Obtiene IG User IDs faltantes |
| `python main.py --continuo` | Scheduler 24/7 (ESTO ES LO QUE NECESITAS) |

---

## ⚠️ PROBLEMAS COMUNES

### "IG User ID no encontrado"
→ Ve a Meta Business Suite, vincula la página Facebook a la cuenta IG

### "Error 400 en publicación"
→ El vídeo excede 60s o el formato está mal. Revisa editor.py

### "Token expirado"
→ Ve a developers.facebook.com/tools/explorer, renueva el token, cópialo en config.py

### "No hay vídeos en la cola"
→ El downloader no descargó. Verifica que TikTok_SEARCH_TERMS esté relleno

### "Error de watermark"
→ Verifica que los archivos PNG estén en C:\Users\Dani\Desktop\anime_ig_bot\watermarks\

---

## 🚀 PRÓXIMO PASO

**Ejecuta ahora:**
```bash
cd C:\Users\Dani\Desktop\anime_ig_bot
python main.py --ahora
```

Si funciona → ejecuta:
```bash
python main.py --continuo
```

**¡Eso es todo!** El bot corre automáticamente. Puedes minimizar la consola y dejarla corriendo.
