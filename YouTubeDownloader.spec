# -*- mode: python ; coding: utf-8 -*-
# Build:  python3 -m PyInstaller YouTubeDownloader.spec
import os, sys

is_win = sys.platform.startswith("win")
ffmpeg_name = "ffmpeg.exe" if is_win else "ffmpeg"
ffmpeg_path = os.path.join("bin", ffmpeg_name)

binaries = [(ffmpeg_path, ".")] if os.path.isfile(ffmpeg_path) else []

a = Analysis(
    ["youtube_downloader.py"],
    pathex=[],
    binaries=binaries,
    datas=[],
    hiddenimports=["yt_dlp"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

if is_win:
    # Windows: un único .exe (onefile) — ahí no hay problema de .app
    exe = EXE(
        pyz, a.scripts, a.binaries, a.datas, [],
        name="YouTubeDownloader",
        debug=False, strip=False, upx=False,
        console=False, disable_windowed_traceback=False,
    )
else:
    # macOS: onedir + .app (onefile+.app crashea con SIGABRT en el arranque)
    exe = EXE(
        pyz, a.scripts, [],
        exclude_binaries=True,
        name="YouTubeDownloader",
        debug=False, strip=False, upx=False,
        console=False, disable_windowed_traceback=False,
    )
    coll = COLLECT(
        exe, a.binaries, a.datas,
        strip=False, upx=False, name="YouTubeDownloader",
    )
    app = BUNDLE(
        coll,
        name="YouTube Downloader.app",
        bundle_identifier="com.rafa.youtubedownloader",
        info_plist={
            "CFBundleShortVersionString": "1.0.0",
            "NSHighResolutionCapable": True,
        },
    )
