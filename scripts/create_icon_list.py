import os


icons = []
for _, __, files in os.walk("icons/current/"):
	for file in files:
		name = ".".join(file.split(".")[:-1])
		if name not in icons:
			icons.append(name)

with open("icons/.list", "w") as f:
	f.write("\n".join(icons))
