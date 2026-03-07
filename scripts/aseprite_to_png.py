from PIL import Image
import aseprite


def rect_color(rect):
    p = rect["pixels"]
    return (p[0], p[1], p[2], p[3])


def draw_rect(canvas, rect):
    color = rect_color(rect)
    img = Image.new("RGBA", (rect["w"], rect["h"]), color)
    canvas.alpha_composite(img, (rect["x"], rect["y"]))


def draw_rect_opaque(canvas, rect):
    color = rect_color(rect)
    img = Image.new("RGBA", (rect["w"], rect["h"]), color)

    x, y = rect["x"], rect["y"]

    # overwrite pixels completely
    canvas.paste(img, (x, y))


def apply_group_opacity(img, opacity):
    if opacity == 255:
        return img

    r, g, b, a = img.split()
    a = a.point(lambda v: (v * opacity) // 255)
    return Image.merge("RGBA", (r, g, b, a))


def build_png(path):

    output = path.replace(".aseprite", ".png")

    sprite = aseprite.read_aseprite_file(path)

    layers = sprite["layers"]
    rects = sprite["frames"][0]["cels"]

    canvas = Image.new("RGBA", (sprite["w"], sprite["h"]), (0, 0, 0, 0))

    inside_group = False
    group_img = None
    group_opacity = 255

    for layer, rect in zip(layers, rects):

        name = layer["name"]

        if name == "gs":
            inside_group = True
            group_img = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            group_opacity = layer.get("opacity", 255)

        if inside_group:
            draw_rect_opaque(group_img, rect)
        else:
            draw_rect(canvas, rect)
        if name == "ge":
            inside_group = False

            group_img = apply_group_opacity(group_img, group_opacity)
            canvas.alpha_composite(group_img)
            group_img = None


    canvas.save(output)