# Drink Water Reminder

> For the project's goal, rules, history and current status, read
> [PROJECT_STATUS.md](PROJECT_STATUS.md). This README only covers how to run it.

A Windows 10/11 (64-bit) app that pops up "Please drink water!" on a timer.

## Use the app (no install)

1. Unzip `water_reminder/dist/Water Reminder.zip` somewhere permanent
   (e.g. Documents).
2. Double-click `Water Reminder.exe`. If Windows says "Windows protected your
   PC", click **More info → Run anyway**.
3. Click an interval: **1 min**, **15 min**, **30 min** or **1 hour**.
   The app now starts automatically with Windows.
4. Optional: **🎬 Add video** to play your own video, with its sound, in the
   popup. **Remove video** goes back to the text-and-voice popup.
5. **Stop** ends reminders and turns off start-with-Windows.

| Button | Does |
|---|---|
| Interval buttons | Start the timer, remember it, enable autostart |
| Test popup | Show a reminder now |
| Stop | Stop the timer, disable autostart |
| 🎬 Add video / Remove video | Set or clear the popup video |

Settings and the video are stored in `%APPDATA%\WaterReminder`.

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
