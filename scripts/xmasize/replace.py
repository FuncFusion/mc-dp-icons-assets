from PIL import Image
import numpy as np
from os import walk, path

def find_pattern(image, pattern):
    """
    Finds all occurrences of the pattern in the image.
    :param image: The target image as a numpy array.
    :param pattern: The pattern to search for as a numpy array.
    :return: A list of top-left corner coordinates of matching regions.
    """
    ih, iw, _ = image.shape
    ph, pw, _ = pattern.shape
    matches = []
    
    for y in range(ih - ph + 1):
        for x in range(iw - pw + 1):
            if np.array_equal(image[y:y+ph, x:x+pw], pattern):
                matches.append((x, y))
    return matches

def replace_pattern(image, matches, replacement):
    """
    Replaces all occurrences of a pattern in the image with the replacement.
    :param image: The target image as a numpy array.
    :param matches: List of top-left corner coordinates for matches.
    :param replacement: The replacement pattern as a numpy array.
    :return: The modified image as a numpy array.
    """
    ph, pw, _ = replacement.shape
    for (x, y) in matches:
        image[y:y+ph, x:x+pw] = replacement
    return image

def replace_relative_pixels(image, matches, color_to_replace, replacement_color, offsets):
    """
    Replaces specific pixels relative to the right-down corner of the matched pattern.
    :param image: The target image as a numpy array.
    :param matches: List of top-left corner coordinates for matches.
    :param color_to_replace: The color to replace (tuple of RGBA values).
    :param replacement_color: The replacement color (tuple of RGBA values).
    :param offsets: A list of (dx, dy) offsets from the bottom-right corner of the pattern.
    :return: The modified image as a numpy array.
    """
    for (x, y) in matches:
        for dx, dy in offsets:
            tx = x + dx
            ty = y + dy
            # Check bounds
            if 0 <= ty < image.shape[0] and 0 <= tx < image.shape[1]:
                if tuple(image[ty, tx]) == color_to_replace:
                    image[ty, tx] = replacement_color
    return image


# # Replace pixels relative to the bottom-right corner
# pattern_height, pattern_width, _ = pattern_array.shape
# bottom_right_offsets = [(11, 0), (12, 0), (11, -1), (12, -1)]  # Offsets relative to the bottom-right corner
# color_to_replace = (255, 255, 255, 255)  # White in RGBA
# replacement_color = (0, 0, 0, 255)  # Black in RGBA

# # Adjust offsets relative to the bottom-right corner of the pattern
# adjusted_offsets = [(pattern_width - 1 + dx, pattern_height - 1 + dy) for dx, dy in bottom_right_offsets]
# target_array = replace_relative_pixels(target_array, matches, color_to_replace, replacement_color, adjusted_offsets)

# # Save the modified image as a transparent PNG
# modified_image = Image.fromarray(target_array, mode="RGBA")
# modified_image.save("modified_image.png", format="PNG")





def replace_colors_in_image(image_array, color_map, output_path):
    """
    Replace specified colors in an image with new colors based on a given map.

    Args:
        image_path (str): Path to the input image.
        color_map (dict): A dictionary where keys are colors to be replaced
                          (hex codes, e.g., "#FFFFFF") and values are their replacements.
        output_path (str): Path to save the output image.
    """
    # Convert hex color codes to RGB tuples
    color_map_rgb = {hex_to_rgb(k): hex_to_rgb(v) for k, v in color_map.items()}

    # Open the image  # Ensure the image supports transparency
    image = Image.fromarray(image_array, mode="RGBA").copy()
    pixels = image.load()

    # Iterate through pixels and replace colors
    for y in range(image.height):
        for x in range(image.width):
            current_color = pixels[x, y][:3]  # Ignore alpha for matching
            if current_color in color_map_rgb:
                new_color = color_map_rgb[current_color]
                pixels[x, y] = (*new_color, pixels[x, y][3])  # Preserve the alpha channel

    # Save the modified image
    image.save(output_path)

def hex_to_rgb(hex_code):
    """
    Convert a hex color code to an RGB tuple.

    Args:
        hex_code (str): Hex color code (e.g., "#FFFFFF").

    Returns:
        tuple: RGB color as a tuple (R, G, B).
    """
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

#
down_pattern = np.array(Image.open("down.png").convert("RGBA"))
down_replacement = np.array(Image.open("down_r.png").convert("RGBA"))

left_side_offsets_frame = [(-4, -11), (-1, -11), (-4, -12), (-1, -12)]
left_side_offsets_wood = [(-3, -11), (-2, -11), (-3, -12), (-2, -12)]
left_offsets = [(0, -11), (1, -11), (0, -12), (1, -12)]
right_offsets = [(10, -11), (11, -11), (10, -12), (11, -12)]
top_offsets = [(5, -16), (6, -16)]
down_offsets = [(5, -6), (6, -6), (5, -7), (6, -7)]

chest_frame_shadowed = list(hex_to_rgb("#1D1A14"))
chest_frame_shadowed.append(255)
chest_frame_shadowed = tuple(map(np.uint8, chest_frame_shadowed))
wrapping_strip = list(hex_to_rgb("#DAC83D"))
wrapping_strip.append(255)
wrapping_strip = tuple(map(np.uint8, wrapping_strip))
chest_wood_shadowed = list(hex_to_rgb("#865107"))
chest_wood_shadowed.append(255)
chest_wood_shadowed = tuple(map(np.uint8, chest_wood_shadowed))
wrapping_strip_shadowed = list(hex_to_rgb("#A4962D"))
wrapping_strip_shadowed.append(255)
wrapping_strip_shadowed = tuple(map(np.uint8, wrapping_strip_shadowed))

color_replacements = {
    "#A5A5A5": "#DAC83D", 
    "#767676": "#A4962D", 
    "#693F05": "#310604", 
    "#1D1A14": "#8A2519", 
    "#A76E1F": "#A41711",
    "#453C2F": "#B63021",
    "#865107": "#7C120D"
}
out_folder = path.abspath("xmased_icons")


for folder_path, _, filenames in walk(path.abspath("icons")):
    for filename in filenames:
        target_icon = np.array(Image.open(path.join(folder_path, filename)))

        # Replacing constant parts
        down_matches = find_pattern(target_icon, down_pattern)
        target_icon = replace_pattern(target_icon, down_matches, down_replacement)

        # Drawing wrapping strip
        for offsets, replace_color in zip((left_side_offsets_frame, left_side_offsets_wood), (chest_frame_shadowed, chest_wood_shadowed)):
            target_icon = replace_relative_pixels(
                    target_icon, down_matches, 
                    replace_color, wrapping_strip_shadowed, 
                    offsets
                )
        for offsets in (left_offsets, right_offsets, top_offsets, down_offsets):
            target_icon = replace_relative_pixels(
                target_icon, down_matches, 
                chest_frame_shadowed, wrapping_strip, 
                offsets
            )

        # Replacing the rest of pixels
        replace_colors_in_image(target_icon, color_replacements, path.join(out_folder, filename.split(".")[0]+"_xmas.png"))

