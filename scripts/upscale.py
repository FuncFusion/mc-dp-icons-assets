import os
from PIL import Image

def upscale_images(input_folder, output_folder, target_size=1000):
    """
    Upscale PNG images in the input folder so their largest dimension becomes target_size
    while maintaining aspect ratio and keeping the original padding, and save them to the output folder.

    :param input_folder: Path to the folder containing input images
    :param output_folder: Path to the folder to save processed images
    :param target_size: The size to which the largest dimension of the image should be scaled
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if filename.lower().endswith('.png'):
                input_path = os.path.join(root, filename)
                output_folder_path = os.path.join(output_folder, root.replace(input_folder, ""))
                output_path = os.path.join(output_folder_path, filename)
                os.makedirs(output_folder_path, exist_ok=True)

                with Image.open(input_path) as img:
                    # Compute scaling factor from the full image, no cropping
                    width, height = img.size
                    scaling_factor = target_size / max(width, height)

                    # Resize image using nearest-neighbor method
                    new_size = (int(width * scaling_factor), int(height * scaling_factor))
                    img_resized = img.resize(new_size, Image.Resampling.NEAREST)

                    # Save the processed image
                    img_resized.save(output_path)

                    print(f"Processed and saved: {output_path}")

if __name__ == "__main__":
    input_dir = "./icons/current/"
    output_dir = "./icons/nocrop_upscaled/"
    upscale_images(input_dir, output_dir)
