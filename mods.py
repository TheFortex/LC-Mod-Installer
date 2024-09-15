import requests, zipfile, os, shutil, json, time
from defs import *
from bcolors import pformat
import bcolors

installed_mods = []

# [Functions]:

def MergeDicts(source, destination):
	"""
	Merge the contents of a source directory or file into a destination directory.
	
	Args:
		source (str): The path to the source directory or file.
		destination (str): The path to the destination directory.
	
	Returns:
		list: A list of the merged file paths.
	"""
	rtrn_files = []

	if os.path.isfile(source):
		# If the source is a file, copy it to the destination directory
		shutil.copy(source, destination)
		rtrn_files.append(destination + source.split("/")[-1])
	else:
		# If the source is a directory, recursively merge its contents into the destination directory
		for src_dir, dirs, files in os.walk(source):
			dst_dir = src_dir.replace(source, destination, 1)
			if not os.path.exists(dst_dir):
				os.makedirs(dst_dir)

			for file_ in files:
				# Skip certain files that should not be merged
				if file_ in ["icon.png", "manifest.json", "README.md", "changelog.txt", "CHANGELOG.md"]:
					continue

				rtrn_files.append(os.path.join(dst_dir, file_))

				src_file = os.path.join(src_dir, file_)
				dst_file = os.path.join(dst_dir, file_)
				if os.path.exists(dst_file):
					os.remove(dst_file)
				shutil.copy(src_file, dst_dir)
	return rtrn_files

def UpdateInstalledModsFile():
	"""
	Update the installed_mods.json file with the current installed mods.

	This function serializes the installed_mods dictionary and writes it to the installed_mods.json file.

	Args:
		None

	Returns:
		None
	"""
	serializable = {mod.name: {"version": mod.version, "files": mod.files} for mod in installed_mods}
	with open(GetGamePath() + "/installed_mods.json", "w") as file:
		file.write(json.dumps(serializable))

def RegisterInstalledMod(mod):
	"""
	Append the installed mod to the installed_mods list and update the installed_mods.json file.

	Args:
		mod (Mod): The Mod object representing the installed mod.

	Returns:
		None
	"""
	global installed_mods
	installed_mods.append(mod)
	UpdateInstalledModsFile()

def DeregisterInstalledMod(mod):
	"""
	Remove the installed mod from the installed_mods list and update the installed_mods.json file.

	Args:
		mod (Mod): The Mod object representing the installed mod.

	Returns:
		None
	"""
	global installed_mods
	installed_mods.remove(mod)
	UpdateInstalledModsFile()

def BulkDelete(lst):
	"""
	removes the specified files and directories.

	Args:
		lst (list): A list of file and directory paths to be removed.

	Returns:
		None
	"""
	for path in lst:
		if os.path.exists(path):
			if os.path.isdir(path):
				# If the path is a directory, remove it and all its contents
				shutil.rmtree(path)
			else:
				# If the path is a file, remove it
				os.remove(path)

# [Class]:

mod_objs = {}

