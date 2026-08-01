@echo off
REM ============================================================
REM  Build del instalable de Windows (ejecutar EN Windows)
REM  Requisitos: Python 3.9+ instalado y en el PATH
REM ============================================================

echo [1/4] Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install yt-dlp pyinstaller

echo [2/4] Descargando ffmpeg para Windows...
if not exist bin mkdir bin
powershell -Command "Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile '%TEMP%\ffmpeg.zip'"
powershell -Command "Expand-Archive -Force '%TEMP%\ffmpeg.zip' '%TEMP%\ffmpeg'"
for /r "%TEMP%\ffmpeg" %%f in (ffmpeg.exe) do copy "%%f" bin\ffmpeg.exe

echo [3/4] Compilando la app...
python -m PyInstaller --noconfirm YouTubeDownloader.spec

echo [4/4] Listo. El ejecutable esta en: dist\YouTubeDownloader.exe
echo Puedes distribuir ese unico .exe (ffmpeg va incluido dentro).
pause
