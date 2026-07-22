import os
from os import path
from json import dump
import yaml
import re
import toml
import plistlib
from shutil import rmtree
from collections import defaultdict


""""""
icon_packs = [
    "./defs/generalIcons.toml",
    "./defs/languageIcons.toml",
    "./defs/bedrockAddonIcons.toml",
    "./defs/bedrockResourceIcons.toml",
    "./defs/dataPackIcons.toml",
    "./defs/resourcePackIcons.toml"
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
name: {name}
scope: {scope}
hidden: true
file_extensions:
  - {file_extensions}
contexts:
  main:
   - include: scope:{parent_scope}
"""


extensions_list_re = re.compile(r"(?m)(file_extensions:(?:\n(?:\s+- [\w\.\-\+]+.*?\n)+|\s+?\[.*?$))")
extension_re = re.compile(r"\n\s+-\s+(?P<ext>[\w\.\-\+]+)")
scope_re = re.compile(r"(?m)^scope:\s+(?P<scope>[\w\.\-\+]+)")
name_re = re.compile(r"(?m)^name:\s+(?P<name>.*?$)")

default_syntaxes = {}
icons = {}
scope_names = {}
taken_default_scopes = defaultdict(set)

def _load_exts_n_scopes(path):
    global default_syntaxes
    with open(path, "r") as f:
        contents = f.read()
    scope = scope_re.search(contents)["scope"]
    name = name_re.search(contents)
    if name != None:
        name = name["name"]
    scope_names[scope] = name
    ext_lists = extensions_list_re.findall(contents)
    for ext_list in ext_lists:
        for ext in yaml.load(ext_list, yaml.CLoader)["file_extensions"]:
            default_syntaxes[ext] = scope

def _load_stupid_tmlang_and_violently_assasinate_creator_of_this_format(path):
    with open(path, 'rb') as f:
        data = plistlib.load(f)
    file_types = data.get('fileTypes', [])
    scope = data.get('scopeName', '')
    name = data.get('name', '')
    scope_names[scope] = name
    for ext in file_types:
        default_syntaxes[ext] = scope

# extension: scope
def load_syntaxes(syntaxes_path):
    for _, __, filenames in os.walk(syntaxes_path):
        for filename in filenames:
            if filename.endswith("sublime-syntax"):
                _load_exts_n_scopes(path.join(syntaxes_path, filename))			
            else:
                _load_stupid_tmlang_and_violently_assasinate_creator_of_this_format(path.join(syntaxes_path, filename))

def load_icons():
    for icon_pack_path in icon_packs:
        with open(icon_pack_path, "r")as f:
            icons.update(toml.load(f))

def create_preference(scopes: list[str], icon_name: str):
    with open(path.join(plugin_path, "preferences", icon_name+".tmPreferences"), "w") as f:
        f.write(tmpreferences_template.format(scopes=",".join(scopes), icon_name=icon_name))

def create_syntax(extensions: list[str], scope: str, name: str, parent_scope: str="source.binary") -> str:
    with open(path.join(plugin_path, "syntaxes", scope+".sublime-syntax"), "w") as f:
        f.write(
            syntax_template.format(
                scope=scope,
                name=name,
                file_extensions="\n  - ".join(extensions),
                parent_scope=parent_scope
            )
        )
    return scope

def create_settings(scope: str, extensions: list[str]):
    with open(path.join(plugin_path, "syntaxes", scope+".sublime-settings"), "w") as f:
        dump({"extensions": extensions}, f)

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
    for icon in icons_to_delete:
        del icons[icon]


if __name__ == "__main__":
    load_syntaxes("./default_syntaxes")
    load_syntaxes("./external_syntaxes")
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
            custom_scope = create_syntax(
                extensions=orphan_extensions, 
                scope=f"mc_dp_icons.{name}", 
                name=name.replace("_file", "")
            )
            scopes[custom_scope] = orphan_extensions
        icons[name]["_scopes"] = scopes
    
    # handling collisions
    for scope, concurring_icons in taken_default_scopes.items():
        if len(concurring_icons) < 2:
            continue
        for icon in concurring_icons:
            forked_scope = f"{scope}.mc_dp_icons.{icon}"
            forked_syntax = create_syntax(
                extensions=icons[icon]["_scopes"][scope],
                parent_scope=scope,
                scope=forked_scope,
                name=scope_names[scope]
            )
            create_settings(
                scope=forked_scope, 
                extensions=icons[icon]["_scopes"][scope]
            )
            del icons[icon]["_scopes"][scope]
            icons[icon]["_scopes"][forked_syntax] = []

    for name, data in icons.items():
        create_preference(list(data["_scopes"]), name)
