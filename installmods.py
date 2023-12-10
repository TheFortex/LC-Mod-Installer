import requests
import zipfile
import os, sys, time
import shutil
import random

__version = 4

global CurrentMenu

game_path = "./"
CurrentMenu = None

bad_input = [
	"You stupid or something?",
	"You are actually retarded if you can't navigate this.",
	"Do you have a brain?",
	"Are you a monkey?",
]

def Clear():
	os.system("cls")
	print("#"*62)
	print("#"*10 + " TheFortex's Lethal Company Mod Installer " + "#"*10)
	print("#"*62)
	print(f"Version {__version}")
	print("Installing to: " + game_path)
	print()

def Menu(menuTitle, options):
	global CurrentMenu
	CurrentMenu = (menuTitle, options)
	while True:
		Clear()
		print(f"-- {menuTitle} --\n")
		for key, (title, callback) in options.items():
			print(f"{key} - {title}")
		
		response = input("\n")
		if response in options.keys():
			return options[response][1]()
		else:
			menuTitle = random.choice(bad_input)

# Merge two dictionaries by moving all files from source to destination and overwriting any duplicates recursively
def MergeDicts(source, destination):
	# Check if source is a directory or a file
	if os.path.isfile(source):
		# If source is a file just copy it to destination
		shutil.copy(source, destination)
	else:
		# If source is a directory, copy all files from source to destination
		for src_dir, dirs, files in os.walk(source):
			# Create corresponding destination directory
			dst_dir = src_dir.replace(source, destination, 1)
			if not os.path.exists(dst_dir):
				os.makedirs(dst_dir)

			# For each file in source directory, copy it to destination directory
			for file_ in files:
				src_file = os.path.join(src_dir, file_)
				dst_file = os.path.join(dst_dir, file_)
				if os.path.exists(dst_file):
					os.remove(dst_file)
				shutil.copy(src_file, dst_dir)

def InstallMod(modName, extract_from, extract_to, modURL):
	Clear()
	for i in range(5):
		try:
			print(f"\nDownloading and installing: {modName}")
			response = requests.get(modURL)
			zip_file_path = f"./TEMPDOWNLOAD.zip"

			print(f"Downloading from '{modURL}'")
			with open(zip_file_path, "wb") as zip_file:
				zip_file.write(response.content)

			if extract_from == ".": extract_from = ""
			if extract_to == ".": extract_to = ""

			with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
				print("Installing...")
				zip_ref.extractall(path="./TEMPEXTRACT")
				MergeDicts("./TEMPEXTRACT" + extract_from, game_path + extract_to)
			
			print("Deleting temporary files...")
			os.remove(zip_file_path)
			shutil.rmtree("./TEMPEXTRACT")
			
			break
		except Exception as e:
			print("Error loading file: ")
			print(e)
			continue
	else:
		print("Failed to download after 5 attempts")
		if os.path.exists(f"./TEMPDOWNLOAD.zip"): os.remove(f"./TEMPDOWNLOAD.zip")
		if os.path.exists(f"./TEMPEXTRACT"): shutil.rmtree("./TEMPEXTRACT")
		os.system("pause")

def ModInstaller(modName, extract_from, extract_to, modURL):
	return lambda: InstallMod(modName, extract_from, extract_to, modURL)

def UninstallMod(modName, modPath):
	Clear()
	print("Uninstalling mod: " + modName)

	if os.path.exists(modPath):
		if os.path.isdir(modPath):
			shutil.rmtree(modPath)
		else:
			os.remove(modPath)
	
	UninstallModsMenu()

def ModUninstaller(modName, modPath):
	return lambda: UninstallMod(modName, modPath)

