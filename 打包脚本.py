import PyInstaller.__main__
import os

项目目录 = os.path.dirname(os.path.abspath(__file__))
src目录 = os.path.join(项目目录, "src")

PyInstaller.__main__.run([
    os.path.join(项目目录, "main.py"),
    "--name=自动操作工具",
    f"--paths={项目目录}",
    "--windowed",
    "--onefile",
    "--noconfirm",
    "--clean",
    "--hidden-import=pynput.keyboard._win32",
    "--hidden-import=pynput.mouse._win32",
    "--hidden-import=rapidocr",
    "--hidden-import=pyautogui",
    "--hidden-import=APScheduler",
    "--hidden-import=pyperclip",
    "--hidden-import=PIL",
    f"--distpath={项目目录}",
    f"--workpath={os.path.join(项目目录, 'build')}",
    f"--specpath={项目目录}",
])
