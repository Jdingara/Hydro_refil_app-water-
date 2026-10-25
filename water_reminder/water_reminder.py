"""Drink Water Reminder - pick an interval and get a popup that says "Please drink water!"

Use "Add video" to show your own video (with its sound) in the popup.
Without a video the popup shows the message and Windows speaks it.
"""
import ctypes
import json
import os
import shutil
import subprocess
import sys
import tempfile
import winreg
import tkinter as tk
import wave
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox

from PIL import ImageTk

MESSAGE = "Please drink water!"
VIDEO_SIZE = 360
VIDEO_EXTS = (".mp4", ".mov", ".webm", ".mkv", ".avi")
DATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "WaterReminder")
BG = "#013b5c"
SETTINGS = os.path.join(DATA_DIR, "settings.json")
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_NAME = "WaterReminder"


def saved_minutes():
    try:
        with open(SETTINGS) as f:
            return json.load(f).get("minutes")
    except (OSError, ValueError):
        return None


def set_autostart(minutes):
    """Remember the interval and start with Windows; None forgets it and removes autostart."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SETTINGS, "w") as f:
        json.dump({"minutes": minutes}, f)
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
        if minutes:
            if getattr(sys, "frozen", False):  # running as the exe
                cmd = f'"{sys.executable}" --autostart'
            else:
                pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
                cmd = f'"{pyw}" "{os.path.abspath(__file__)}" --autostart'
            winreg.SetValueEx(k, RUN_NAME, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(k, RUN_NAME)
            except FileNotFoundError:
                pass


def saved_video():
    if os.path.isdir(DATA_DIR):
        for n in os.listdir(DATA_DIR):
            if n.startswith("reminder_video") and n.lower().endswith(VIDEO_EXTS):
                return os.path.join(DATA_DIR, n)
    return None


def speak(text):
    # Windows built-in text-to-speech; runs in background so the UI never freezes
    cmd = ("Add-Type -AssemblyName System.Speech; "
           "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
           "try { $s.SelectVoiceByHints('Female') } catch {}; "
           f"$s.Rate = -2; $s.Speak('{text}')")
    subprocess.Popen(["powershell", "-NoProfile", "-Command", cmd],
                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def play_wav(path):
    mci = ctypes.windll.winmm.mciSendStringW
    mci("close reminder", None, 0, None)
    if mci(f'open "{path}" alias reminder', None, 0, None) == 0:
        mci("play reminder", None, 0, None)
        return True
    return False


def load_video(path):
    """Decode a video into frames plus a temp WAV of its soundtrack."""
    import av

    with av.open(path) as c:
        delay = int(1000 / float(c.streams.video[0].average_rate or 30))
        frames = []
        for f in c.decode(video=0):
            img = f.to_image()
            img.thumbnail((VIDEO_SIZE, VIDEO_SIZE))
            frames.append(img)
    wav = None
    with av.open(path) as c:
        if c.streams.audio:
            rs = av.AudioResampler(format="s16", layout="stereo", rate=44100)
            pcm = b"".join(bytes(o.planes[0])[:o.samples * 4]
                           for f in c.decode(audio=0) for o in rs.resample(f))
            wav = os.path.join(tempfile.gettempdir(), "water_reminder_voice.wav")
            with wave.open(wav, "wb") as w:
                w.setnchannels(2)
                w.setsampwidth(2)
                w.setframerate(44100)
                w.writeframes(pcm)
    return frames, delay, wav


class App:
    def __init__(self, root):
        self.root = root
        self.job = None
        self.next_at = None
        self.popup = None
        self.video = None  # (frames, delay, wav) once loaded
        root.title("Drink Water Reminder")
        root.geometry("360x340")
        root.resizable(False, False)
        root.configure(bg="#024a72")

        tk.Label(root, text="💧 Drink Water Reminder", font=("Segoe UI", 16, "bold"),
                 bg="#024a72", fg="white").pack(pady=(18, 10))
        tk.Label(root, text="Remind me every:", font=("Segoe UI", 11),
                 bg="#024a72", fg="#cdeffc").pack()

        row = tk.Frame(root, bg="#024a72")
        row.pack(pady=10)
        for label, minutes in (("1 min", 1), ("15 min", 15), ("30 min", 30), ("1 hour", 60)):
            tk.Button(row, text=label, width=6, font=("Segoe UI", 11, "bold"),
                      bg="#4dd0e1", relief="flat",
                      command=lambda m=minutes: self.start(m)).pack(side="left", padx=5)

        self.status = tk.Label(root, font=("Segoe UI", 11), bg="#024a72", fg="white")
        self.status.pack(pady=8)

        btns = tk.Frame(root, bg="#024a72")
        btns.pack()
        tk.Button(btns, text="Test popup", command=self.remind, relief="flat",
                  font=("Segoe UI", 10)).pack(side="left", padx=5)
        tk.Button(btns, text="Stop", command=self.stop, relief="flat", bg="#ff6b6b", fg="white",
                  font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)

        vrow = tk.Frame(root, bg="#024a72")
        vrow.pack(pady=(14, 4))
        tk.Button(vrow, text="🎬 Add video", command=self.add_video, relief="flat",
                  font=("Segoe UI", 10)).pack(side="left", padx=5)
        tk.Button(vrow, text="Remove video", command=self.remove_video, relief="flat",
                  font=("Segoe UI", 10)).pack(side="left", padx=5)
        self.video_label = tk.Label(root, font=("Segoe UI", 9), bg="#024a72", fg="#cdeffc")
        self.video_label.pack()

        self.refresh_video_label()
        self.tick()

        minutes = saved_minutes()
        if minutes:  # was running before the restart: carry on
            self.start(minutes)
            if "--autostart" in sys.argv:
                root.iconify()

    # ---- video ----
    def refresh_video_label(self):
        self.video_label.config(text="Popup: your video" if saved_video()
                                else "Popup: text only (no video added)")

    def add_video(self):
        path = filedialog.askopenfilename(
            title="Choose a reminder video",
            filetypes=[("Videos", " ".join("*" + e for e in VIDEO_EXTS))])
        if not path:
            return
        try:
            load_video(path)  # make sure it can be played before saving
        except Exception as e:
            messagebox.showerror("Video", f"Sorry, this video can't be played.\n\n{e}")
            return
        self.remove_video()
        os.makedirs(DATA_DIR, exist_ok=True)
        shutil.copy(path, os.path.join(DATA_DIR, "reminder_video" + os.path.splitext(path)[1].lower()))
        self.refresh_video_label()
        self.remind()

    def remove_video(self):
        old = saved_video()
        if old:
            os.remove(old)
        self.video = None
        self.refresh_video_label()

    # ---- timer ----
    def start(self, minutes):
        self.cancel()
        self.interval_ms = minutes * 60 * 1000
        self.schedule()
        set_autostart(minutes)

    def schedule(self):
        self.next_at = datetime.now() + timedelta(milliseconds=self.interval_ms)
        self.job = self.root.after(self.interval_ms, self.fire)

    def fire(self):
        self.remind()
        self.schedule()

    def stop(self):
        self.cancel()
        set_autostart(None)

    def cancel(self):
        if self.job:
            self.root.after_cancel(self.job)
        self.job = None
        self.next_at = None

    def tick(self):
        if self.next_at:
            left = max(0, int((self.next_at - datetime.now()).total_seconds()))
            self.status.config(text=f"Next reminder in {left // 60:02d}:{left % 60:02d}"
                                    f"  ({self.next_at:%I:%M %p})")
        else:
            self.status.config(text="Not running - pick a time above")
        self.root.after(1000, self.tick)

    # ---- popup ----
    def remind(self):
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()

        path = saved_video()
        if path and not self.video:
            try:
                self.video = load_video(path)
            except Exception:
                self.video = None

        p = self.popup = tk.Toplevel(self.root)
        p.overrideredirect(True)
        p.attributes("-topmost", True)
        p.configure(bg=BG, highlightthickness=3, highlightbackground="#4dd0e1")
        w, h = (340, 500) if self.video else (340, 170)
        p.geometry(f"{w}x{h}+{p.winfo_screenwidth() - w - 20}+{p.winfo_screenheight() - h - 60}")

        pic = tk.Label(p, bg=BG)
        if self.video:
            pic.pack(pady=(14, 4))
        tk.Label(p, text="💧 " + MESSAGE, font=("Segoe UI", 18, "bold"),
                 bg=BG, fg="white").pack(pady=(24 if not self.video else 0, 0))
        tk.Button(p, text="Done, I drank 💧", font=("Segoe UI", 11, "bold"), bg="#4dd0e1",
                  relief="flat", command=p.destroy).pack(pady=12)
        p.after(60_000, lambda: p.winfo_exists() and p.destroy())  # auto-close after 1 min

        if not self.video:
            speak(MESSAGE)
            return

        frames, delay, wav = self.video
        tkframes = [ImageTk.PhotoImage(f) for f in frames]
        if not (wav and play_wav(wav)):
            speak(MESSAGE)

        def animate(i=0):
            if p.winfo_exists():
                pic.config(image=tkframes[i])
                pic.image = tkframes  # keep references alive
                if i < len(tkframes) - 1:  # play once, stay on last frame
                    p.after(delay, animate, i + 1)
        animate()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
