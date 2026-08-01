# YouTube Downloader

App de escritorio simple: pega la URL de YouTube y descarga el video (MP4) o el audio (MP3).
Muestra el progreso en vivo (%, MB, velocidad y tiempo restante) y trae ffmpeg incluido.

## Descargar

- **Windows:** ve a la pestaña [Releases](../../releases) y descarga `YouTubeDownloader.exe`.
  La primera vez Windows mostrará *"Windows protegió tu PC"* → pulsa **Más información → Ejecutar de todas formas**
  (es normal en apps sin firmar).
- **macOS:** usa el `YouTube Downloader.dmg`. Clic derecho sobre la app → **Abrir** la primera vez.

## Cómo se compila el .exe (automático, en la nube)

Cada `push` a `main` dispara el workflow [`.github/workflows/build.yml`](.github/workflows/build.yml),
que en un runner de Windows: instala dependencias, descarga ffmpeg, compila con PyInstaller y
publica el `.exe` en **Releases** (y como artefacto en la pestaña **Actions**).
También se puede lanzar a mano desde **Actions → Build Windows → Run workflow**.

## Ejecutar sin compilar (desarrollo)

```
python3 -m pip install yt-dlp
python3 youtube_downloader.py
```
Para MP3 y máxima calidad necesitas `ffmpeg` instalado (o junto al ejecutable).
