import random, sys, os, winreg
import tkinter as tk
from tkinter import filedialog
from defs import *
from globals import bad_input
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
	global game_path

	os.system("cls")
	print("Please browse to the game directory.")
	print("Note: If you place this script in the game directory, you can skip this step")
	print()

	os.system("pause")
	root = tk.Tk()
	root.withdraw()

	while True:
		game_path = filedialog.askopenfilename(title = "Select game executable", filetypes = (("Lethal Company", "*.exe"), ("All files", "*.*"))).split("Lethal Company.exe")[0]
		if os.path.exists(os.path.join(game_path, "Lethal Company.exe")):
			break
		else:
			print("The selected directory does not contain the game.")
			os.system("pause")
	game_path = SetGamePath(game_path)

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
	try:
		# Computer\HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Valve\Steam
		game_path = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\WOW6432Node\Valve\Steam"), "InstallPath")[0]
		game_path = os.path.join(game_path, "steamapps", "common", "Lethal Company")
		assert os.path.exists(os.path.join(game_path, "Lethal Company.exe")), "Game not found"
		game_path = SetGamePath(game_path)
	except:
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