class Mod:
	def __init__(self, name, data):
		"""
		Initialize a Mod object with the given parameters.

		Args:
			required (bool): Whether the mod is required or not.
			name (str): The name of the mod.
			version (str): The version of the mod.
			url (str): The URL to download the mod from.
			extract_from (str): The path to extract the mod files from.
			extract_to (str): The path to extract the mod files to.
			dependencies (list): A list of mod names that this mod depends on.

		Returns:
			None
		"""
		self.name = name
		self.required = data["required"]
		self.version = data["version"]
		self.extract_from = data["extract_from"]
		self.extract_to = data["extract_to"]
		self.url = data["url"]
		self.installed = False
		self.dependencies = [mod_objs.get(dependency, dependency) for dependency in data["dependencies"]]

		for mod in mod_objs.values():
			if self.name in mod.dependencies:
				mod.dependencies.pop(mod.dependencies.index(self.name))
				mod.dependencies.append(self)

		mod_objs[name] = self

	def __str__(self):
		"""
		Return a string representation of the Mod object.

		The string representation includes whether the mod is installed or required, as well as the name and version of the mod.

		Args:
			None

		Returns:
			str: The string representation of the Mod object.
		"""
		return (self.installed and pformat("[INSTALLED] ", bcolors.BGREEN) or "") + (self.required and pformat("[REQUIRED]", bcolors.BRED, bcolors.UNDERLINE) + " " or "") + self.name + pformat(f" v{self.version}", bcolors.BLACK)

	def Install(self):
		# Check if the mod is already installed
		if self.installed:
			print(f"Mod '{self}' is already installed")
			os.system("pause")
			return

		# Install dependencies recursively
		for dependency in self.dependencies:
			if not dependency.installed:
				dependency.Install()

		# Attempt to download and install the mod
		for i in range(5):
			try:
				print(f"\nDownloading and installing: {self}")
				print(f"Downloading from '{self.url}'")
				response = requests.get(self.url)
				assert response.status_code == 200, f"Response code: {response.status_code}"
				zip_file_path = f"./TEMPDOWNLOAD.zip"

				# Save the downloaded file
				with open(zip_file_path, "wb") as zip_file:
					zip_file.write(response.content)

				# Extract the mod files
				with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
					print("Installing...")
					zip_ref.extractall(path="./TEMPEXTRACT")
					self.files = MergeDicts("./TEMPEXTRACT" + self.extract_from, GetGamePath() + self.extract_to)

				# Delete temporary files
				print("Deleting temporary files...")
				os.remove(zip_file_path)
				shutil.rmtree("./TEMPEXTRACT")

				# Append the installed mod to the installed_mods dictionary and mark it as installed
				RegisterInstalledMod(self)
				self.installed = True

				break
			except AssertionError as e:
				print("Error downloading file: ")
				print(e)
				print("Retrying in 3 seconds...")
				time.sleep(3)
			except Exception as e:
				print("Error loading file: ")
				print(e)
				os.system("pause")
				break
			continue
		else:
			print("Failed to download after 5 attempts")
			# Clean up temporary files if download failed
			if os.path.exists(f"./TEMPDOWNLOAD.zip"):
				os.remove(f"./TEMPDOWNLOAD.zip")
			if os.path.exists(f"./TEMPEXTRACT"):
				shutil.rmtree("./TEMPEXTRACT")
			os.system("pause")

	def Uninstall(self):
		# Check if the mod is even installed
		if not self.installed:
			print(f"Mod '{self}' is not installed")
			os.system("pause")
			return
		
		# Check if any installed mods depend on this mod
		for mod in installed_mods.copy():
			if not mod in installed_mods:
				continue
			if self in mod.dependencies:
				# Prompt the user to confirm uninstallation if there are dependencies
				if BooleanPrompt(f"Mod '{mod.name}' depends on '{self.name}', uninstall anyway?"):
					mod.Uninstall()
				else:
					return

		# Uninstall the mod
		print(f"Uninstalling: {self}")
		BulkDelete(self.files)
		DeregisterInstalledMod(self)
		self.installed = False

# [Export functions]:

