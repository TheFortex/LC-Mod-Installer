import requests, zipfile, os, shutil, json, time
from defs import *

mods_list = []
installed_mods = {}

try:
	with open("./installed_mods.json", "r") as file:
		installed_mods = json.loads(file.read())
except:
	installed_mods = {}
	pass

# [Functions]:

def MergeDicts(source, destination):
	files = []

	if os.path.isfile(source):
		shutil.copy(source, destination)
		files.append(destination+source.split("/")[-1])
	else:
		for src_dir, dirs, files in os.walk(source):
			dst_dir = src_dir.replace(source, destination, 1)
			if not os.path.exists(dst_dir):
				os.makedirs(dst_dir)

			for file_ in files:
				if file_ in ["icon.png", "manifest.json", "README.md"]: continue

				files.append(os.path.join(dst_dir, file_))

				src_file = os.path.join(src_dir, file_)
				dst_file = os.path.join(dst_dir, file_)
				if os.path.exists(dst_file):
					os.remove(dst_file)
				shutil.copy(src_file, dst_dir)

def UpdateInstalledModsFile():
	with open("./installed_mods.json", "w") as file:
		file.write(json.dumps(installed_mods))

def AppendInstalledMods(name, files):
	installed_mods[name] = files
	UpdateInstalledModsFile()

def PopInstalledMods(name):
	installed_mods.pop(name)
	UpdateInstalledModsFile()

def Uninstall(name, files):
	PopInstalledMods(name)
	for path in files:
		if os.path.exists(path):
			if os.path.isdir(path):
				shutil.rmtree(path)
			else:
				os.remove(path)

def Uninstaller(name, files):
	return lambda: Uninstall(name, files)

def UninstallRemovedMods():
	mod_names = [mod.name for mod in mods_list]
	[Uninstall(name, files) for name, files in installed_mods.items() if name not in mod_names]

# [Class]:

class Mod:
	def __init__(self, required, name, version, url, extract_from, extract_to, dependencies):
		self.required = required
		self.name = name
		self.version = version
		self.extract_from = extract_from
		self.extract_to = extract_to
		self.url = url
		self.dependencies = dependencies

		self.files = installed_mods.get(self.name, [])
		self.installed = bool(self.files)

	def __str__(self):
		return (self.required and "[REQUIRED] " or "") + f"{self.name} {self.version}"
	
	def Install(self):
		if self.installed:
			print(f"Mod '{self}' is already installed")
			return
		
		for i in range(5):
			try:
				print(f"\nDownloading and installing: {self}")
				print(f"Downloading from '{self.url}'")
				response = requests.get(self.url)
				zip_file_path = f"./TEMPDOWNLOAD.zip"

				with open(zip_file_path, "wb") as zip_file:
					zip_file.write(response.content)

				with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
					print("Installing...")
					zip_ref.extractall(path="./TEMPEXTRACT")
					self.files = MergeDicts("./TEMPEXTRACT" + self.extract_from, game_path + self.extract_to)
				
				print("Deleting temporary files...")
				os.remove(zip_file_path)
				shutil.rmtree("./TEMPEXTRACT")

				AppendInstalledMods(self.name, self.files)
				self.installed = True
				
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
	
	def Uninstall(self):
		if not self.installed:
			print(f"Mod '{self}' is not installed")
			return
		
		Uninstall(self.name, self.files)
		self.installed = False

# [Export functions]:

def UpdateList():
	global mods_list

	while True:
		try:
			# pull from mods.json from github
			request = requests.get("https://raw.githubusercontent.com/TheFortex/LC-Mod-Installer/master/mods.json")
			assert request.status_code == 200, f"Response code: {request.status_code}"
			modsdata = request.json()
			break
		except Exception as e:
			print("Failed to load mods:")
			print(e)
			print("Retrying in 3 seconds...")
			print()
			time.sleep(3)

	mods_list = [Mod(*data) for data in modsdata]
	UninstallRemovedMods()

def UninstallAllMods():
	Clear()
	print("Uninstalling all mods...")

	global installed_mods
	installed_mods = {}
	UpdateInstalledModsFile()

	if os.path.exists(f"{game_path}/BepInEx"): os.system(f"rmdir /s /q \"{game_path}/BepInEx\"")
	if os.path.exists(f"{game_path}/changelog.txt"): os.remove(f"{game_path}/changelog.txt")
	if os.path.exists(f"{game_path}/icon.png"): os.remove(f"{game_path}/icon.png")
	if os.path.exists(f"{game_path}/manifest.json"): os.remove(f"{game_path}/manifest.json")
	if os.path.exists(f"{game_path}/README.md"): os.remove(f"{game_path}/README.md")
	if os.path.exists(f"{game_path}/doorstop_config.ini"): os.remove(f"{game_path}/doorstop_config.ini")
	if os.path.exists(f"{game_path}/winhttp.dll"): os.remove(f"{game_path}/winhttp.dll")
	if os.path.exists(f"{game_path}/winhttp_x64.dll"): os.remove(f"{game_path}/winhttp_x64.dll")
	if os.path.exists(f"{game_path}/winhttp_x86.dll"): os.remove(f"{game_path}/winhttp_x86.dll")
	if os.path.exists(f"{game_path}/winhttp_x64.dll.config"): os.remove(f"{game_path}/winhttp_x64.dll.config")
	if os.path.exists(f"{game_path}/winhttp_x86.dll.config"): os.remove(f"{game_path}/winhttp_x86.dll.config")

def GetModsList():
	return mods_list

def GetInstalledMods():
	return installed_mods