from os import walk, rename

for _, __, files in walk("./"):
	for filename in files:
		splitted = filename.split(".")
		splitted[0] = splitted[0]+"_file" if not "_folder" in splitted[0] else splitted[0]
		finalname = ".".join(splitted)
		if finalname != filename:
			rename(filename, finalname)
			print("Renamed", filename, "->", finalname)
