import os
from os import path
import re
import toml
from shutil import rmtree
from collections import defaultdict


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
scope: {scope}
hidden: true
file_extensions:
  - {file_extensions}
contexts:
  main:
    - include: scope:{parent_scope}
"""

extensions_list_re = re.compile(r"file_extensions:\n(?:\s+- [\w\.\-\+]+.*?\n)+")
extension_re = re.compile(r"\n\s+-\s+(?P<ext>[\w\.\-\+]+)")
scope_re = re.compile(r"(?m)^scope:\s+(?P<scope>[\w\.\-\+]+)")

default_syntaxes = {}
icons = {}
taken_default_scopes = defaultdict(set)

def _load_exts_n_scopes(path):
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
			_load_exts_n_scopes("./default_syntaxes/"+filename)			

def load_icons():
	for icon_pack_path in icon_packs:
		with open(icon_pack_path, "r")as f:
			icons.update(toml.load(f))

def create_preference(scopes: list[str], icon_name: str):
	with open(path.join(plugin_path, "preferences", icon_name+".tmPreferences"), "w") as f:
		f.write(tmpreferences_template.format(scopes=",".join(scopes), icon_name=icon_name))

def create_syntax(extensions: list[str], scope: str, parent_scope: str="source.binary") -> str:
	with open(path.join(plugin_path, "syntaxes", scope+".sublime-syntax"), "w") as f:
		f.write(
			syntax_template.format(
				scope=scope, 
				file_extensions="\n  - ".join(extensions),
				parent_scope=parent_scope
			)
		)
	return scope

def find_scopes(icon_name: str, extensions: list[str]) -> tuple[dict[str, list], list[str]]:
	global taken_default_scopes
	localized_tds = taken_default_scopes
	matching_scopes = defaultdict(list)
	orphan_extensions = []
	for ext in extensions:
		try:
			matching_scope = default_syntaxes[ext]
			matching_scopes[matching_scope].append(ext)
			localized_tds[matching_scope].add(icon_name)
		except KeyError:
			orphan_extensions.append(ext)
	return matching_scopes, orphan_extensions


def _create_test_file(name, data):
	if "extensions" in data:
		for ext in data["extensions"]:
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

def clean_unsupported_stuff():
	icons_to_delete = []
	for name, data in icons.items():
		if "folder" in name or not data:
			icons_to_delete.append(name)
		else:
			icons[name] = _remove_subfolder_jsons(data)


if __name__ == "__main__":
	load_default_syntaxes()
	load_icons()
	clean_unsupported_stuff()

	rmtree(path.join(plugin_path, "preferences"), ignore_errors=True)
	os.mkdir(path.join(plugin_path, "preferences"))
	rmtree(path.join(plugin_path, "syntaxes"), ignore_errors=True)
	os.mkdir(path.join(plugin_path, "syntaxes"))

	for name, data in icons.items():
		_create_test_file(name, data)

		extensions = []
		if "filenames" in data:
			extensions += data["filenames"]
		if "extensions" in data:
			extensions += data["extensions"]
		scopes, orphan_extensions = find_scopes(name, extensions)
		if orphan_extensions:
			custom_scope = create_syntax(orphan_extensions, f"mc_dp_icons.{name}")
			scopes[custom_scope] = orphan_extensions
		icons[name]["_scopes"] = scopes
	
	# handling collisions
	for scope, concurring_icons in taken_default_scopes.items():
		if len(concurring_icons) < 2:
			continue
		for icon in concurring_icons:
			forked_scope = create_syntax(
				extensions=icons[icon]["_scopes"][scope],
				parent_scope=scope,
				scope=f"{scope}.mc_dp_icons.{icon}"
			)
			del icons[icon]["_scopes"][scope]
			icons[icon]["_scopes"][forked_scope] = []

	for name, data in icons.items():
		create_preference(list(data["_scopes"]), name)
