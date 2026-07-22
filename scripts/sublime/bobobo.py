import toml
with open("./defs/languageIcons.toml") as  f:
	print("\n".join([gex.replace("_file", "") for gex in toml.load(f).keys()]))