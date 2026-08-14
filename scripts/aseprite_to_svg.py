import aseprite


post_align_scale = 1
pre_align_scale = 50
CRISP = True

if CRISP:
    svg = '<svg viewBox="0 0 {0} {1}" shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg">{2}</svg>'
else:
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

    minx *= pre_align_scale
    maxx *= pre_align_scale
    miny *= pre_align_scale
    maxy *= pre_align_scale
    true_width = maxx - minx
    true_height = maxy - miny
    max_side = max(true_width, true_height)
    offsetx = (max_side - true_width) // 2
    offsety = (max_side - true_height + 1) // 2
    
    for element in element_data:
        type = element["type"]

        if type == "group_start":
            elements += group_start_template.format(**element)

        elif type == "group_end":
            elements += "</g>"

        elif type == "rect":
            element["x"] = (element["x"]*pre_align_scale - minx + offsetx) * post_align_scale
            element["y"] = (element["y"]*pre_align_scale - miny + offsety) * post_align_scale
            element["w"] *= pre_align_scale * post_align_scale
            element["h"] *= pre_align_scale * post_align_scale
            elements += rect_template.format(**element)

    return svg.format(max_side*post_align_scale, max_side*post_align_scale, elements)


# print(convert("../icons/current/misc_file.aseprite"))

if __name__ == "__main__":
    from os import walk, getcwd
    from os.path import abspath, join

    icons_path = "icons/current"
    out_path = "neovim/svgs"
    # in case script is not running from the root of repo
    if getcwd().endswith("scripts"):
        icons_path = "../" + icons_path

    for root, __, files in walk(icons_path):
        for filename in files:
            if filename.endswith(".aseprite"):
                svg_path = join(out_path, filename[:-9]+".svg")
                with open(svg_path, "w")as f:
                    f.write(convert(join(icons_path, filename)))
                print("Processed " + filename)
