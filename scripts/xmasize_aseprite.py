import aseprite
from aseprite_to_png import build_png

# xmas_folder_template = aseprite.read_aseprite_file("folder_xmas.aseprite")


def xmasize(path: str):
	# xmased_icon = xmas_folder_template.copy().copy()
	xmased_icon = aseprite.read_aseprite_file("folder_xmas.aseprite")
	sprite = aseprite.read_aseprite_file(path)

	cels = sprite["frames"][0]["cels"]
	layers = sprite["layers"]

	content_inner = {"cels": [], "layers": []}
	content_over = {"cels": [], "layers": []}

	for index, layer in enumerate(layers):
		if layer["name"] == "----":
			content_inner_start = index+1
		elif layer["name"] == "---":
			content_inner_end = index
		elif layer["name"] == "--":
			content_outer_start = index+1

	content_inner["cels"] = cels[content_inner_start: content_inner_end][::-1]
	content_inner["layers"] = layers[content_inner_start: content_inner_end][::-1]

	content_over["cels"] = cels[content_outer_start :]
	content_over["layers"] = layers[content_outer_start :]


	for cel, layer in zip(content_inner["cels"], content_inner["layers"]):
		xmased_icon["frames"][0]["cels"].insert(9, cel)
		xmased_icon["layers"].insert(9, layer)

	for cel, layer in zip(content_over["cels"], content_over["layers"]):
		xmased_icon["frames"][0]["cels"].append(cel)
		xmased_icon["layers"].append(layer)

	for index, cel in enumerate(xmased_icon["frames"][0]["cels"]):
		xmased_icon["frames"][0]["cels"][index]["layer"] = index

	out_path = path.replace(".aseprite", "_xmas.aseprite")
	aseprite.write_aseprite_file(out_path, xmased_icon)
	return out_path


# xmasize("../icons/future/jetbrains_folder.aseprite")


exlusions = (
	"overlay_folder",
	"assets_folder",
	"data_folder",
	"namespace_folder",
	"src_folder"
)


if __name__ == "__main__":
	from os import walk
	from os.path import abspath
	import webbrowser

	icons_path = "../icons/future/"
	icons_path += "/" if not icons_path.endswith("/") else ""

	for root, __, files in walk(icons_path):
		for filename in files:
			if filename.endswith("_folder.aseprite") and not any(True for exlusion in exlusions if exlusion in filename):
				print("Processing "+filename)
				saved_path = xmasize(icons_path+filename)
				build_png(saved_path)
