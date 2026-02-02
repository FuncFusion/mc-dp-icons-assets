import aseprite


scale = 50
# svg = '<svg viewBox="0 0 {0} {1}" shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg">{2}</svg>'
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

	return svg.format((maxx-minx + (1 if maxx-minx % 2 == 1 else 0))*scale, (maxy-miny + (1 if maxy-miny % 2 == 1 else 0))*scale, rects)


if __name__ == "__main__":
	from os import walk
	from os.path import abspath
	import webbrowser

	icons_path = "../../icons/future/files/coding/" # <- SLASH IN THE END OF PATH IS NECCESSARY

	for root, __, files in walk(icons_path):
		for filename in files:
			if filename.endswith(".aseprite"):
				svg_path = icons_path+filename[:-9]+".svg"
				with open(svg_path, "w")as f:
					f.write(convert(icons_path+filename))
					# webbrowser.open("file:///"+abspath(svg_path).replace("\\", "/"))
				print("Processed " + filename)
