import os
from os import path
import re
import toml


""""""
icon_packs = [
	"./defs/generalIcons.toml",
	"./defs/languageIcons.toml"
]

plugin_path = "./mc-dp-icons-sublime"
""""""

tmpreferences_template = """<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
	<dict>
		<key>scope</key>
		<string>{scopes}</string>
		<key>settings</key>
		<dict>
			<key>icon</key>
			<string>{icon_name}</string>
		</dict>
	</dict>
</plist>
"""
syntax_template = """%YAML 1.2
---
name: {scope}
scope: mc_dp_icons.{scope}
hidden: true
file_extensions:
  - {file_extensions}
contexts:
  main:
    - include: scope:source.binary
"""

extensions_list_re = re.compile(r"file_extensions:\n(?:\s+- [\w\.\-\+]+.*?\n)+")
extension_re = re.compile(r"\n\s+-\s+(?P<ext>[\w\.\-\+]+)")
scope_re = re.compile(r"(?m)^scope:\s+(?P<scope>[\w\.\-\+]+)")

default_syntaxes = {}

def load_exts_n_scopes(path):
	global default_syntaxes
	with open(path, "r") as f:
		contents = f.read()
	scope = scope_re.search(contents)["scope"]
	ext_lists = extensions_list_re.findall(contents)
	for ext_list in ext_lists:
		for ext in extension_re.findall(ext_list):
			default_syntaxes[ext] = scope


# extension: scope
def load_default_syntaxes():
	for _, __, filenames in os.walk("./default_syntaxes"):
		for filename in filenames:
			load_exts_n_scopes("./default_syntaxes/"+filename)			


def create_preference(scopes: list[str], icon_name: str):
	with open(path.join(plugin_path, "preferences", icon_name+".tmPreferences"), "w") as f:
		f.write(tmpreferences_template.format(scopes=",".join(scopes), icon_name=icon_name))

def create_syntax(extensions: list[str], icon_name: str):
	with open(path.join(plugin_path, "syntaxes", icon_name+".sublime-syntax"), "w") as f:
		f.write(syntax_template.format(scope=icon_name, file_extensions="\n  - ".join(extensions)))
	return "mc_dp_icons."+icon_name

def find_scopes(extensions):
	found_scopes = set()
	orphan_extensions = []
	for ext in extensions:
		try:
			found_scopes.add(default_syntaxes[ext])
		except:
			orphan_extensions.append(ext)
	return list(found_scopes), orphan_extensions


def register_icon(name: str, data: dict):
	extensions = []
	if "filenames" in data:
		extensions += data["filenames"]
	if "extensions" in data:
		extensions += data["extensions"]
	scopes, orphan_extensions = find_scopes(extensions)
	if orphan_extensions:
		scope = create_syntax(orphan_extensions, name)
		scopes.append(scope)
	create_preference(scopes, name)

def _create_test_file(name, data):
	if "extensions" in data:
		for ext in data["extensions"]:
			if "/" in ext:
				continue
			open(f"./test/{name}.{ext}", "w").close()
	if "filenames" in data:
		for filename in data["filenames"]:
			open(f"./test/{filename}", "w").close()

def _remove_subfolder_jsons(icon_data: dict[str, list]):
	for i in ("extensions", "filenames"):
		if i in icon_data:
			exts_to_remove = []
			for ext in icon_data[i]:
				if "/" in ext:
					exts_to_remove.append(ext)
			for ext in exts_to_remove:
				icon_data[i].remove(ext)
	return icon_data


if __name__ == "__main__":
	load_default_syntaxes()

	for icon_pack_path in icon_packs:
		with open(icon_pack_path, "r")as f:
			icon_pack = toml.load(f)
		for icon_name, icon_data in icon_pack.items():
			icon_data = _remove_subfolder_jsons(icon_data)
			register_icon(icon_name, icon_data)
			_create_test_file(icon_name, icon_data)