def UninstallAllMods():
	Clear()
	print("Uninstalling all mods...")
	if os.path.exists(f"{game_path}/BepInEx"): os.system(f"rmdir /s /q \"{game_path}/BepInEx\"")
	if os.path.exists(f"{game_path}/changelog.txt"): os.remove(f"{game_path}/changelog.txt")
	if os.path.exists(f"{game_path}/doorstop_config.ini"): os.remove(f"{game_path}/doorstop_config.ini")
	if os.path.exists(f"{game_path}/winhttp.dll"): os.remove(f"{game_path}/winhttp.dll")
	if os.path.exists(f"{game_path}/winhttp_x64.dll"): os.remove(f"{game_path}/winhttp_x64.dll")
	if os.path.exists(f"{game_path}/winhttp_x86.dll"): os.remove(f"{game_path}/winhttp_x86.dll")
	if os.path.exists(f"{game_path}/winhttp_x64.dll.config"): os.remove(f"{game_path}/winhttp_x64.dll.config")
	if os.path.exists(f"{game_path}/winhttp_x86.dll.config"): os.remove(f"{game_path}/winhttp_x86.dll.config")
	MainMenu()

#################################### MENU FUNCTIONS ####################################

def SetGamePath():

	os.system("cls")

	global game_path
	if os.path.exists("./Lethal Company.exe"):
		game_path = "./"
	else:
		print("Note: To get the game directory, right click on the game in Steam, go to Manage > Browse local files")
		print("then copy the path from the file explorer and paste it here.")
		print("Example: C:/Program Files (x86)/Steam/steamapps/common/Lethal Company")
		print()
		print("Note: If you place this script in the game directory, you can skip this step")
		print()
		game_path = input("Paste the path to the game: ")
		if not game_path: game_path = "./"

def InstallModsMenu():

	Clear()

	if os.path.exists(f"{game_path}/BepInEx"):
		print("Warning: There are already mods installed. It is recommended to uninstall them first.")
		print("Do you want to continue? (y/n): ")
		while True:
			response = input()
			if response.lower() == "y" or response.lower() == "ye" or response.lower() == "yes":
				break
			elif response.lower() == "n" or response.lower() == "no":
				return MainMenu()
			else:
				print(random.choice(bad_input))

	Clear()

	print("Fetching mod list...")

	url = "https://pastebin.com/raw/uVHGMQNX"
	response = requests.get(url)
	menu = {
		"..": ("Back", MainMenu),
		"all": ("Install all mods", lambda: [(download_callback()) for key, (mod_name, download_callback) in menu.items() if key != ".." and key != "all"])
	}

	i = 1
	for line in response.iter_lines():
		if line:
			modName, extract_from, extract_to, modURL = line.decode("utf-8").split(" - ")
			callback = ModInstaller(modName, extract_from, extract_to, modURL)
			menu[str(i)] = (modName, callback)
			i += 1

	Menu("Install Mods", menu)

def UninstallModsMenu():
	Clear()

	print("Reading installed mods...")
	menu = {
		"..": ("Back", MainMenu),
		"all": ("Uninstall all mods", UninstallAllMods)
	}
	if os.path.exists(f"{game_path}/BepInEx/plugins"):
		i = 1
		for filename in os.listdir(f"{game_path}/BepInEx/plugins"):
			callback = ModUninstaller(filename, f"{game_path}/BepInEx/plugins/{filename}")
			menu[str(i)] = (filename, callback)
			i += 1

	Menu("Uninstall Mods", menu)

def Exit():
	sys.exit()

def MainMenu():
	Menu("Main Menu", {
		"0": ("Set Game Path", SetGamePath),
		"1": ("Install Mods", InstallModsMenu),
		"2": ("Uninstall Mods", UninstallModsMenu),
		"4": ("Exit", Exit),
	})


if os.path.exists(f"./TEMPDOWNLOAD.zip"): os.remove(f"./TEMPDOWNLOAD.zip")
if os.path.exists(f"./TEMPEXTRACT"): shutil.rmtree("./TEMPEXTRACT")
SetGamePath()
MainMenu()
while True:
	Menu(CurrentMenu[0], CurrentMenu[1])