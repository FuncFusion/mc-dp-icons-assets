import aseprite


scale = 50
# svg = '<svg viewBox="0 0 {0} {1}" shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg">{2}</svg>'
svg = '<svg viewBox="0 0 {0} {1}" xmlns="http://www.w3.org/2000/svg">{2}</svg>'
rect_template = '<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#{fill}" {opacity}/>'
group_start_template = '<g {opacity}>'


def convert(path):
	sprite = aseprite.read_aseprite_file(path)
	minx = sprite["w"]
	miny = sprite["h"]
	maxx = 0
	maxy = 0
	elements = ""
	element_data = []

	in_group: bool = False
	for layer, meta in zip( sprite["frames"][0]["cels"], sprite["layers"]):
		name = meta["name"]

		x = layer["x"]
		y = layer["y"]
		w = layer["w"]
		h = layer["h"]
		if x < minx:
			minx = x
		if y < miny:
			miny = y
		if (mx:=x+w) > maxx:
			maxx = mx
		if (my:=y+h) > maxy:
			maxy = my
	
		rect = {
			"type": "rect",
			"x": x, 
			"y": y,
			"w": w,
			"h": h,
			"fill": layer["pixels"][:3].hex(),
			"opacity": "" if layer["pixels"][3] == 255 or in_group or name in ("gs", "ge") else f'opacity="{str(layer["pixels"][3]/255)[1:]}"'
		}

		if name == "gs":
			element_data.append({
				"type": "group_start",
				"opacity": f'opacity="{str(layer["pixels"][3]/255)[1:]}"'
			})
			element_data.append(rect)
			in_group = True

		elif name == "ge" and in_group:
			element_data.append(rect)
			element_data.append({
				"type": "group_end"
			})
			in_group = False

		else:
			element_data.append(rect)
	
	
	for element in element_data:
		type = element["type"]

		if type == "group_start":
			elements += group_start_template.format(**element)

		elif type == "group_end":
			elements += "</g>"

		elif type == "rect":
			element["x"] = (element["x"] - minx) * scale
			element["y"] = (element["y"] - miny) * scale
			element["w"] *= scale
			element["h"] *= scale
			elements += rect_template.format(**element)

	return svg.format((maxx-minx + (1 if maxx-minx % 2 == 1 else 0))*scale, (maxy-miny + (1 if maxy-miny % 2 == 1 else 0))*scale, elements)


print(convert("../../icons/current/fsh.aseprite"))

# if __name__ == "__main__":
# 	from os import walk
# 	from os.path import abspath
# 	import webbrowser

# 	icons_path = "../../icons/future/" # <- SLASH IN THE END OF PATH IS NECCESSARY

# 	for root, __, files in walk(icons_path):
# 		for filename in files:
# 			if filename.endswith(".aseprite"):
# 				svg_path = icons_path+filename[:-9]+".svg"
# 				with open(svg_path, "w")as f:
# 					f.write(convert(icons_path+filename))
# 					# webbrowser.open("file:///"+abspath(svg_path).replace("\\", "/"))
# 				print("Processed " + filename)
