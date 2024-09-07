import os, subprocess

os.system('pyinstaller --onefile main.py --name "installmods"')
subprocess.Popen(f"explorer /select, {os.path.realpath('dist/installmods.exe')}")