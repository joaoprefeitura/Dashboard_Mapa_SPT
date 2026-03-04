@echo off
echo Iniciando o Dashboard...

:: Vai para a pasta exata onde este arquivo .bat está, não importa o disco ou local
cd /d "%~dp0"

:: Roda o Streamlit
python -m streamlit run app_stream.py

pause