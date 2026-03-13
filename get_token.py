import requests
import json
import os

# 1. Reemplaza con tus credenciales reales
APP_ID = "1732371876763735"
CLIENT_SECRET = "wTWeFAlmktaBuTsdg96lCml1nNH6wIIy"
AUTH_CODE = "TG-69b4261a4f1cea00010d0e23-1410231298" 
TOKENS_FILE = "tokens.json"

def get_refresh_token():
    if os.path.exists(TOKENS_FILE):
        try:
            with open(TOKENS_FILE, "r") as f:
                tokens = json.load(f)
                return tokens.get("refresh_token")
        except Exception as e:
            print(f"Error reading tokens.json: {e}")
    return None

def generate_tokens():
    url = "https://api.mercadolibre.com/oauth/token"
    
    refresh_token = get_refresh_token()

    if refresh_token:
        print("Encontrado refresh_token en tokens.json. Intentando refrescar...")
        payload = {
            "grant_type": "refresh_token",
            "client_id": APP_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token
        }
    else:
        print(f"No hay refresh_token válido. Usando AUTH_CODE inicial: {AUTH_CODE}")
        payload = {
            "grant_type": "authorization_code",
            "client_id": APP_ID,
            "client_secret": CLIENT_SECRET,
            "code": AUTH_CODE,
            "redirect_uri": "https://www.google.com" # Debe coincidir exacto
        }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded"
    }
    
    print("Requesting tokens from Mercado Libre...")
    response = requests.post(url, data=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        new_access_token = data.get('access_token')
        new_refresh_token = data.get('refresh_token')

        print("\n=== EXITO: GUÁRDATE ESTOS DATOS ===")
        print(f"Access Token: {new_access_token}")
        print(f"Refresh Token: {new_refresh_token}")
        print("===================================\n")

        # Guardar en tokens.json para que backend.py lo use
        try:
            with open(TOKENS_FILE, "w") as f:
                json.dump({
                    "access_token": new_access_token,
                    "refresh_token": new_refresh_token
                }, f)
            print("Nuevos tokens guardados en tokens.json automáticamente.")
        except Exception as e:
            print(f"Error guardando tokens en tokens.json: {e}")

    else:
        print(f"\nERROR {response.status_code}: El código TG- o el refresh_token expiró.")
        print(response.text)

if __name__ == "__main__":
    generate_tokens()