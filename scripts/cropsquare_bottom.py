import os
from PIL import Image

def crop_and_square_small_images(input_folders, output_folder):
    """
    Crop PNG images from multiple input folders if they are under 40x40 pixels,
    then pad them to a 1:1 (square) aspect ratio based on their longest dimension.
    Saves all images to the output folder maintaining directory structure,
    aligning the texture to the bottom of the square.

    :param input_folders: List of paths to the folders containing input images.
    :param output_folder: Path to the folder to save processed images.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for input_folder in input_folders:
        if not os.path.exists(input_folder):
            print(f"Skipping {input_folder} - Directory not found.")
            continue

        for root, dirs, files in os.walk(input_folder):
            for filename in files:
                if filename.lower().endswith('.png'):
                    input_path = os.path.join(root, filename)
                    
                    # Create a safe output path to prevent overwriting
                    folder_basename = os.path.basename(os.path.normpath(input_folder))
                    relative_path = os.path.relpath(root, input_folder)
                    
                    if relative_path == ".":
                        output_folder_path = os.path.join(output_folder, folder_basename)
                    else:
                        output_folder_path = os.path.join(output_folder, folder_basename, relative_path)
                        
                    os.makedirs(output_folder_path, exist_ok=True)
                    output_path = os.path.join(output_folder_path, filename)

                    with Image.open(input_path) as img:
                        # Ensure image has an alpha channel for transparency
                        img = img.convert("RGBA")
                        width, height = img.size
                        
                        # Check if the texture is strictly under 64x64
                        if width <= 64 and height <= 64:
                            bbox = img.getbbox()
                            if bbox:
                                # Step 1: Crop to the actual visible content
                                img_cropped = img.crop(bbox)
                                cropped_w, cropped_h = img_cropped.size
                                
                                # Step 2: Find the largest dimension to make it 1:1
                                max_dim = max(cropped_w, cropped_h)
                                
                                # Step 3: Create a new transparent square image
                                square_img = Image.new("RGBA", (max_dim, max_dim), (0, 0, 0, 0))
                                
                                # Step 4: Calculate offsets to bottom-align the cropped image
                                offset_x = (max_dim - cropped_w) // 2  # Centered horizontally
                                offset_y = max_dim - cropped_h         # Aligned to the bottom vertically
                                
                                # Paste the cropped image onto the transparent square
                                square_img.paste(img_cropped, (offset_x, offset_y))
                                
                                square_img.save(output_path)
                                print(f"Squared ({max_dim}x{max_dim}) and saved: {output_path}")
                            else:
                                # Image is completely transparent/empty
                                img.save(output_path)
                                print(f"Copied empty image: {output_path}")
                        else:
                            print(f"Skipped untouched (>=64x64): {output_path}")

if __name__ == "__main__":
    # Define your list of input folders here
    input_dirs = [
        "./illustrations/authors"
    ]
    output_dir = "./icons/cropped_bottom/"
    
    crop_and_square_small_images(input_dirs, output_dir)