def UpdateList():
	global installed_mods, mod_objs
	mod_objs = {}
	installed_mods = []

	while True:
		try:
			# Pull mods.json from GitHub
			request = requests.get("https://raw.githubusercontent.com/TheFortex/LC-Mod-Installer/main/mods.json")
			assert request.status_code == 200, f"Response code: {request.status_code}"
			modsdata = request.json()
			break
		except Exception as e:
			print("Failed to load mods:")
			print(e)
			print("Retrying in 3 seconds...")
			print()
			time.sleep(3)

	# Create Mod objects from modsdata and add them to mod_objs if they don't already exist
	[Mod(name, data) for name, data in modsdata.items()]

	try:
		# Check if installed_mods.json exists, if not create it
		if not os.path.exists("./installed_mods.json"):
			with open(GetGamePath() + "/installed_mods.json", "w") as file:
				file.write("{}")

		# Load installed mods from installed_mods.json
		with open(GetGamePath() + "/installed_mods.json", "r") as file:
			# Loop through all installed mods
			for name, data in json.loads(file.read()).items():
				version = data["version"]
				files = data["files"]
				obj = mod_objs.get(name)
				if obj:
					# If the mod is available, mark it as installed
					obj.files = files
					obj.installed = True
					installed_mods.append(obj)
					print(f"Loaded installed mod: {name} v{obj.version} (installed v{version})")

					# If the mod has a different version, prompt the user to update it
					if obj.version != version:
						if BooleanPrompt(f"Mod '{name}' is outdated (Current Version: {obj.version}, Installed Version: {version}). Update?"):
							obj.Uninstall()
							obj.Install()
				else:
					# If the mod is not available, uninstall it
					BulkDelete(files)
		
		# Update installed_mods.json file
		UpdateInstalledModsFile()
	except Exception as e:
		print("Failed to load installed mods:")
		print(e)
		
		if BooleanPrompt("Uninstall all mods? (Recommended)"):
			UninstallAllMods()
		pass

def UninstallAllMods():
	"""
	Uninstall all mods.

	This function removes all mod-related files and directories from the game directory.

	Args:
		None

	Returns:
		None
	"""
	global installed_mods

	Clear()
	print("Uninstalling all mods...")

	# Remove BepInEx directory if it exists
	if os.path.exists(f"{GetGamePath()}/BepInEx"):
		os.system(f"rmdir /s /q \"{GetGamePath()}/BepInEx\"")

	# Remove specific files if they exist
	if os.path.exists(f"{GetGamePath()}/changelog.txt"):
		os.remove(f"{GetGamePath()}/changelog.txt")
	if os.path.exists(f"{GetGamePath()}/icon.png"):
		os.remove(f"{GetGamePath()}/icon.png")
	if os.path.exists(f"{GetGamePath()}/manifest.json"):
		os.remove(f"{GetGamePath()}/manifest.json")
	if os.path.exists(f"{GetGamePath()}/README.md"):
		os.remove(f"{GetGamePath()}/README.md")
	if os.path.exists(f"{GetGamePath()}/doorstop_config.ini"):
		os.remove(f"{GetGamePath()}/doorstop_config.ini")
	if os.path.exists(f"{GetGamePath()}/winhttp.dll"):
		os.remove(f"{GetGamePath()}/winhttp.dll")
	if os.path.exists(f"{GetGamePath()}/winhttp_x64.dll"):
		os.remove(f"{GetGamePath()}/winhttp_x64.dll")
	if os.path.exists(f"{GetGamePath()}/winhttp_x86.dll"):
		os.remove(f"{GetGamePath()}/winhttp_x86.dll")
	if os.path.exists(f"{GetGamePath()}/winhttp_x64.dll.config"):
		os.remove(f"{GetGamePath()}/winhttp_x64.dll.config")
	if os.path.exists(f"{GetGamePath()}/winhttp_x86.dll.config"):
		os.remove(f"{GetGamePath()}/winhttp_x86.dll.config")

	# Clear installed_mods dictionary
	installed_mods = []

	# Update installed_mods.json file
	UpdateInstalledModsFile()

def GetModsList():
	"""
	Get the list of mods.

	This function returns a list of all the Mod objects representing the available mods.

	Args:
		None

	Returns:
		list: The list of Mod objects representing the available mods.
	"""
	return mod_objs.values()

def GetInstalledMods():
	"""
	Get the list of installed mods.

	This function returns the installed_mods list, which contains the installed mods as the corresponding Mod object.

	Args:
		None

	Returns:
		dict: The list of installed mods.
	"""
	return installed_mods