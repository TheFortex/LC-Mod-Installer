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
		print(f"-- {menuTitle} --\n")  # Print the menu title
		for key, (title, callback) in options.items():
			print(f"{key} - {title}")  # Print the menu options
		
		response = input("\n")  # Get user input
		if response in options.keys():  # Check if the input is a valid option
			title, callback = options[response]
			return callback()  # Execute the callback function associated with the selected option
		else:
			menuTitle = random.choice(bad_input)  # If the input is invalid, select a random bad input message

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
		# Prompt the user to select the game executable file
		game_path = filedialog.askopenfilename(title="Select game executable", filetypes=(("Lethal Company", "*.exe"), ("All files", "*.*"))).split("Lethal Company.exe")[0]
		if os.path.exists(os.path.join(game_path, "Lethal Company.exe")):
			break
		else:
			print("The selected directory does not contain the game.")
			os.system("pause")
	
	# Set the game path
	game_path = SetGamePath(game_path)

def InstallModsMenu(Fetch=True):
	# Clear the console screen
	Clear()

	# Check if there are already mods installed
	# if os.path.exists(f"{game_path}/BepInEx"):
	#     print("Warning: There are already mods installed. It is recommended to uninstall them first.")
	#     if not BooleanPrompt("Do you want to continue?"): return MainMenu()

	# Clear the console screen
	Clear()

	# Fetch the mod list if Fetch is True
	if Fetch:
		print("Fetching mod list...")
		mods.UpdateList()

	# Create the menu dictionary
	menu = {
		"..": ("Back", MainMenu),
		"all": ("Install all mods", lambda: [callback() for mod, callback in menu.values() if str(mod) != mod]),
		"required": ("Install required mods", lambda: [callback() for mod, callback in menu.values() if str(mod) != mod and mod.required])
	}
	
	# Add each mod to the menu dictionary
	for i, mod in enumerate(mods.GetModsList()):
		menu[str(i+1)] = (mod, (mod.Install))

	# Call the Menu function with the appropriate arguments
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

	# Call the Menu function with the appropriate arguments
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
		# Try to get the game path from the Windows registry
		# Steam Path Registry key: Computer\HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Valve\Steam -> InstallPath
		game_path = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\WOW6432Node\Valve\Steam"), "InstallPath")[0]
		# Construct the full game path
		game_path = os.path.join(game_path, "steamapps", "common", "Lethal Company")
		# Check if the game executable exists in the game path
		assert os.path.exists(os.path.join(game_path, "Lethal Company.exe")), "Game not found"
		# Set the game path
		game_path = SetGamePath(game_path)
	except:
		# If there is an exception, prompt the user to manually set the game path
		SetGamePathMenu()
	
	# Call the MainMenu function to start the menu loop
	MainMenu()
	while True:
		try:
			# Execute the current menu function (either CurrentMenu or MainMenu)
			(CurrentMenu or MainMenu)()
		except KeyboardInterrupt:
			# If the user presses Ctrl+C, exit the program
			print("Exiting...")
			sys.exit()
		except Exception as e:
			# If there is an exception, print the error message and pause the program
			print("An error occurred:")
			print(e)
			os.system("pause")