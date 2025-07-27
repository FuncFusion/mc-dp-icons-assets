import os
from PIL import Image, ImageOps

def crop_and_upscale_images(input_folder, output_folder, target_size=1000):
    """
    Crop PNG images in the input folder by their content, upscale the largest dimension to target_size
    while maintaining aspect ratio, and save them to the output folder.

    :param input_folder: Path to the folder containing input images
    :param output_folder: Path to the folder to save processed images
    :param target_size: The size to which the largest dimension of the image should be scaled
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.png'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            with Image.open(input_path) as img:
                # Crop image to content
                img_cropped = ImageOps.crop(img, border=0)
                bbox = img_cropped.getbbox()
                if bbox:
                    img_cropped = img_cropped.crop(bbox)

                # Compute scaling factor
                width, height = img_cropped.size
                scaling_factor = target_size / max(width, height)

                # Resize image using nearest-neighbor method
                new_size = (int(width * scaling_factor), int(height * scaling_factor))
                img_resized = img_cropped.resize(new_size, Image.Resampling.NEAREST)

                # Save the processed image
                img_resized.save(output_path)

                print(f"Processed and saved: {output_path}")

if __name__ == "__main__":
    input_dir = r"../../icons/future/files/coding"
    output_dir = r"../../icons/future/us"
    crop_and_upscale_images(input_dir, output_dir)
