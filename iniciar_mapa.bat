@echo off
echo ===================================================
echo Iniciando o Painel de Ensaios SPT de Matupa...
echo Aguarde um momento, o navegador sera aberto em breve.
echo ===================================================

:: 1. Garante que o CMD "entre" na pasta do projeto
cd /d "%~dp0"

:: 2. Tenta rodar o Streamlit
".\venv\Scripts\streamlit.exe" run app_stream.py


pause