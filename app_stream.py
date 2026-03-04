import streamlit as st
import pandas as pd
import base64
import os
import folium
from streamlit_folium import st_folium

# Configuração da página
st.set_page_config(layout="wide", page_title="Dashboard de Locais")

# === O SEGREDO DA PORTABILIDADE ===
# Descobre o caminho absoluto da pasta onde este script (app_stream.py) está salvo
DIRETORIO_BASE = os.path.dirname(os.path.abspath(__file__))

# Função para carregar e tratar os dados
@st.cache_data
def carregar_dados():
    # Constrói o caminho dinâmico para o CSV
    caminho_csv = os.path.join(DIRETORIO_BASE, 'locais.csv')
    
    try:
        df = pd.read_csv(caminho_csv, sep=';', encoding='utf-8-sig')
    except Exception as e:
        st.error(f"Erro ao ler o arquivo CSV: {e}")
        return pd.DataFrame()

    if 'lat' in df.columns and 'lng' in df.columns:
        df['lat'] = df['lat'].astype(str).str.replace(',', '.').astype(float)
        df['lng'] = df['lng'].astype(str).str.replace(',', '.').astype(float)
        df = df.rename(columns={'lng': 'lon'})
        
    return df

# Função para renderizar o PDF
def mostrar_pdf(caminho_arquivo):
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ O arquivo PDF não foi encontrado: {caminho_arquivo}")

# ---------------------------------------------------------
# Interface do Dashboard
# ---------------------------------------------------------
st.title("📍 Dashboard de Análise de Locais (Google Satélite)")

df = carregar_dados()

if not df.empty:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🗺️ Mapa Interativo")
        st.write("Clique em um marcador para carregar os dados.")
        
        # Cria o mapa base (não precisamos mais passar o 'location' nem 'zoom_start' aqui)
        m = folium.Map(
            tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
            attr="Google Satellite"
        )
        
        # Adiciona os marcadores no mapa
        for idx, row in df.iterrows():
            folium.Marker(
                location=[row['lat'], row['lon']],
                tooltip=row['nome'],
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)
            
        # ==========================================
        # O TRUQUE PARA CENTRALIZAR AUTOMATICAMENTE:
        # Pega a lista de todas as coordenadas [lat, lon]
        limites = df[['lat', 'lon']].values.tolist()
        # Manda o mapa se autoajustar para enquadrar todos os pontos
        m.fit_bounds(limites)
        # ==========================================
            
        mapa_dados = st_folium(m, width=700, height=600)

    with col2:
        st.subheader("📄 Detalhes e PDF")
        
        if local_selecionado:
            dados_local = df[df['nome'] == local_selecionado].iloc[0]
            
            st.success(f"**Local Selecionado:** {dados_local['nome']}")
            st.info(f"**Comentário:** {dados_local['comentario']}\n\n**Coordenadas:** {dados_local['lat']}, {dados_local['lon']}")
            
            nome_pdf = dados_local['pdf']
            # Constrói o caminho dinâmico para a pasta de PDFs
            caminho_pdf = os.path.join(DIRETORIO_BASE, 'pdf', nome_pdf)
            
            mostrar_pdf(caminho_pdf)
        else:
            st.info("👈 Selecione um ponto no mapa ao lado para visualizar o PDF e os comentários.")
else:
    st.error("Não foi possível carregar os dados para exibir o mapa.")