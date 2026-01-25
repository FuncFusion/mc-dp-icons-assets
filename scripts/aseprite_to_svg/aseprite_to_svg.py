import aseprite


scale = 50
svg = '<svg viewBox="0 0 {0} {1}" xmlns="http://www.w3.org/2000/svg">{2}</svg>'
rect_template = '<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#{fill}" {opacity}/>'


def convert(path):
	sprite = aseprite.read_aseprite_file(path)
	minx = sprite["w"]
	miny = sprite["h"]
	maxx = 0
	maxy = 0
	rects = ""
	rect_data = []

	for layer in sprite["frames"][0]["cels"]:
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
	
		rect_data.append({
			"x": x, 
			"y": y,
			"w": w,
			"h": h,
			"fill": layer["pixels"][:3].hex(),
			"opacity": "" if layer["pixels"][3] == 255 else f'opacity="{str(layer["pixels"][3]/255)[1:]}"'
		})
	
	
	for rect in rect_data:
		rect["x"] = (rect["x"] - minx) * scale
		rect["y"] = (rect["y"] - miny) * scale
		rect["w"] *= scale
		rect["h"] *= scale
		rects += rect_template.format(**rect)

	return svg.format((maxx-minx)*scale, (maxy-miny)*scale, rects)


if __name__ == "__main__":
	# with open("svg.svg","w")as f:
	# 	f.write(convert("loom.aseprite"))
	from os import walk

	icons_path = "../../icons/current/"

	for _, __, files in walk(icons_path):
		for filename in files:
			if filename.endswith(".aseprite"):
				with open(filename[:-9]+".svg", "w")as f:
					f.write(convert(icons_path+filename))
				print("Processed " filename)
