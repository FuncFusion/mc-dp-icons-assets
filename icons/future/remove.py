from os import walk, remove

for _, __, filenames in walk("./"):
	for file in filenames:
		if "_xmas" in file:
			print(file)
			remove(file)