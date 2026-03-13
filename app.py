import streamlit as st
import requests
import pandas as pd
import json
import os
import time

# 1. Credentials config
TOKENS_FILE = "tokens.json"

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

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "User-Agent": "ProjectDeltaStockManager/1.0"
    }

def fetch_user_id(token):
    url = "https://api.mercadolibre.com/users/me"
    response = requests.get(url, headers=get_headers(token))

    if response.status_code == 200:
        return response.json().get("id")
    else:
        st.error(f"Error al obtener User ID: {response.status_code} - {response.text}")
        return None

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

def fetch_competitors(query, token):
    url = "https://api.mercadolibre.com/sites/MLA/search"
    params = {
        "q": query,
        "limit": 50
    }

    # We do not use authorization header here to prevent IP blocking
    headers = {
        "User-Agent": "ProjectDeltaStockManager/1.0"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error al buscar competidores: {response.status_code} - {response.text}")
        return None

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


st.title("📦 Gestor de E-Commerce - Mercado Libre")

token = load_access_token()

if not token:
    st.warning("No se encontró un token de acceso válido. Por favor, ejecuta `python get_token.py` para generar uno.")
    st.stop()

tab_stock, tab_research = st.tabs(["Mi Stock", "Investigación de Mercado"])

with tab_stock:
    st.header("Gestor de Stock")
    if st.button("Consultar Mi Stock", type="primary"):
        with st.spinner("Consultando datos del vendedor..."):
            user_id = fetch_user_id(token)

        if user_id:
            with st.spinner(f"Buscando publicaciones para el usuario {user_id}..."):
                item_ids = fetch_seller_items(user_id, token)

            if not item_ids:
                st.info("No tienes publicaciones activas en Mercado Libre.")
            else:
                with st.spinner(f"Obteniendo detalles de {len(item_ids)} publicaciones..."):
                    item_details = fetch_item_details(item_ids, token)

                if item_details:
                    df = pd.DataFrame(item_details)
                    st.success("¡Datos obtenidos con éxito!")

                    # Format dataframe for better UI
                    st.dataframe(
                        df,
                        use_container_width=True,
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

with tab_research:
    st.header("Investigación de Competencia")

    query = st.text_input("Ingresa el producto a investigar:", value="campanas extractoras para cocina")

    if st.button("Buscar Competencia", type="primary"):
        with st.spinner(f"Buscando '{query}' en Mercado Libre..."):
            search_data = fetch_competitors(query, token)

        if search_data:
            total_sellers = search_data.get("paging", {}).get("total", 0)
            results = search_data.get("results", [])

            st.metric("Total de publicaciones encontradas", total_sellers)

            if results:
                competitor_details = []
                for item in results:
                    seller = item.get("seller", {})
                    seller_id = seller.get("id", "N/A")
                    seller_nickname = seller.get("nickname", "N/A")

                    shipping = item.get("shipping", {})
                    free_shipping = "Sí" if shipping.get("free_shipping") else "No"

                    competitor_details.append({
                        "ID": item.get("id"),
                        "Título": item.get("title"),
                        "Precio": item.get("price"),
                        "Vendedor (ID - Nombre)": f"{seller_id} - {seller_nickname}",
                        "Condición": item.get("condition"),
                        "Envío Gratis": free_shipping,
                        "Enlace": item.get("permalink")
                    })

                df_comp = pd.DataFrame(competitor_details)

                # Sort by Price ascending
                df_comp = df_comp.sort_values(by="Precio", ascending=True).reset_index(drop=True)

                st.subheader(f"Top 50 Resultados (Ordenados por Precio)")
                st.dataframe(
                    df_comp,
                    use_container_width=True,
                    column_config={
                        "Precio": st.column_config.NumberColumn("Precio", format="$ %d"),
                        "Enlace": st.column_config.LinkColumn("Enlace ML", display_text="Ver Producto")
                    }
                )

                # Allow download
                csv_comp = df_comp.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Descargar Reporte de Competencia (CSV)",
                    data=csv_comp,
                    file_name='reporte_competencia_ml.csv',
                    mime='text/csv',
                )
            else:
                st.warning("No se encontraron resultados para esta búsqueda.")
