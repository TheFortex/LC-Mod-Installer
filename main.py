import os, requests, sys, shutil, menu, mods
from defs import *
from globals import __version

# Check for updates

# This script checks for updates of the LC Mod Installer program and performs the update if a new version is available. It also cleans any possible leftover files and starts the program.
# The script performs the following steps:
# 1. Checks for updates by sending a GET request to the GitHub API to retrieve the latest release information.
# 2. If the response status code is 200, it extracts the remote version number from the response.
# 3. If the remote version is greater than the current version (__version), it prompts the user to update and proceeds with the update process.
# 4. During the update process, it downloads the updated installer file and saves it as "installmods_new.exe".
# 5. It creates a batch script called "update.bat" that will be used to update the program.
# 6. It starts the "update.bat" script with the current process ID as an argument.
# 7. The "update.bat" script kills the current process, replaces the old installer file with the new one, and starts the updated program.
# 8. If the update process fails, it prompts the user to retry or exit.
# 9. After the update process is completed or if no update is available, it cleans any possible leftover files.
# 10. Finally, it calls the "UpdateList()" function from the "mods" module to update the list of available mods and starts the program by calling the "Start()" function from the "menu" module.
# Note: The batch script "update.bat" is responsible for replacing the old installer file with the new one because it needs to kill the current process to release the file lock. This is necessary because the script is running within the same process as the program itself.
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

		# Send GET request to GitHub API to retrieve latest release information
		response = requests.get("https://api.github.com/repos/TheFortex/LC-Mod-Installer/releases/latest")

		# Check if response status code is 200
		assert response.status_code == 200, f"Response code: {response.status_code}"

		# Extract remote version number from response
		remote_version = int(response.json()["name"].split(" ")[1])

		# Check if remote version is greater than current version
		if remote_version > __version:
			print(f"New version available: {remote_version} (Current: {__version}) - The program will now update.")
			os.system("pause")

			while True:
				try:
					# Get download URL for updated installer file
					download_url = response.json()["assets"][0]["browser_download_url"]
					response = requests.get(download_url)

					# Check if response status code is 200
					assert response.status_code == 200, f"Response code: {response.status_code}"

					# Save updated installer file as "installmods_new.exe"
					with open("installmods_new.exe", "wb") as file:
						file.write(response.content)

					# Create batch script "update.bat" for updating the program
					with open("update.bat", "w") as file:
						file.write(UpdaterBatch)

					# Start "update.bat" script with current process ID as argument
					os.system(f"start update.bat {os.getpid()}")
				except Exception as e:
					print("Failed to update:")
					print(e)

					# Prompt user to retry or exit
					if not BooleanPrompt("Retry?"):
						break

		break
	except Exception as e:
		print("Failed to check for updates: ")
		print(e)
		print()

		# Prompt user to retry or exit
		if not BooleanPrompt("Retry?"):
			break

# Clean any possible leftover files

if os.path.exists(f"./TEMPDOWNLOAD.zip"): os.remove(f"./TEMPDOWNLOAD.zip")
if os.path.exists(f"./TEMPEXTRACT"): shutil.rmtree("./TEMPEXTRACT")
if os.path.exists(f"./installmods_new.exe"): os.remove(f"./installmods_new.exe")
if os.path.exists(f"./update.bat"): os.remove(f"./update.bat")

# Start

if __name__ == "__main__":
	mods.UpdateList()
	menu.Start()