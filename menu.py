from defs import *
from globals import bad_input
import random, sys, os
import mods

game_path = SetGamePath()
CurrentMenu = None

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

def SetGamePathMenu():
	os.system("cls")

	global game_path
	if not os.path.exists("./Lethal Company.exe"):
		print("Note: To get the game directory, right click on the game in Steam, go to Manage > Browse local files")
		print("then copy the path from the file explorer and paste it here.")
		print("Example: C:/Program Files (x86)/Steam/steamapps/common/Lethal Company")
		print()
		print("Note: If you place this script in the game directory, you can skip this step")
		print()
		game_path = SetGamePath(input("Paste the path to the game: "))

def InstallModsMenu():

	Clear()

	if os.path.exists(f"{game_path}/BepInEx"):
		print("Warning: There are already mods installed. It is recommended to uninstall them first.")
		if not BooleanPrompt("Do you want to continue?"): return MainMenu()

	Clear()

	print("Fetching mod list...")
	mods.UpdateList()

	menu = {
		"..": ("Back", MainMenu),
		"all": ("Install all mods", lambda: [callback() for mod, callback in menu if str(mod) != mod]),
		"required": ("Install required mods", lambda: [callback() for mod, callback in menu if str(mod) != mod and mod.required])
	}

	for i, mod in mods.GetModsList(): menu[str(i)] = (mod, mod.Install)

	Menu("Install Mods", menu)

def UninstallModsMenu():
	Clear()

	print("Reading installed mods...")
	menu = {
		"..": ("Back", MainMenu),
		"all": ("Uninstall all mods", lambda: [mods.UninstallAllMods, MainMenu()])
	}
	for name, files in mods.GetInstalledMods().items(): menu[name] = (name, mods.Uninstaller(name, files))

	Menu("Uninstall Mods", menu)

def Exit():
	sys.exit()

def MainMenu():
	Menu("Main Menu", {
		"0": ("Set Game Path", SetGamePathMenu),
		"1": ("Install Mods", InstallModsMenu),
		"2": ("Uninstall Mods", UninstallModsMenu),
		"4": ("Exit", Exit),
	})

def Start():
	SetGamePathMenu()
	while True:
		# try:
			MainMenu()
		# except KeyboardInterrupt:
		# 	print("Exiting...")
		# 	sys.exit()
		# except Exception as e:
		# 	print("An error occured: ")
		# 	print(e)
		# 	os.system("pause")