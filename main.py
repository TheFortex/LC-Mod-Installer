import os, requests, sys, shutil, menu, mods
from defs import *
from globals import __version

# Check for updates

UpdaterBatch = """
@echo off
title Updating LC Mod Installer...
echo Killing process %1...
taskkill /pid %1 /f > nul 2>&1
:wait
tasklist | find /i "installmods.exe" > nul 2>&1
if errorlevel 1 (
	move /Y installmods_new.exe installmods.exe
	start installmods.exe
	exit
) else (
	timeout /t 1 /nobreak > nul
	goto wait
)
"""

while True:
	try:
		print("Checking for updates...")
		response = requests.get("https://api.github.com/repos/TheFortex/LC-Mod-Installer/releases/latest")
		assert response.status_code == 200, f"Response code: {response.status_code}"
		remote_version = int(response.json()["name"].split(" ")[1])

		if remote_version > __version:
			print(f"New version available: {remote_version} (Current: {__version}) - The program will now update.")
			os.system("pause")
			while True:
				try:
					download_url = response.json()["assets"][0]["browser_download_url"]
					response = requests.get(download_url)
					assert response.status_code == 200, f"Response code: {response.status_code}"
					with open("installmods_new.exe", "wb") as file:
						file.write(response.content)

					with open("update.bat", "w") as file:
						file.write(UpdaterBatch)

					os.system(f"start update.bat {os.getpid()}")
				except Exception as e:
					print("Failed to update:")
					print(e)
					if not BooleanPrompt("Retry?"): break
		
		break
	except Exception as e:
		print("Failed to check for updates: ")
		print(e)
		print()
		if not BooleanPrompt("Retry?"): break

# Clean any possible leftover files

if os.path.exists(f"./TEMPDOWNLOAD.zip"): os.remove(f"./TEMPDOWNLOAD.zip")
if os.path.exists(f"./TEMPEXTRACT"): shutil.rmtree("./TEMPEXTRACT")
if os.path.exists(f"./installmods_new.exe"): os.remove(f"./installmods_new.exe")
if os.path.exists(f"./update.bat"): os.remove(f"./update.bat")

# Start

if __name__ == "__main__":
	mods.UpdateList()
	menu.Start()