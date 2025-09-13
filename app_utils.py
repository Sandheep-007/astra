# app_utils.py

import os
import subprocess
import webbrowser
import winreg
import shutil
import difflib

from settings import KNOWN_WEB_APPS

def search_google(query):
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(search_url)

def get_installed_apps():
    apps = {}

    def extract_from_registry(hive, flag):
        try:
            with winreg.OpenKey(hive, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths", 0, flag) as key:
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    subkey = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey) as app_key:
                        try:
                            path = winreg.QueryValueEx(app_key, "")[0]
                            name = os.path.splitext(os.path.basename(path))[0].lower()
                            apps[name] = path
                        except FileNotFoundError:
                            continue
        except Exception:
            pass

    extract_from_registry(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
    extract_from_registry(winreg.HKEY_CURRENT_USER, winreg.KEY_READ)

    return apps

def get_start_menu_shortcuts():
    shortcut_map = {}
    folders = [
        os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs")
    ]

    for folder in folders:
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".lnk"):
                    name = os.path.splitext(file)[0].lower()
                    shortcut_path = os.path.join(root, file)
                    shortcut_map[name] = shortcut_path

    return shortcut_map

def open_app_or_web(app_name):
    app_name = app_name.lower().strip()
    installed_apps = get_installed_apps()
    shortcuts = get_start_menu_shortcuts()

    # 🔸 Special case: Calculator
    if app_name in ["calculator", "calc"]:
        print("🧮 Launching Calculator")
        subprocess.Popen("calc.exe")
        return True

    # 🔸 Registry match
    match = difflib.get_close_matches(app_name, installed_apps.keys(), n=1, cutoff=0.6)
    if match:
        path = installed_apps[match[0]]
        print(f"✅ Opening installed app: {match[0]} → {path}")
        try:
            subprocess.Popen(path)
            return True
        except Exception as e:
            print(f"⚠️ Failed to open installed app: {e}")

    # 🔸 PATH-based
    exe = shutil.which(app_name)
    if exe:
        print(f"✅ Found in PATH → {exe}")
        try:
            subprocess.Popen([exe])
            return True
        except Exception as e:
            print(f"⚠️ Failed to open PATH app: {e}")

    # 🔸 Start Menu shortcut match
    shortcut_match = difflib.get_close_matches(app_name, shortcuts.keys(), n=1, cutoff=0.6)
    if shortcut_match:
        shortcut_path = shortcuts[shortcut_match[0]]
        print(f"🟢 Opening Start Menu shortcut: {shortcut_match[0]} → {shortcut_path}")
        os.startfile(shortcut_path)
        return True

    # 🔸 Substring match
    for name, path in shortcuts.items():
        if app_name in name:
            print(f"🟢 Opening shortcut via substring match: {name} → {path}")
            os.startfile(path)
            return True

    # 🔸 Known web apps
    for name, url in KNOWN_WEB_APPS.items():
        if name in app_name:
            print(f"🌐 Opening known web app: {app_name}")
            webbrowser.open(url)
            return True

    # 🔸 Final fallback
    print(f"🔎 Searching on Google: {app_name}")
    search_google(app_name)
    return False
