import streamlit as st
import pandas as pd
import base64
import os
import folium
from streamlit_folium import st_folium

# 1. Configuração inicial da página
st.set_page_config(layout="wide", page_title="Dashboard de Locais")

# 2. Descobre a pasta raiz (onde este script está rodando) para ser portátil
DIRETORIO_BASE = os.path.dirname(os.path.abspath(__file__))

# 3. Função para carregar os dados do CSV (usando cache para ficar rápido)
@st.cache_data
def carregar_dados():
    caminho_csv = os.path.join(DIRETORIO_BASE, 'locais.csv')
    
    try:
        df = pd.read_csv(caminho_csv, sep=';', encoding='utf-8-sig')
    except Exception as e:
        st.error(f"Erro ao ler o arquivo CSV: {e}")
        return pd.DataFrame()

    # Tratamento para transformar as vírgulas em pontos e converter para números
    if 'lat' in df.columns and 'lng' in df.columns:
        df['lat'] = df['lat'].astype(str).str.replace(',', '.').astype(float)
        df['lng'] = df['lng'].astype(str).str.replace(',', '.').astype(float)
        df = df.rename(columns={'lng': 'lon'}) # Padroniza como 'lon'
        
    return df

# 4. Função para exibir o PDF na tela
def mostrar_pdf(caminho_arquivo):
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ O arquivo PDF correspondente não foi encontrado no caminho: {caminho_arquivo}")

# =========================================================
# INTERFACE DO DASHBOARD
# =========================================================

st.title("📍 Dashboard de Análise de Locais (Google Satélite)")

df = carregar_dados()

if not df.empty:
    # Cria duas colunas: a da esquerda para o mapa, a da direita para o PDF
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🗺️ Mapa Interativo")
        st.write("Clique em um marcador vermelho para carregar os dados e o PDF do ensaio.")
        
        # Cria o mapa base usando o Satélite do Google (sem zoom fixo inicial)
        m = folium.Map(
            tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
            attr="Google Satellite"
        )
        
        # Adiciona os marcadores lendo linha por linha do DataFrame
        for idx, row in df.iterrows():
            folium.Marker(
                location=[row['lat'], row['lon']],
                tooltip=row['nome'], # O nome vira a "chave" para sabermos qual foi clicado
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)
            
        # Pega a lista com todas as coordenadas [lat, lon] e manda o mapa focar nelas
        limites = df[['lat', 'lon']].values.tolist()
        m.fit_bounds(limites)
            
        # Renderiza o mapa e guarda as interações do usuário na variável 'mapa_dados'
        mapa_dados = st_folium(m, width=700, height=600)
        
        # Verifica se algum pino foi clicado
        local_selecionado = None
        if mapa_dados and mapa_dados.get("last_object_clicked_tooltip"):
            local_selecionado = mapa_dados["last_object_clicked_tooltip"]

    with col2:
        st.subheader("📄 Detalhes e PDF")
        
        # Se houve clique em um local, mostra as informações dele
        if local_selecionado:
            # Filtra o DataFrame para achar a linha do local clicado
            dados_local = df[df['nome'] == local_selecionado].iloc[0]
            
            st.success(f"**Local Selecionado:** {dados_local['nome']}")
            st.info(f"**Comentário:** {dados_local['comentario']}\n\n**Coordenadas:** {dados_local['lat']}, {dados_local['lon']}")
            
            # Monta o caminho da pasta pdf junto com o nome do arquivo que está no CSV
            nome_pdf = dados_local['pdf']
            caminho_pdf = os.path.join(DIRETORIO_BASE, 'pdf', nome_pdf)
            
            # Chama a função para exibir o PDF
            mostrar_pdf(caminho_pdf)
        else:
            # Mensagem que aparece enquanto nenhum pino foi clicado
            st.info("👈 Selecione um ponto no mapa ao lado para visualizar o PDF e os comentários.")
else:
    st.error("Não foi possível carregar os dados do arquivo 'locais.csv'. Verifique se ele está na mesma pasta do programa.")