import toml
from collections import defaultdict

config = {
	"generic_file": "generic_file",
	"generic_folder_closed": "generic_folder_closed",
	"generic_folder_opened": "generic_folder",
	"namespace_folder_closed": "namespace_folder_closed",
	"namespace_folder_opened": "namespace_folder",
	"foldernames": {
		"closed": {},
		"opened": {}
	},
	"filenames": defaultdict(lambda: defaultdict(dict)),
	"extensions": defaultdict(lambda: defaultdict(dict))
}
config["extensions"]["tmcf"]["icon"] = "mcfunction_tick_file"
config["extensions"]["lmcf"]["icon"] = "mcfunction_load_file"
config["extensions"]["mcf"]["icon"] = "mcfunction_file"

icon_packs = [
	"./defs/bedrockAddonIcons.toml",
	"./defs/bedrockResourceIcons.toml",
	"./defs/dataPackIcons.toml",
	"./defs/generalIcons.toml",
	"./defs/languageIcons.toml",
	"./defs/resourcePackIcons.toml"
]
icons = {}
def load_icons():
	for icon_pack_path in icon_packs:
		with open(icon_pack_path, "r")as f:
			icons.update(toml.load(f))


load_icons()
for icon, data in icons.items():
	if "." in icon: 
		icon = icon.replace(".", "_")

	if "foldernames" in data:
		foldertype = "closed" if "closed" in icon else "opened"
		for foldername in data["foldernames"]:
			config["foldernames"][foldertype][foldername] = icon
	if "filenames" in data:
		for filename in data["filenames"]:
			if "/" in filename:
				folder = filename.split("/")[0]
				filename = filename.split("/")[1]
				config["filenames"][filename]["folder"][folder] = icon
			else:
				config["filenames"][filename]["icon"] = icon
	if "extensions" in data:
		for extension in data["extensions"]:
			if "/" in extension:
				folder = extension.split("/")[0]
				extension = extension.split("/")[1]
				config["extensions"][extension]["folder"][folder] = icon
			else:
				config["extensions"][extension]["icon"] = icon

config["filenames"] = dict(config["filenames"])
config["extensions"] = dict(config["extensions"])
for fn in config["filenames"]:
	config["filenames"][fn] = dict(config["filenames"][fn])
for fn in config["extensions"]:
	config["extensions"][fn] = dict(config["extensions"][fn])

from pyperclip import copy
print(str(config))
copy(str(config))
