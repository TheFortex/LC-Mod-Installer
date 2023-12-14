import os, requests, sys, menu, shutil
from defs import *
from globals import __version

# Check for updates

while True:
	try:
		print("Checking for updates...")
		response = requests.get("https://api.github.com/repos/TheFortex/LC-Mod-Installer/releases/latest")
		assert response.status_code == 200, f"Response code: {response.status_code}"
		remote_version = int(response.json()["name"].split(" ")[1])

		def Update():
			download_url = response.json()["assets"][0]["browser_download_url"]
			response = requests.get(download_url)
			assert response.status_code == 200, f"Response code: {response.status_code}"
			with open("installmods.exe", "wb") as file:
				file.write(response.content)

			os.system("installmods.exe")
			sys.exit()

		if remote_version > __version:
			print("New version available, updating...")
			os.system("pause")
			while True:
				try:
					Update()
					break
				except:
					if not BooleanPrompt("Failed to update, retry?"): break
		
		break
	except Exception as e:
		print("Failed to check for updates: ")
		print(e)
		print()
		if not BooleanPrompt("Retry?"): break

# Clean any possible leftover files

if os.path.exists(f"./TEMPDOWNLOAD.zip"): os.remove(f"./TEMPDOWNLOAD.zip")
if os.path.exists(f"./TEMPEXTRACT"): shutil.rmtree("./TEMPEXTRACT")

# Start

if __name__ == "__main__": menu.Start()