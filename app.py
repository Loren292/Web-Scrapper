import os
import pandas as pd
import streamlit as st

# Import modules from main.py since the backend logic is there
from main import (
    Meli_Demand_Engine,
    LLM_Semantic_Bridge,
    Alibaba_Sourcing_Scraper,
    Arbitrage_Compiler
)

def main() -> None:
    """
    Main function to render the Single Page Application UI with Streamlit.
    """
    # ---------------------------------------------------------
    # 1. Sidebar (Barra Lateral - Configuración)
    # ---------------------------------------------------------
    st.sidebar.title("Configuración del Motor")

    # AI Provider Selection
    ai_provider = st.sidebar.radio(
        "Proveedor de IA",
        ["OpenAI", "Gemini"],
        help="Seleccione el modelo de lenguaje a utilizar para la traducción semántica."
    )

    api_key_label = "OpenAI API Key" if ai_provider == "OpenAI" else "Gemini API Key"
    api_key_help = "Ingrese su clave de API de OpenAI (gpt-4o-mini)." if ai_provider == "OpenAI" else "Ingrese su clave de API de Gemini (1.5 Flash)."

    api_key_input = st.sidebar.text_input(
        api_key_label,
        type="password",
        help=api_key_help
    )

    limit_input = st.sidebar.slider(
        "Límite de Tendencias a analizar",
        min_value=5,
        max_value=50,
        value=10,
        step=1
    )

    ejecutar_boton = st.sidebar.button("Ejecutar Escaneo de Arbitraje", type="primary")

    # ---------------------------------------------------------
    # 2. Main Panel (Panel Central - Ejecución y Logs)
    # ---------------------------------------------------------
    st.title("Project Delta: Arbitrage Scanner")

    # Manejo de Estado (CRÍTICO): Store the DataFrame so it persists across interactions
    if "results_df" not in st.session_state:
        st.session_state.results_df = None

    if ejecutar_boton:
        # Manejo de Errores: Habilitar el pipeline solo si hay API Key
        if not api_key_input:
            st.error(f"Error: Debes ingresar una {api_key_label} válida antes de ejecutar el escaneo.")
        else:
            # Clear previous keys to avoid conflicts, then set the active one
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            if "GEMINI_API_KEY" in os.environ:
                del os.environ["GEMINI_API_KEY"]

            if ai_provider == "OpenAI":
                os.environ["OPENAI_API_KEY"] = api_key_input
            else:
                os.environ["GEMINI_API_KEY"] = api_key_input

            # Feedback en Tiempo Real
            with st.status("Iniciando pipeline...", expanded=True) as status:
                try:
                    # Módulo 1: Motor de Mercado Libre
                    status.update(label="Ejecutando Módulo 1: Analizando tendencias en Mercado Libre...", state="running")
                    meli_engine = Meli_Demand_Engine()
                    meli_data = meli_engine.get_top_opportunities(limit_input)

                    # Módulo 2: Puente Semántico LLM
                    ai_name = "GPT-4o-mini" if ai_provider == "OpenAI" else "Gemini"
                    status.update(label=f"Ejecutando Módulo 2: Traduciendo términos con {ai_name}...", state="running")
                    llm_bridge = LLM_Semantic_Bridge()
                    b2b_terms = llm_bridge.translate_terms(meli_data)

                    # Módulo 3: Scraper de Alibaba
                    # Pasamos headless=True para ejecución desatendida, pero listo para depurar
                    status.update(label="Ejecutando Módulo 3: Scrapeando proveedores en Alibaba...", state="running")
                    alibaba_scraper = Alibaba_Sourcing_Scraper(headless=True)
                    alibaba_data = alibaba_scraper.scrape_suppliers(b2b_terms)

                    # Módulo 4: Compilador de Arbitraje
                    status.update(label="Ejecutando Módulo 4: Compilando resultados de arbitraje...", state="running")
                    compiler = Arbitrage_Compiler()
                    df_final = compiler.generate_dataframe(meli_data, alibaba_data)

                    # Actualizar estado de la sesión con los datos exportados
                    st.session_state.results_df = df_final

                    status.update(label="¡Pipeline completado con éxito!", state="complete", expanded=False)

                except Exception as e:
                    status.update(label="Se encontró un error durante la ejecución.", state="error")
                    st.error(f"Detalles del error: {str(e)}")

    # ---------------------------------------------------------
    # 3. Main Panel (Resultados y Exportación)
    # ---------------------------------------------------------
    if st.session_state.results_df is not None:
        df = st.session_state.results_df

        st.subheader("Resultados del Escáner")

        # UX de Enlaces: Configurar URL para que se rendericen como hipervínculos clickeables
        column_configuration = {
            "MELI_URL": st.column_config.LinkColumn("Enlace MercadoLibre"),
            "Alibaba_URL": st.column_config.LinkColumn("Enlace Alibaba")
        }

        # Mostrar el DataFrame, aplicando configuración de columnas
        st.dataframe(
            df,
            use_container_width=True,
            column_config=column_configuration,
            hide_index=True
        )

        # Botón de descarga para exportar los resultados completos en CSV
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Descargar Reporte CSV",
            data=csv_data,
            file_name="arbitrage_scanner_results.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
