import streamlit as st
import requests
import pandas as pd
import json
import os
import time

# 1. Credentials config
TOKENS_FILE = "tokens.json"
APP_ID = "1732371876763735"
CLIENT_SECRET = "wTWeFAlmktaBuTsdg96lCml1nNH6wIIy"

st.set_page_config(
    page_title="Gestor de Stock - Mercado Libre",
    layout="wide"
)

def load_access_token():
    if os.path.exists(TOKENS_FILE):
        try:
            with open(TOKENS_FILE, "r") as f:
                tokens = json.load(f)
                return tokens.get("access_token")
        except Exception as e:
            st.error(f"Error leyendo tokens.json: {e}")
    return None

def refresh_access_token_on_fly():
    """Attempts to refresh the token directly using the saved refresh_token."""
    if not os.path.exists(TOKENS_FILE):
        return None

    try:
        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)
            refresh_token = tokens.get("refresh_token")
    except Exception:
        return None

    if not refresh_token:
        return None

    url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "refresh_token",
        "client_id": APP_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        new_access_token = data.get('access_token')
        new_refresh_token = data.get('refresh_token')

        try:
            with open(TOKENS_FILE, "w") as f:
                json.dump({
                    "access_token": new_access_token,
                    "refresh_token": new_refresh_token
                }, f)
            return new_access_token
        except Exception:
            pass
    return None

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "User-Agent": "ProjectDeltaStockManager/1.0"
    }

def fetch_user_id(token):
    url = "https://api.mercadolibre.com/users/me"
    response = requests.get(url, headers=get_headers(token))

    # Refresh on the fly logic
    if response.status_code in [401, 403]:
        new_token = refresh_access_token_on_fly()
        if new_token:
            # Update token and retry
            token = new_token
            response = requests.get(url, headers=get_headers(token))

    if response.status_code == 200:
        return response.json().get("id"), token
    else:
        st.error(f"Error al obtener User ID: {response.status_code} - {response.text}")
        return None, token

def fetch_seller_items(user_id, token):
    url = f"https://api.mercadolibre.com/users/{user_id}/items/search"
    all_items = []
    scroll_id = None

    # We use search endpoint with scroll to get all items if there are many
    # For simplicity, we just fetch the first page here. A robust implementation would loop.
    params = {
        "status": "active",
        "limit": 50 # Max 50 per request
    }

    response = requests.get(url, headers=get_headers(token), params=params)

    if response.status_code == 200:
        data = response.json()
        all_items.extend(data.get("results", []))
        return all_items
    else:
        st.error(f"Error al buscar publicaciones: {response.status_code} - {response.text}")
        return []

def fetch_item_details(item_ids, token):
    """Fetches details for a list of item IDs. Max 20 ids per request."""
    if not item_ids:
        return []

    details = []

    # Chunk the item_ids into groups of 20
    chunk_size = 20
    for i in range(0, len(item_ids), chunk_size):
        chunk = item_ids[i:i + chunk_size]
        ids_str = ",".join(chunk)
        url = f"https://api.mercadolibre.com/items?ids={ids_str}"

        response = requests.get(url, headers=get_headers(token))

        if response.status_code == 200:
            data = response.json()
            # The multi-get API returns a list of objects with "code" and "body"
            for item in data:
                if item.get("code") == 200:
                    body = item.get("body", {})
                    details.append({
                        "ID": body.get("id"),
                        "Título": body.get("title"),
                        "Precio": body.get("price"),
                        "Stock Disponible": body.get("available_quantity"),
                        "Condición": body.get("condition"),
                        "Enlace": body.get("permalink")
                    })
        else:
             st.error(f"Error fetching item details: {response.status_code} - {response.text}")

        time.sleep(0.5) # Sleep to avoid rate limiting

    return details


st.title("📦 Gestor de Stock - Mercado Libre")

token = load_access_token()

if not token:
    st.warning("No se encontró un token de acceso válido. Por favor, ejecuta `python get_token.py` para generar uno.")
    st.stop()

if st.button("Consultar Mi Stock", type="primary"):
    with st.spinner("Consultando datos del vendedor (y refrescando token si es necesario)..."):
        user_id, valid_token = fetch_user_id(token)

    if user_id:
        # Note: We pass valid_token onwards because if it was refreshed on the fly,
        # the initial `token` variable in the script is stale for this run.
        with st.spinner(f"Buscando publicaciones para el usuario {user_id}..."):
            item_ids = fetch_seller_items(user_id, valid_token)

        if not item_ids:
            st.info("No tienes publicaciones activas en Mercado Libre.")
        else:
            with st.spinner(f"Obteniendo detalles de {len(item_ids)} publicaciones..."):
                    item_details = fetch_item_details(item_ids, valid_token)

            if item_details:
                df = pd.DataFrame(item_details)
                st.success("¡Datos obtenidos con éxito!")

                # Format dataframe for better UI
                st.dataframe(
                    df,
                    width='stretch',
                    column_config={
                        "Enlace": st.column_config.LinkColumn("Enlace ML", display_text="Ver Producto")
                    }
                )

                # Allow download
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Descargar Reporte de Stock (CSV)",
                    data=csv,
                    file_name='reporte_stock_ml.csv',
                    mime='text/csv',
                )
            else:
                 st.error("No se pudieron obtener los detalles de las publicaciones.")
