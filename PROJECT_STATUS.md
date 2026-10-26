# Project Status — Drink Water Reminder

## Goal

A simple Windows desktop app that pops up every N minutes (default 30) with a
"Please drink water!" message, optionally playing a user-supplied talking-avatar
video. Built for Sasi's own laptop, and shareable as a zip/exe that friends can
run on Windows 10/11 64-bit with no installs.

## Core Decisions/Rules

Do not change these without asking the user first.

- **Scope is deliberately tiny.** Pick an interval, get a popup that says drink
  water. The user said explicitly: "That is the only requirement. Nothing else."
  Don't add features (stats, tracking, accounts) unprompted.
- **Desktop app, not web.** Python + tkinter, packaged with PyInstaller into a
  folder exe. A browser/PWA was rejected: background-tab popups are unreliable.
- **Popup modes:** a user-added video loops with its own sound until the user
  clicks "Done, I drank 💧". There is no auto-close. With no video, show a
  text-only popup and speak the message once with the Windows female TTS voice
  (slow rate, "kind" voice).
- **Generic message text:** "Please drink water!" (no name) so the shared exe
  works for anyone. Sasi's personal video says "Sasi" in its own audio.
- **Video is chosen in the app** (🎬 Add video / Remove video), not by dropping
  files into a folder. It's copied to `%APPDATA%\WaterReminder\reminder_video.<ext>`.
- **Autostart until Stop.** Picking an interval saves it and registers the app in
  `HKCU\...\CurrentVersion\Run` with `--autostart`; Stop clears both. Closing the
  window with ✕ does *not* remove autostart.
- **Target platform:** Windows 10/11 **64-bit only**. The user accepted this
  ("that's enough"). 32-bit, Mac, Linux are out of scope.
- **Content boundaries (assistant-side):** no deepfaked face or voice of real
  people (e.g. making a real actor "say drink water"); no downloading copyrighted
  movie stills/clips; no sexualized images of real people bundled or generated.
  The user supplies their own media; the AI-video route uses an anime/cartoon
  character made in a third-party tool.
- **User's own media is never bundled into the shared zip.**

## Non-Obvious Technical Findings

- `python` on this machine resolves to the Microsoft Store stub (Permission
  denied). Use the `py` launcher (Python 3.14.3, 64-bit only).
- tkinter can't play MP4. The app uses **PyAV** (`av`) to decode frames to PIL
  images, and extracts the audio track to a temp WAV, which it then plays via
  `winmm` `mciSendStringW`. Timing: one `after(delay)` per frame, no A/V sync
  correction (fine for short clips of about 4 s).
- PyInstaller needs `--collect-all av`, or PyAV's DLLs are missing in the exe.
  The resulting folder is about 137 MB and the zip about 57 MB.
- TTS goes through `powershell` + `System.Speech` with `CREATE_NO_WINDOW`, so
  there are no extra deps. The female voice is "Microsoft Zira"; if it's missing,
  `SelectVoiceByHints` is wrapped in try and falls back to the default voice.
  The message is inserted inside single quotes, so a `'` in MESSAGE would break it.
- `mciSendString` opens MP3 and WAV fine (verified with return code 0).
- Autostart command differs when frozen: `sys.executable --autostart` for the
  exe, and `pythonw.exe <script> --autostart` from source. If the exe folder is
  moved, the Run entry goes stale until an interval is picked again.
- The first popup after launch decodes the whole video (~1 s for 4 s at 30 fps);
  later popups reuse the cached frames in `App.video`.
- Wikimedia Commons API (`generator=search`, `prop=imageinfo`) is a quick
  source for freely-licensed images; it needs a User-Agent header.

## Full Roadmap

| Phase | Milestone | Status |
|---|---|---|
| 0 | Review old PWA repo (`Hydro_refil_app-water-`) | Done (not reused) |
| 1 | tkinter app: interval buttons, countdown, popup + TTS | Done |
| 2 | Avatars: drawn cartoon → photos → slideshow GIF | Done, then superseded |
| 3 | Video popup with its own audio (PyAV) | Done |
| 4 | In-app Add/Remove video; text-only fallback | Done |
| 5 | PyInstaller exe + shareable zip (GitHub Release v1.0) | Done |
| 6 | Autostart with Windows until Stop | Done (simulated, not real reboot) |
| 7 | Verify on another laptop / real reboot | Not started |
| 8 | 32-bit build | Deferred (only if a user needs it) |

## Current Status (last updated: 2026-10-26)

**Built:** `water_reminder/water_reminder.py` is the app. The exe is in
`water_reminder/dist/Water Reminder/` and the shareable copy is
`water_reminder/dist/Water Reminder.zip`. The exe is running on Sasi's laptop
with a 30-minute interval, autostart registered, and their video installed in
`%APPDATA%\WaterReminder`.

