import requests

# 1. Reemplaza con tus credenciales reales
APP_ID = "1732371876763735"
CLIENT_SECRET = "wTWeFAlmktaBuTsdg96lCml1nNH6wIIy"
AUTH_CODE = "TG-69b4261a4f1cea00010d0e23-1410231298" 

def generate_tokens():
    url = "https://api.mercadolibre.com/oauth/token"
    
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
        print("\n=== EXITO: GUÁRDATE ESTOS DATOS ===")
        print(f"Access Token: {data.get('access_token')}")
        print(f"Refresh Token: {data.get('refresh_token')}")
        print("===================================\n")
    else:
        print(f"\nERROR {response.status_code}: El código TG- probablemente expiró o hay un error de tipeo.")
        print(response.text)

if __name__ == "__main__":
    generate_tokens()