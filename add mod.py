import json, os, sys, requests, zipfile, winreg, shutil
from defs import BooleanPrompt
from mods import MergeDicts

mods = {}

def read_mods():
	global mods
	with open('mods.json', 'r') as f:
		mods = json.load(f)

def write_mods():
	with open('mods.json', 'w') as f:
		json.dump(mods, f, indent=4)

def add_mod(name, mod):
	if name in mods and mods[name]["version"] == mod["version"]:
		print(f"Mod {name} v{mod['version']} already exists")
		return
	
	mods[name] = mod
	write_mods()

def download_mod(url):
	response = requests.get(url)
	assert response.status_code == 200, f"Response code: {response.status_code}"
	zip_file_path = f"./TEMPDOWNLOAD.zip"

	# Save the downloaded file
	with open(zip_file_path, "wb") as zip_file:
		zip_file.write(response.content)

	# Extract the mod files
	with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
		zip_ref.extractall(path="./TEMPEXTRACT")
	
	return "./TEMPEXTRACT"

def deduce_extract_from_and_to(mod_path):
	# If the mod has a folder called "BepInEx", set the extract_from to "/BepInEx" and extract_to to "/BepInEx"
	# If the mod has a folder called "plugins", set the extract_from to "/plugins" and extract_to to "/BepInEx/plugins"
	# If neither of the above, set the extract_from to "/" and extract_to to "/BepInEx/plugins"

	if os.path.isdir(f"{mod_path}/BepInEx"):
		extract_from = "/BepInEx"
		extract_to = "/BepInEx"
	elif os.path.isdir(f"{mod_path}/plugins"):
		extract_from = "/plugins"
		extract_to = "/BepInEx/plugins"
	else:
		extract_from = "/"
		extract_to = "/BepInEx/plugins"
	
	# Print the deduced values and the mod_path file and folder structure to confirm the deduced values are correct

	print(f"Mod path: {mod_path}")
	print(f"File and folder structure:")
	for root, dirs, files in os.walk(mod_path):
		level = root.replace(mod_path, '').count(os.sep)
		indent = ' ' * 4 * (level)
		print(f"{indent}{os.path.basename(root)}/")
		subindent = ' ' * 4 * (level + 1)
		for f in files:
			print(f"{subindent}{f}")
	print()
	print(f"Extract from: {extract_from}")
	print(f"Extract to: {extract_to}")

	if not BooleanPrompt("Is this correct?"):
		extract_from = input("Enter the extract from path: ")
		extract_to = input("Enter the extract to path: ")
	
	return extract_from, extract_to

def deduce_name_and_version(mod_path):
	# Get the name and version from the mod's manifest file
	manifest_path = f"{mod_path}/manifest.json"
	if manifest_path:
		with open(manifest_path, 'r') as f:
			manifest = json.load(f)
			name = manifest["name"]
			version = manifest["version_number"]
	else:
		name = input("Enter the mod name: ")
		version = input("Enter the mod version: ")
	
	return name, version

def find_dependency(dependencyFullName):
	for name in mods.keys():
		if name in dependencyFullName:
			return name
	return None

def deduce_dependencies(mod_path):
	dependencies = []

	# Get the dependencies from the mod's manifest file
	manifest_path = f"{mod_path}/manifest.json"
	if manifest_path:
		with open(manifest_path, 'r') as f:
			manifest = json.load(f)
			dependencyread = manifest.get("dependencies", [])
		
		for dependency in dependencyread:
			dependencyName = find_dependency(dependency)
			if dependencyName:
				if not BooleanPrompt(f"Infer dependency {dependency} as {dependencyName}?"):
					dependencyName = input(f"Enter the mod name for dependency {dependency}: ")
			else:
				dependencyName = input(f"Enter the mod name for dependency {dependency}: ")
			dependencies.append(dependencyName)
	else:
		dependencies = input("Enter the dependencies separated by a comma: ").split(", ")
	
	return dependencies

def install_mod(name, mod, mod_path):
	# get the game path
	try:
		# Try to get the game path from the Windows registry
		# Steam Path Registry key: Computer\HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Valve\Steam -> InstallPath
		game_path = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam"), "InstallPath")[0]
		# Construct the full game path
		game_path = os.path.join(game_path, "steamapps", "common", "Lethal Company")
		# Check if the game executable exists in the game path
		assert os.path.exists(os.path.join(game_path, "Lethal Company.exe")), "Game not found"
	except:
		# If there is an exception, prompt the user to manually set the game path
		game_path = input("Enter the game path: ")

	# read installed_mods.json from the game path
	with open(f"{game_path}/installed_mods.json", 'r') as f:
		installed_mods = json.load(f)
	
	# check if the mod is already installed
	if name in installed_mods:
		print(f"Mod {name} v{mod['version']} already installed")
		return
	
	# extract the mod files
	files = MergeDicts(f"{mod_path}{mod['extract_from']}", f"{game_path}{mod['extract_to']}")

	# add the mod to the installed mods list
	installed_mods[name] = {"version": mod["version"], "files": files}

	# write the installed mods list to installed_mods.json
	with open(f"{game_path}/installed_mods.json", 'w') as f:
		json.dump(installed_mods, f, indent=4)

def commit_and_push():
	# Check if the user has git installed
	if os.system("git --version") != 0:
		print("Git not found")
		return
	
	# Commit the changes to mods.json
	os.system("git add mods.json")
	os.system("git commit -m \"Add mod\"")

	# Push the changes to the remote repository
	os.system("git push")

def clean_up():
	if os.path.exists(f"./TEMPDOWNLOAD.zip"): os.remove(f"./TEMPDOWNLOAD.zip")
	if os.path.exists(f"./TEMPEXTRACT"): shutil.rmtree("./TEMPEXTRACT")

def main():
	clean_up()
	read_mods()

	url = input("Enter the mod download URL: ")
	print()
	mod_path = download_mod(url)
	print()
	name, version = deduce_name_and_version(mod_path)
	print()
	extract_from, extract_to = deduce_extract_from_and_to(mod_path)
	print()
	dependencies = deduce_dependencies(mod_path)
	print()
	required = BooleanPrompt("Is this mod required?")
	print()
	mod = {
		"required": required,
		"version": version,
		"url": url,
		"extract_from": extract_from,
		"extract_to": extract_to,
		"dependencies": dependencies
	}

	print(f"Mod: {name} v{version}\nRequired: {required}\nExtract from: {extract_from}\nExtract to: {extract_to}\nDependencies: {dependencies}")
	print()
	if not BooleanPrompt("Add the mod?"):
		return
	
	add_mod(name, mod)
	print()
	BooleanPrompt("Commit and push changes to mods.json?") and commit_and_push()
	print()
	BooleanPrompt("Install the mod?") and install_mod(name, mod, mod_path)
	clean_up()

if __name__ == "__main__":
	try:
		main()
		print("Awesome!")
	except Exception as e:
		print("Failed:")
		print(e)
		print()
	
	os.system("pause")
		