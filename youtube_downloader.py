#!/usr/bin/env python3
"""App de escritorio simple para descargar videos de YouTube desde el portapapeles."""

import os
import re
import sys
import shutil
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from yt_dlp import YoutubeDL

YT_REGEX = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/\S+")


def find_ffmpeg():
    """Busca ffmpeg: primero junto al ejecutable/empaquetado, luego en el PATH."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    exe = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    for path in (os.path.join(base, exe), os.path.join(base, "bin", exe)):
        if os.path.isfile(path):
            return os.path.dirname(path)
    found = shutil.which(exe)
    return os.path.dirname(found) if found else None


FFMPEG_DIR = find_ffmpeg()


class App:
    def __init__(self, root):
        self.root = root
        root.title("YouTube Downloader")
        root.geometry("560x300")
        root.resizable(False, False)

        self.dest = os.path.join(os.path.expanduser("~"), "Downloads")

        pad = {"padx": 12, "pady": 6}

        # URL
        tk.Label(root, text="URL de YouTube:").pack(anchor="w", **pad)
        row = tk.Frame(root)
        row.pack(fill="x", padx=12)
        self.url_var = tk.StringVar()
        self.entry = tk.Entry(row, textvariable=self.url_var)
        self.entry.pack(side="left", fill="x", expand=True)
        tk.Button(row, text="Pegar", command=self.paste).pack(side="left", padx=(6, 0))

        # Formato
        opts = tk.Frame(root)
        opts.pack(fill="x", **pad)
        tk.Label(opts, text="Formato:").pack(side="left")
        self.fmt = tk.StringVar(value="video")
        tk.Radiobutton(opts, text="Video (MP4)", variable=self.fmt, value="video",
                       command=self.toggle_quality).pack(side="left")
        tk.Radiobutton(opts, text="Solo audio (MP3)", variable=self.fmt, value="audio",
                       command=self.toggle_quality).pack(side="left")

        # Calidad
        self.QUALITIES = {"Máxima": 0, "1080p": 1080, "720p": 720, "480p": 480, "360p": 360}
        self.quality_lbl = tk.Label(opts, text="   Calidad:")
        self.quality_lbl.pack(side="left")
        self.quality = ttk.Combobox(opts, state="readonly", width=8,
                                    values=list(self.QUALITIES.keys()))
        self.quality.set("Máxima")
        self.quality.pack(side="left")

        # Carpeta destino
        drow = tk.Frame(root)
        drow.pack(fill="x", **pad)
        self.dest_var = tk.StringVar(value=self.dest)
        tk.Label(drow, text="Guardar en:").pack(side="left")
        tk.Label(drow, textvariable=self.dest_var, fg="#555").pack(side="left", padx=6)
        tk.Button(drow, text="Cambiar", command=self.choose_dir).pack(side="right")

        # Descargar
        self.btn = tk.Button(root, text="Descargar", command=self.start, height=2, bg="#cc0000", fg="white")
        self.btn.pack(fill="x", padx=12, pady=(10, 6))

        # Progreso
        self.progress = ttk.Progressbar(root, mode="determinate", maximum=100)
        self.progress.pack(fill="x", padx=12)
        self.status = tk.StringVar(value="Listo.")
        tk.Label(root, textvariable=self.status, fg="#555").pack(anchor="w", padx=12, pady=4)

        # Autopegar si el portapapeles tiene una URL de YouTube
        self.paste(silent=True)

        if not FFMPEG_DIR:
            self.status.set("Listo. (ffmpeg no encontrado: MP3 y máxima calidad no disponibles)")

    def paste(self, silent=False):
        try:
            clip = self.root.clipboard_get().strip()
        except tk.TclError:
            clip = ""
        if YT_REGEX.search(clip):
            self.url_var.set(clip)
        elif not silent:
            messagebox.showinfo("Portapapeles", "No hay una URL de YouTube en el portapapeles.")

    def toggle_quality(self):
        state = "readonly" if self.fmt.get() == "video" else "disabled"
        self.quality.config(state=state)

    def choose_dir(self):
        d = filedialog.askdirectory(initialdir=self.dest_var.get())
        if d:
            self.dest = d
            self.dest_var.set(d)

    def start(self):
        url = self.url_var.get().strip()
        if not YT_REGEX.search(url):
            messagebox.showerror("Error", "Introduce una URL de YouTube válida.")
            return
        # Datos leídos en el hilo PRINCIPAL (tkinter no es seguro entre hilos)
        kind = self.fmt.get()
        quality = self.quality.get()
        dest = self.dest_var.get()
        self._state = None      # progreso publicado por el hilo de descarga
        self._result = None     # ("ok", None) | ("error", mensaje)
        self._bar_mode = "indeterminate"
        self.btn.config(state="disabled")
        self.progress.config(mode="indeterminate")
        self.progress.start(12)
        self.status.set("Obteniendo información del video…")
        threading.Thread(target=self.download, args=(url, kind, quality, dest),
                         daemon=True).start()
        self._poll()            # el hilo principal refresca la UI cada 200 ms

    @staticmethod
    def _mb(n):
        return f"{n / 1024 / 1024:.0f} MB" if n else "?"

    def hook(self, d):
        """Se ejecuta en el hilo de descarga: NO toca tkinter, solo publica datos."""
        try:
            st = d.get("status")
            if st == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                done = d.get("downloaded_bytes") or 0
                speed = d.get("speed") or 0
                eta = d.get("eta")
                pct = done / total * 100 if total else None
                spd = f"{speed / 1024 / 1024:.1f} MB/s" if speed else "…"
                if eta:
                    eta = int(eta)
                    eta_s = f" · faltan {eta // 60}m {eta % 60:02d}s"
                else:
                    eta_s = ""
                pct_s = f"{pct:.1f}%" if pct is not None else "…"
                txt = f"Descargando {pct_s}  ({self._mb(done)} de {self._mb(total)}) · {spd}{eta_s}"
                self._state = {"phase": "downloading", "pct": pct, "pct_s": pct_s, "txt": txt}
            elif st == "finished":
                self._state = {"phase": "merging",
                               "txt": "Uniendo audio y video… (puede tardar)"}
        except Exception:
            pass  # nunca dejar que un fallo del hook rompa la descarga

    def _poll(self):
        """Se ejecuta en el hilo PRINCIPAL: lee lo publicado y actualiza la UI."""
        s = self._state
        if s:
            if s["phase"] == "downloading" and s["pct"] is not None:
                if self._bar_mode != "determinate":
                    self.progress.stop()
                    self.progress.config(mode="determinate")
                    self._bar_mode = "determinate"
                self.progress.config(value=s["pct"])
                self.status.set(s["txt"])
                self.root.title(f"YouTube Downloader — {s['pct_s']}")
            elif s["phase"] == "merging":
                if self._bar_mode != "indeterminate":
                    self.progress.config(mode="indeterminate")
                    self.progress.start(12)
                    self._bar_mode = "indeterminate"
                self.status.set(s["txt"])
        r = self._result
        if r:
            self.progress.stop()
            if r[0] == "ok":
                self.progress.config(mode="determinate", value=100)
                self.status.set("✓ Descarga completada.")
            else:
                self.progress.config(mode="determinate", value=0)
                self.status.set("Error en la descarga.")
                messagebox.showerror("Error", r[1])
            self.btn.config(state="normal")
            self.root.title("YouTube Downloader")
            return  # deja de refrescar
        self.root.after(200, self._poll)

    def download(self, url, kind, quality, dest):
        """Se ejecuta en el hilo de descarga: NO toca tkinter."""
        outtmpl = os.path.join(dest, "%(title)s.%(ext)s")
        if kind == "audio":
            if not FFMPEG_DIR:
                self._result = ("error", "Para descargar MP3 necesitas ffmpeg instalado.")
                return
            opts = {
                "format": "bestaudio/best",
                "outtmpl": outtmpl,
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
                "progress_hooks": [self.hook],
                "quiet": True,
                "no_warnings": True,
            }
        else:
            h = self.QUALITIES.get(quality, 0)
            cap = f"[height<={h}]" if h else ""
            if FFMPEG_DIR:
                # Preferir H.264 (avc1) + m4a: se reproduce nativo y sin "fantasma" en Mac.
                # Si no hay avc1 a esa calidad, cae al mejor disponible (VP9/AV1) y como
                # último recurso a un formato combinado.
                fmt = (
                    f"bestvideo{cap}[vcodec^=avc1][ext=mp4]+bestaudio[ext=m4a]/"
                    f"bestvideo{cap}[ext=mp4]+bestaudio[ext=m4a]/"
                    f"bestvideo{cap}+bestaudio/best{cap}[ext=mp4]/best{cap}"
                )
            else:
                fmt = f"best{cap}[ext=mp4]/best{cap}"
            opts = {
                "format": fmt,
                "outtmpl": outtmpl,
                "merge_output_format": "mp4",
                "progress_hooks": [self.hook],
                "quiet": True,
                "no_warnings": True,
            }
        if FFMPEG_DIR:
            opts["ffmpeg_location"] = FFMPEG_DIR
        try:
            with YoutubeDL(opts) as ydl:
                ydl.download([url])
            self._result = ("ok", None)
        except Exception as e:
            self._result = ("error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
