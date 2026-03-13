import streamlit as st
from backend import Meli_Demand_Engine, Static_Semantic_Bridge, Alibaba_Sourcing_Scraper, Arbitrage_Compiler

# Configure Streamlit page
st.set_page_config(
    page_title="Project Delta: Arbitrage Scanner",
    layout="wide"
)

# Manage state
if "df_final" not in st.session_state:
    st.session_state.df_final = None

# Sidebar Configuration
st.sidebar.title("Configuración del Motor")
limit_input = st.sidebar.slider("Límite de Tendencias a analizar", min_value=5, max_value=50, value=10)
run_pipeline = st.sidebar.button("Ejecutar Escaneo de Arbitraje", type="primary", use_container_width=True)

# Main Panel Layout
st.title("Project Delta: Arbitrage Scanner (Static Mapping)")

if run_pipeline:
    with st.status("Iniciando pipeline...", expanded=True) as status:
        try:
            st.write("Consultando API de Tendencias de ML...")
            meli_data = Meli_Demand_Engine().get_top_opportunities(limit=limit_input)

            if not meli_data:
                st.warning("No se encontraron oportunidades en Mercado Libre.")
                status.update(label="Proceso detenido.", state="error")
            else:
                st.write("Cruzando datos con el Diccionario B2B local...")
                b2b_terms = Static_Semantic_Bridge().translate_terms(meli_data)

                if not b2b_terms:
                    st.warning("Ninguna de las tendencias coincidió con el diccionario B2B local.")
                    status.update(label="Proceso detenido.", state="error")
                else:
                    st.write("Scrapeando Alibaba de forma asíncrona (Playwright)...")
                    alibaba_data = Alibaba_Sourcing_Scraper().scrape_suppliers(b2b_terms)

                    st.write("Compilando reporte de arbitraje...")
                    df_final = Arbitrage_Compiler().generate_dataframe(meli_data, alibaba_data)

                    # Save to session state so it persists on UI interactions
                    st.session_state.df_final = df_final
                    status.update(label="Escaneo completado con éxito.", state="complete")
        except Exception as e:
            st.error(f"Se produjo un error durante la ejecución del pipeline: {e}")
            status.update(label="Error en el escaneo.", state="error")

# Display Results & Export functionality
if st.session_state.df_final is not None:
    st.subheader("Resultados del Arbitraje")

    # Configure DataFrame visualization
    st.dataframe(
        st.session_state.df_final,
        use_container_width=True,
        column_config={
            "MELI_URL": st.column_config.LinkColumn(
                "MELI_URL",
                help="Enlace a los listados de Mercado Libre",
                display_text="Ver en MELI"
            ),
            "Alibaba_URL": st.column_config.LinkColumn(
                "Alibaba_URL",
                help="Enlace al proveedor en Alibaba",
                display_text="Ver Proveedor"
            )
        }
    )

    # Export CSV Button
    csv_data = st.session_state.df_final.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar CSV",
        data=csv_data,
        file_name='project_delta_report.csv',
        mime='text/csv',
    )
