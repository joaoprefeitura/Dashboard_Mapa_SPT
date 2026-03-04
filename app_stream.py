import streamlit as st
import pandas as pd
import os
import folium
from streamlit_folium import st_folium
# Nova importação para ler PDFs com segurança na nuvem
from streamlit_pdf_viewer import pdf_viewer 

st.set_page_config(layout="wide", page_title="Dashboard de Locais")

DIRETORIO_BASE = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def carregar_dados():
    caminho_csv = os.path.join(DIRETORIO_BASE, 'locais.csv')
    try:
        df = pd.read_csv(caminho_csv, sep=';', encoding='utf-8-sig')
    except Exception as e:
        st.error(f"Erro ao ler o ficheiro CSV: {e}")
        return pd.DataFrame()

    if 'lat' in df.columns and 'lng' in df.columns:
        df['lat'] = df['lat'].astype(str).str.replace(',', '.').astype(float)
        df['lng'] = df['lng'].astype(str).str.replace(',', '.').astype(float)
        df = df.rename(columns={'lng': 'lon'})
        
    return df

# Função atualizada usando a nova biblioteca
def mostrar_pdf(caminho_arquivo):
    if os.path.exists(caminho_arquivo):
        
        # O pdf_viewer faz todo o trabalho pesado de renderizar o PDF de forma segura
        pdf_viewer(caminho_arquivo, width=700, height=800)
        
        # Mantém o botão de download por garantia e conveniência
        with open(caminho_arquivo, "rb") as f:
            st.download_button(
                label="📥 Descarregar PDF Original",
                data=f.read(),
                file_name=os.path.basename(caminho_arquivo),
                mime="application/pdf"
            )
    else:
        st.warning(f"⚠️ O ficheiro PDF não foi encontrado: {caminho_arquivo}")

# =========================================================
# INTERFACE DO DASHBOARD
# =========================================================

st.title("📍 Dashboard de Análise de Locais (Google Satélite)")

df = carregar_dados()

if not df.empty:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🗺️ Mapa Interativo")
        st.write("Clique num marcador vermelho para carregar os dados.")
        
        m = folium.Map(
            tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
            attr="Google Satellite"
        )
        
        for idx, row in df.iterrows():
            folium.Marker(
                location=[row['lat'], row['lon']],
                tooltip=row['nome'],
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)
            
        limites = df[['lat', 'lon']].values.tolist()
        m.fit_bounds(limites)
            
        mapa_dados = st_folium(m, width=700, height=600)
        
        local_selecionado = None
        if mapa_dados and mapa_dados.get("last_object_clicked_tooltip"):
            local_selecionado = mapa_dados["last_object_clicked_tooltip"]

    with col2:
        st.subheader("📄 Detalhes e PDF")
        
        if local_selecionado:
            dados_local = df[df['nome'] == local_selecionado].iloc[0]
            
            st.success(f"**Local Selecionado:** {dados_local['nome']}")
            st.info(f"**Comentário:** {dados_local['comentario']}\n\n**Coordenadas:** {dados_local['lat']}, {dados_local['lon']}")
            
            nome_pdf = dados_local['pdf']
            caminho_pdf = os.path.join(DIRETORIO_BASE, 'pdf', nome_pdf)
            
            mostrar_pdf(caminho_pdf)
        else:
            st.info("👈 Selecione um ponto no mapa ao lado para visualizar o PDF e os comentários.")
else:
    st.error("Não foi possível carregar os dados do ficheiro 'locais.csv'.")