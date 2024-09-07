import os, random
from globals import bad_input, __version
from bcolors import pprint, mpprint, pinput
import bcolors

game_path = "./"
def SetGamePath(path="./"):
	global game_path
	game_path = path or "./"
	return game_path

def GetGamePath():
	return game_path

def Clear():
	os.system("cls")
	pprint(" _         _   _           _    ____                                        ", bcolors.RED)
	pprint("| |    ___| |_| |__   __ _| |  / ___|___  _ __ ___  _ __   __ _ _ __  _   _ ", bcolors.RED)
	pprint("| |   / _ \ __| '_ \ / _` | | | |   / _ \| '_ ` _ \| '_ \ / _` | '_ \| | | |", bcolors.RED)
	pprint("| |__|  __/ |_| | | | (_| | | | |__| (_) | | | | | | |_) | (_| | | | | |_| |", bcolors.RED)
	pprint("|_____\___|\__|_| |_|\__,_|_|  \____\___/|_| |_| |_| .__/ \__,_|_| |_|\__, |", bcolors.RED)
	pprint("          __  __           _   ___           _     |_|_ _             |___/ ", bcolors.RED)
	pprint("         |  \/  | ___   __| | |_ _|_ __  ___| |_ __ _| | | ___ _ __         ", bcolors.BRED)
	pprint("         | |\/| |/ _ \ / _` |  | || '_ \/ __| __/ _` | | |/ _ \ '__|        ", bcolors.BRED)
	pprint("         | |  | | (_) | (_| |  | || | | \__ \ || (_| | | |  __/ |           ", bcolors.BRED)
	pprint("         |_|  |_|\___/ \__,_| |___|_| |_|___/\__\__,_|_|_|\___|_|  			", bcolors.BRED)
	print()
	pprint(" |            __ __| |           __|         |               ", bcolors.GREY, bcolors.BLINK)
	pprint("  _ \  |  |      |     \    -_)  _|  _ \   _| _|   -_) \ \ / ", bcolors.GREY, bcolors.BLINK)
	pprint("_.__/ \_, |     _|  _| _| \___| _| \___/ _| \__| \___|  _\_\ ", bcolors.GREY, bcolors.BLINK)
	pprint("      ___/                                                   ", bcolors.GREY, bcolors.BLINK)
	print()
	pprint(f" Version {__version} ", bcolors.INVERT)
	mpprint(["Installing to: ", bcolors.BOLD], [os.path.realpath(game_path), bcolors.BLUE])
	print()

def BooleanPrompt(prompt):
	while True:
		response = input(prompt+" (y/n): ")
		if response.lower() in ["y", "ye", "yes"]:
			return True
		elif response.lower() in ["n", "no"]:
			return False
		else:
			print(random.choice(bad_input))

def Wrap(*funcs):
	def wrapper():
		for func, *args in funcs:
			func(*args)
	return wrapper

def Note(string):
	mpprint(["Note: ", bcolors.BCYAN, bcolors.UNDERLINE], [string, bcolors.UNDERLINE])

def Warning(string):
	mpprint(["WARNING: ", bcolors.BYELLOW], string)

def Error(string):
	mpprint(["ERROR: ", bcolors.BRED], string)

def Success(string):
	mpprint(["Success: ", bcolors.BGREEN], string)

def Info(string):
	mpprint(["Info: ", bcolors.BWHITE, bcolors.UNDERLINE], [string, bcolors.UNDERLINE])