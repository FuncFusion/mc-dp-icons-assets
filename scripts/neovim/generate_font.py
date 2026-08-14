#========================================================================#
#                                                                        #
#  SHOULD BE EXECUTED IN VIRTUAL ENVIRONMENT WITH *NANOEMOJI* INSTALLED  #
#                                                                        #
#========================================================================#
# *Paths are configured for the script to be ran at `scripts/neovim/`


from os import path
from shutil import copy
import toml
from subprocess import run


LOAD_FONT = True  # Linux only
REGENERATE_FONT = True
starting_char = "F800"
defs_folder = "../sublime/defs"
icons_folder = "svgs"
output_folder = "named_icons"
base_symbol = "1FA8E"
base_symbol_chr = chr(int(base_symbol, 16))
icon_list = "../../icons/.list"

default_dir = "generic_folder_closed"
default_file = "generic_file"

default_icons = '''default = {{
directory = {{ glyph = '{default_dir}',  hl = 'MiniIconsGreen' }},
extension = {{ glyph = '{default_file}', hl = 'MiniIconsGreen' }},
file      = {{ glyph = '{default_file}', hl = 'MiniIconsGreen' }},
filetype  = {{ glyph = '{default_file}', hl = 'MiniIconsGreen' }},
}},
'''

creation_command = [
    "nanoemoji", 
    "--color_format", "glyf_colr_1", 
    "--family", "Datapack Icons", 
    "--output_file", "datapack_icons.ttf"
]

icon_packs = [
    "generalIcons.toml",
    "languageIcons.toml",
    "bedrockAddonIcons.toml",
    "bedrockResourceIcons.toml",
    "dataPackIcons.toml",
    "resourcePackIcons.toml"
]

icon_chars_table = {}
icon_definition = '["{key}"]={{glyph="{chars}",hl="MiniIconsGreen"}},'
mini_icons_exts = ""
mini_icons_files = ""
mini_icons_dirs = ""

icons = {}

# LOAD ICON LISTS
with open(icon_list, "r") as f:
    for i in f.read().split("\n"):
        icons[i] = {}

# LOAD ICON DEFINITIONS
for icon_pack in icon_packs:
    with open(path.join(defs_folder, icon_pack), "r") as f:
        icons.update(toml.load(f))


index = int(starting_char, 16)
for icon in icons:
    chars = f"{base_symbol_chr}{chr(index)}"
    icon_chars_table[icon] = chars

    if "extensions" in icons[icon]:
        for extension in icons[icon]["extensions"]:
            if "/" in extension: continue
            mini_icons_exts += icon_definition.format(
                key=extension,
                chars=chars
            )
    if "filenames" in icons[icon]:
        for filename in icons[icon]["filenames"]:
            if "/" in filename: continue
            mini_icons_files += icon_definition.format(
                key=filename,
                chars=chars
            )
    if "foldernames" in icons[icon]:
        for foldername in icons[icon]["foldernames"]:
            if "/" in foldername: continue
            mini_icons_dirs += icon_definition.format(
                key=foldername,
                chars=chars
            )
            
    icon_out_path = path.join(output_folder, f"{base_symbol}-{index:0{4}X}.svg")
    if REGENERATE_FONT:
        copy(
            path.join(icons_folder, f"{icon}.svg"),
            icon_out_path
        )
        creation_command.append(icon_out_path)
    index += 1


import pyperclip
mini_conf = (
    default_icons.format(default_dir=icon_chars_table[default_dir], default_file=icon_chars_table[default_file])+
    f"file = {{{mini_icons_files}}},\n"
    f"extension = {{{mini_icons_exts}}},\n"
    f"directory = {{{mini_icons_dirs}}}"
)
print(mini_conf)
pyperclip.copy(mini_conf)


with open("icon_chars.toml", "w") as f:
    toml.dump(icon_chars_table, f)


if REGENERATE_FONT:
    run(creation_command)

    if LOAD_FONT:
        run(["fc-cache", "-fv"])
        run(["cp", "nanoemoji/build/datapack_icons.ttf", path.expanduser("~/.local/share/fonts/datapack_icons.ttf")])
