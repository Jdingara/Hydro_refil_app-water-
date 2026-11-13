# Drink Water Reminder

> For the project's goal, rules, history and current status, read
> [PROJECT_STATUS.md](PROJECT_STATUS.md). This README only covers how to run it.

A Windows 10/11 (64-bit) app that pops up "Please drink water!" on a timer.

## Use the app (no install)

1. Download
   [Water.Reminder.zip](https://github.com/Jdingara/Hydro_refil_app-water-/releases/download/v1.0/Water.Reminder.zip)
   (or build it, see below) and unzip it somewhere permanent (e.g. Documents).
2. Double-click `Water Reminder.exe`. If Windows says "Windows protected your
   PC", click **More info → Run anyway**.
3. Click an interval: **15 min**, **30 min** or **1 hour**.
   The app now starts automatically with Windows.
4. Optional: **🎬 Add video** to play your own video, with its sound, in the
   popup. **Remove video** goes back to the text-and-voice popup.
5. The popup (and the video, looping) stays until you click **Done, I drank 💧**,
   or closes by itself after 1 minute.
6. **Stop** ends reminders and turns off start-with-Windows.

| Button | Does |
|---|---|
| Interval buttons | Start the timer, remember it, enable autostart |
| Test popup | Show a reminder now |
| Stop | Stop the timer, disable autostart |
| 🎬 Add video / Remove video | Set or clear the popup video |

Settings and the video are stored in `%APPDATA%\WaterReminder`.

## Troubleshooting

| Problem | Fix |
|---|---|
| App didn't open after restart | Ctrl+Shift+Esc → **Startup apps** → set **Water Reminder** to **Enabled**. Cleanup tools sometimes disable it. |
| Can't find the app in Windows search | From v1.1 the app adds "Drink Water Reminder" to the Start menu the first time it opens; search may take a minute to pick it up. On v1.0, right-click `Water Reminder.exe` → **Pin to Start**. |
| App was closed | Open `Water Reminder.exe` again; it resumes your saved interval. |

## Run from source

Requires Python 3.14 (64-bit) via the `py` launcher.

```powershell
py -m pip install pillow av
py water_reminder\water_reminder.py
```

Command-line flag:

| Flag | Effect |
|---|---|
| `--autostart` | Start minimized (used by the Windows startup entry) |

## Build the exe

```powershell
py -m pip install pyinstaller
cd water_reminder
py -m PyInstaller --noconfirm --windowed --name "Water Reminder" --collect-all av --distpath dist water_reminder.py
Compress-Archive -Force "dist\Water Reminder" "dist\Water Reminder.zip"
```

Close any running `Water Reminder.exe` before rebuilding.
