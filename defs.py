import os, random
from globals import bad_input, __version

game_path = "./"
def SetGamePath(path="./"):
	global game_path
	game_path = path or "./"
	return game_path

def GetGamePath():
	return game_path

def Clear():
	os.system("cls")
	print("#"*62)
	print("#"*10 + " TheFortex's Lethal Company Mod Installer " + "#"*10)
	print("#"*62)
	print(f"Version {__version}")
	print("Installing to: " + os.path.realpath(game_path))
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