**Verified:** the source compiles. Video decode gives 122 frames (202×360) plus
4.1 s of WAV audio. The extracted voice played aloud, and the user confirmed
hearing the TTS. The exe launches; `--autostart` starts minimized, resumes the
saved interval, and writes the Run key. `set_autostart(30/None)` round-trips.
The user screenshotted the video popup working in the exe. On 2026-10-26 the
user reported that the looping video works. The repo is **public**. GitHub Release
**v1.0** is published (tag on `desktop-app` @ de249e7) with asset
`Water.Reminder.zip` (GitHub renamed the space to a dot). Its SHA-256 `722d1a5e…`
matches the local `dist/Water Reminder.zip`. Download link:
https://github.com/Jdingara/Hydro_refil_app-water-/releases/download/v1.0/Water.Reminder.zip
Gotcha: the user's first attempt was left as a **draft** (URL
`releases/edit/untagged-…`). Drafts are invisible to the public API, which
returns an empty list or 404, until "Publish release" is clicked.
**Not verified:** a real reboot; any machine other than Sasi's.

**How it got here (and why):**
- The old repo was a browser PWA that depended on a missing push server at
  localhost:3000. It wasn't reused; the user wanted a desktop app.
- The first avatar was a drawn cartoon water drop. The user wanted Rajinikanth:
  two Wikimedia photos were downloaded, then the user asked for "Petta" movie
  style plus his voice. That was declined (copyrighted stills, and deepfaking a
  real person's voice and face), and the Rajinikanth photos were removed.
- The user then asked for a "sexy" South Indian lady in a sari. Instead a
  cartoon sari lady GIF was drawn (`saree_lady_cartoon.gif`). The user supplied
  their own photos (`photos/`), and these were made into a crossfade slideshow
  GIF. The user rejected pictures and wanted an AI talking video. The assistant
  gave a prompt for Hedra or D-ID; the user generated a ~4 s anime sari lady
  video saying "Please drink water, Sasi." That is the current video.
- Folder-based avatar/sound pickup (random choice from `avatars/` and
  `sounds/`) was replaced by the in-app Add video button so the shared exe is
  self-explanatory. Those folders and the helper scripts are now legacy.
- The message changed from "Drink water, please!" to "Please drink water, Sasi."
  and then to generic "Please drink water!" for sharing.
- A temporary "1 min" interval button was added for testing and is still there.
- The video originally played once, held on the last frame, and auto-closed
  after 1 minute. The user saw it in the exe (so exe popup and video playback
  are confirmed working) and asked for it to repeat until Done is clicked. Now
  frames loop, the WAV restarts at frame 0, and Done closes the audio. The
  auto-close was removed for both modes.
- **Git:** `water intake/` is now a git repo whose remote is
  `Jdingara/Hydro_refil_app-water-`, on an orphan branch `desktop-app` (pushed).
  `main` still holds the old PWA. Personal media (`photos/`, `avatars/`,
  `*.mp4`, `*.jfif`), `dist/` and the nested PWA clone are git-ignored. Pushing
  works through Git Credential Manager even though `gh` isn't logged in.

## Open Decisions

- Keep or remove the "1 min" test button before wider sharing?
- Clean up legacy files (`avatars/`, `sounds/`, `photos/`, `make_*.py`,
  `saree_lady_cartoon.gif`, `Start Water Reminder.bat`)? This needs the user's
  OK because `photos/` holds their personal images.
- Add a "your name" field so the TTS/text can greet each user by name (offered,
  not yet chosen).
- Code signing to avoid the "Windows protected your PC" warning (costs money;
  not requested).
- Should ✕ minimize instead of quitting, so reminders don't stop for the session?
- 32-bit build: install 32-bit Python and rebuild only if a recipient needs it.
- After any rebuild, publish a new Release (e.g. v1.1) with the new zip, by hand
  through the website (`gh` isn't logged in, so the assistant can't do it).
- Merge `desktop-app` into `main`? The branch is an orphan (no shared history
  with the PWA on `main`), so it's kept separate for now.

## Repo Structure

```
water intake/
├── CLAUDE.md / AGENTS.md      Pointers for AI tools → read this file first
├── PROJECT_STATUS.md          This file: single source of truth
├── README.md                  How to run/build/share
├── Hydro_refil_app-water-/    Old browser PWA (git clone), unused reference
└── water_reminder/
    ├── water_reminder.py      The app (tkinter UI, timer, popup, video, autostart)
    ├── dist/Water Reminder/   Built exe folder (PyInstaller output)
    ├── dist/Water Reminder.zip  Shareable build
    ├── Start Water Reminder.bat  Legacy launcher for the .py (pre-exe)
    ├── make_saree_avatar.py   Legacy: draws the cartoon sari GIF
    ├── make_slideshow.py      Legacy: builds slideshow GIF from photos/
    ├── saree_lady_cartoon.gif Legacy cartoon avatar
    ├── avatars/               Legacy; holds the original MP4 the user made
    ├── photos/                User's personal images (not used by the app)
    └── sounds/                Legacy, empty

%APPDATA%\WaterReminder\       Runtime data: settings.json, reminder_video.*
HKCU\...\CurrentVersion\Run\WaterReminder   Autostart entry (while running)
```
