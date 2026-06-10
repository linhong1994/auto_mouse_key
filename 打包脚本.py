import PyInstaller.__main__
import os

项目目录 = os.path.dirname(os.path.abspath(__file__))
src目录 = os.path.join(项目目录, "src")

PyInstaller.__main__.run([
    os.path.join(src目录, "main.py"),
    "--name=自动操作工具",
    f"--paths={src目录}",
    "--windowed",
    "--onefile",
    "--noconfirm",
    "--clean",
    "--hidden-import=pynput.keyboard._win32",
    "--hidden-import=pynput.mouse._win32",
    "--hidden-import=paddleocr",
    "--hidden-import=paddle",
    "--hidden-import=pyautogui",
    "--hidden-import=APScheduler",
    "--hidden-import=pyperclip",
    "--hidden-import=PIL",
    f"--distpath={os.path.join(项目目录, 'dist')}",
    f"--workpath={os.path.join(项目目录, 'build')}",
    f"--specpath={项目目录}",
])
