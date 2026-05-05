"""
GET_IG_USER_IDS.PY
Obtiene los IG User IDs faltantes usando Graph API
Copia-pega directamente los 3 IDs en config.py
"""

import requests
import json
from config import META_ACCESS_TOKEN, INSTAGRAM_ACCOUNTS

print("\n" + "="*70)
print("OBTENIENDO IG USER IDs FALTANTES")
print("="*70 + "\n")

# ============================================================================
# 1. OBTENER PÁGINAS FACEBOOK VINCULADAS
# ============================================================================
print("[1/2] Obteniendo páginas Facebook vinculadas...\n")

url_pages = "https://graph.facebook.com/v19.0/me/accounts"
params = {"access_token": META_ACCESS_TOKEN}

try:
    response = requests.get(url_pages, params=params)
    response.raise_for_status()
    pages_data = response.json()
    pages = pages_data.get("data", [])
    
    if not pages:
        print("❌ No hay páginas Facebook vinculadas. Ve a Meta Business Suite y vincula las cuentas.")
        exit(1)
    
    print(f"✅ Encontradas {len(pages)} página(s):\n")
    
    pages_map = {}
    for i, page in enumerate(pages, 1):
        page_id = page["id"]
        page_name = page["name"]
        pages_map[page_id] = page_name
        print(f"   [{i}] {page_name:<30} → ID: {page_id}")
    
    print()

except Exception as e:
    print(f"❌ Error obteniendo páginas: {e}")
    exit(1)

# ============================================================================
# 2. OBTENER IG USER IDs
# ============================================================================
print("[2/2] Obteniendo IG User IDs para cada página...\n")

ig_ids = {}

for page_id, page_name in pages_map.items():
    url_ig = f"https://graph.instagram.com/v19.0/{page_id}"
    params = {
        "fields": "instagram_business_account",
        "access_token": META_ACCESS_TOKEN
    }
    
    try:
        response = requests.get(url_ig, params=params)
        response.raise_for_status()
        data = response.json()
        
        ig_account = data.get("instagram_business_account", {})
        ig_user_id = ig_account.get("id")
        
        if ig_user_id:
            ig_ids[page_name] = ig_user_id
            print(f"   ✅ {page_name:<30} → IG ID: {ig_user_id}")
        else:
            print(f"   ⚠️  {page_name:<30} → No vinculada a Instagram")
    
    except Exception as e:
        print(f"   ❌ Error en {page_name}: {e}")

print("\n" + "="*70)
print("RESULTADOS — COPIA ESTOS IDs EN config.py")
print("="*70 + "\n")

# Mapeo de páginas a cuentas (ajusta según tus nombres)
cuenta_mapping = {
    "Luffyniista": "luffyniista",
    "Toonyy Chopper": "toonyy.chopper",
    "Sr Shanks": "sr._shanks",
}

for page_name, cuenta_nombre in cuenta_mapping.items():
    if page_name in ig_ids:
        ig_id = ig_ids[page_name]
        print(f"   {cuenta_nombre}:")
        print(f"      'ig_user_id': '{ig_id}',")
    else:
        print(f"   ⚠️  {page_name} (para {cuenta_nombre}): NO ENCONTRADA")

print("\n" + "="*70)
print("¿FALTA ALGUNA PÁGINA?")
print("="*70)
print("""
1. Ve a Meta Business Suite → https://business.facebook.com
2. Configura → Cuentas de Instagram
3. Vincula las cuentas @toonyy.chopper y @sr._shanks (crear página si es necesario)
4. Vuelve a ejecutar este script
""")
