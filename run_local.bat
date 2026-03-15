@echo off
cd /d "%~dp0spotify_dashboard"

set SPOTIFY_REDIRECT_URI=http://127.0.0.1:8502/callback
set SPOTIFY_CACHE_PATH=%~dp0.spotify_cache

call "%~dp0load_env.bat"

C:\Python314\python.exe -m streamlit run app/main.py --server.port 8502 --server.address 127.0.0.1
