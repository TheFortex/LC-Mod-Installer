from defs import *
from globals import bad_input
import random, sys, os
import mods

game_path = SetGamePath()
CurrentMenu = None

def Menu(self, menuTitle, options):
	global CurrentMenu
	CurrentMenu = self
	while True:
		Clear()
		print(f"-- {menuTitle} --\n")
		for key, (title, callback) in options.items():
			print(f"{key} - {title}")
		
		response = input("\n")
		if response in options.keys():
			title, callback = options[response]
			return callback()
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

def InstallModsMenu(Fetch=True):

	# Clear()

	# if os.path.exists(f"{game_path}/BepInEx"):
	# 	print("Warning: There are already mods installed. It is recommended to uninstall them first.")
	# 	if not BooleanPrompt("Do you want to continue?"): return MainMenu()

	Clear()

	if Fetch:
		print("Fetching mod list...")
		mods.UpdateList()

	menu = {
		"..": ("Back", MainMenu),
		"all": ("Install all mods", lambda: [callback() for mod, callback in menu.values() if str(mod) != mod]),
		"required": ("Install required mods", lambda: [callback() for mod, callback in menu.values() if str(mod) != mod and mod.required])
	}
	
	for i, mod in enumerate(mods.GetModsList()):
		menu[str(i+1)] = (mod, (mod.Install))

	Menu(Wrap((InstallModsMenu, False)), "Install Mods", menu)

def UninstallModsMenu():
	Clear()

	print("Reading installed mods...")
	menu = {
		"..": ("Back", MainMenu),
		"all": ("Uninstall all mods", Wrap((mods.UninstallAllMods,), (MainMenu,)))
	}

	i = 1
	for name, mod in mods.GetInstalledMods().items():
		menu[str(i)] = (f"{mod.name} {mod.version}", mod.Uninstall)
		i += 1

	Menu(UninstallModsMenu, "Uninstall Mods", menu)

def Exit():
	sys.exit()

def MainMenu():
	Menu(MainMenu, "Main Menu", {
		"0": ("Set Game Path", SetGamePathMenu),
		"1": ("Install Mods", InstallModsMenu),
		"2": ("Uninstall Mods", UninstallModsMenu),
		"4": ("Exit", Exit),
	})

def Start():
	SetGamePathMenu()
	MainMenu()
	while True:
		try:
			(CurrentMenu or MainMenu)()
		except KeyboardInterrupt:
			print("Exiting...")
			sys.exit()
		except Exception as e:
			print("An error occured:")
			print(e)
			os.system("pause")