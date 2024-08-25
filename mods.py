import requests, zipfile, os, shutil, json, time
from defs import *

mods_list = []
installed_mods = {}

# [Functions]:

def MergeDicts(source, destination):
	rtrn_files = []

	if os.path.isfile(source):
		shutil.copy(source, destination)
		rtrn_files.append(destination+source.split("/")[-1])
	else:
		for src_dir, dirs, files in os.walk(source):
			dst_dir = src_dir.replace(source, destination, 1)
			if not os.path.exists(dst_dir):
				os.makedirs(dst_dir)

			for file_ in files:
				if file_ in ["icon.png", "manifest.json", "README.md", "changelog.txt", "CHANGELOG.md"]: continue
	
				rtrn_files.append(os.path.join(dst_dir, file_))

				src_file = os.path.join(src_dir, file_)
				dst_file = os.path.join(dst_dir, file_)
				if os.path.exists(dst_file):
					os.remove(dst_file)
				shutil.copy(src_file, dst_dir)
	return rtrn_files

def UpdateInstalledModsFile():
	serializable = {name: mod.files for name, mod in installed_mods.items()}
	with open(GetGamePath() + "/installed_mods.json", "w") as file:
		file.write(json.dumps(serializable))

def AppendInstalledMods(name, mod):
	global installed_mods
	installed_mods[name] = mod
	UpdateInstalledModsFile()

def PopInstalledMods(name):
	global installed_mods
	installed_mods.pop(name)
	UpdateInstalledModsFile()

def Uninstall(name, files):
	for path in files:
		if os.path.exists(path):
			if os.path.isdir(path):
				shutil.rmtree(path)
			else:
				os.remove(path)

# [Class]:

mod_objs = {}
class Mod:
	def __init__(self, required, name, version, url, extract_from, extract_to, dependencies):
		self.required = required
		self.name = name
		self.version = version
		self.extract_from = extract_from
		self.extract_to = extract_to
		self.url = url
		self.installed = False
		self.dependencies = [mod_objs[dependency] for dependency in dependencies]

		mod_objs[name] = self

	def __str__(self):
		return (self.installed and "[INSTALLED] " or "") + (self.required and "[REQUIRED] " or "") + f"{self.name} {self.version}"

	def Install(self):
		if self.installed:
			print(f"Mod '{self}' is already installed")
			os.system("pause")
			return
		
		for dependency in self.dependencies:
			if not dependency.installed: dependency.Install()
		
		for i in range(5):
			try:
				print(f"\nDownloading and installing: {self}")
				print(f"Downloading from '{self.url}'")
				response = requests.get(self.url)
				assert response.status_code == 200, f"Response code: {response.status_code}"
				zip_file_path = f"./TEMPDOWNLOAD.zip"

				with open(zip_file_path, "wb") as zip_file:
					zip_file.write(response.content)

				with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
					print("Installing...")
					zip_ref.extractall(path="./TEMPEXTRACT")
					self.files = MergeDicts("./TEMPEXTRACT" + self.extract_from, GetGamePath() + self.extract_to)
				
				print("Deleting temporary files...")
				os.remove(zip_file_path)
				shutil.rmtree("./TEMPEXTRACT")

				AppendInstalledMods(f"{self.name} - {self.version}", self)
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
			if os.path.exists(f"./TEMPDOWNLOAD.zip"): os.remove(f"./TEMPDOWNLOAD.zip")
			if os.path.exists(f"./TEMPEXTRACT"): shutil.rmtree("./TEMPEXTRACT")
			os.system("pause")

	def Uninstall(self):
		for mod in installed_mods.copy().values():
			if not mod in installed_mods.values(): continue
			if self in mod.dependencies:
				if BooleanPrompt(f"Mod '{mod.name}' depends on '{self.name}', uninstall anyway?"):
					mod.Uninstall()
				else:
					return

		if not self.installed:
			print(f"Mod '{self}' is not installed")
			os.system("pause")
			return

		print(f"Uninstalling: {self}")
		Uninstall(self.name, self.files)
		PopInstalledMods(f"{self.name} - {self.version}")
		self.installed = False

# [Export functions]:

def UpdateList():
	global mods_list, installed_mods

	while True:
		try:
			# pull from mods.json from github
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

	[Mod(*data) for data in modsdata if not mod_objs.get(data[1])]
	mods_list = mod_objs.values()
	try:
		if not os.path.exists("./installed_mods.json"):
			with open(GetGamePath() + "/installed_mods.json", "w") as file:
				file.write("{}")
		with open(GetGamePath() + "/installed_mods.json", "r") as file:
			for id, files in json.loads(file.read()).items():
				name, version = id.split(" - ")
				if name in mod_objs.keys() and mod_objs[name].version == version:
					installed_mods[name] = mod_objs[name]
					mod_objs[name].files = files
					mod_objs[name].installed = True
				else:
					Uninstall(name, files)
					installed_mods.pop(name)
	except Exception as e:
		print("Failed to load installed mods:")
		print(e)
		os.system("pause")

		installed_mods = {}
		pass

def UninstallAllMods():
	global installed_mods

	Clear()
	print("Uninstalling all mods...")

	if os.path.exists(f"{GetGamePath()}/BepInEx"): os.system(f"rmdir /s /q \"{GetGamePath()}/BepInEx\"")
	if os.path.exists(f"{GetGamePath()}/changelog.txt"): os.remove(f"{GetGamePath()}/changelog.txt")
	if os.path.exists(f"{GetGamePath()}/icon.png"): os.remove(f"{GetGamePath()}/icon.png")
	if os.path.exists(f"{GetGamePath()}/manifest.json"): os.remove(f"{GetGamePath()}/manifest.json")
	if os.path.exists(f"{GetGamePath()}/README.md"): os.remove(f"{GetGamePath()}/README.md")
	if os.path.exists(f"{GetGamePath()}/doorstop_config.ini"): os.remove(f"{GetGamePath()}/doorstop_config.ini")
	if os.path.exists(f"{GetGamePath()}/winhttp.dll"): os.remove(f"{GetGamePath()}/winhttp.dll")
	if os.path.exists(f"{GetGamePath()}/winhttp_x64.dll"): os.remove(f"{GetGamePath()}/winhttp_x64.dll")
	if os.path.exists(f"{GetGamePath()}/winhttp_x86.dll"): os.remove(f"{GetGamePath()}/winhttp_x86.dll")
	if os.path.exists(f"{GetGamePath()}/winhttp_x64.dll.config"): os.remove(f"{GetGamePath()}/winhttp_x64.dll.config")
	if os.path.exists(f"{GetGamePath()}/winhttp_x86.dll.config"): os.remove(f"{GetGamePath()}/winhttp_x86.dll.config")

	global installed_mods
	installed_mods = {}
	UpdateInstalledModsFile()

def GetModsList():
	return mods_list

def GetInstalledMods():
	return installed_mods