import os
import json

def create_xmas_theme():
    default_json_path = './file_icon_themes/default.json'
    xmas_json_path = './file_icon_themes/xmas.json'
    icons_dir = './icons'

    if not os.path.exists(default_json_path):
        print(f"Error: Could not find '{default_json_path}'. Make sure you are in the project root.")
        return

    print(f"Reading {default_json_path}...\n")

    # Read the raw string to preserve all custom formatting and compactness
    with open(default_json_path, 'r', encoding='utf-8') as f:
        raw_content = f.read()

    # Parse as JSON temporarily just to get the valid definitions
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError as e:
        print(f"FATAL: Could not parse JSON file.\nError: {e}")
        return

    if "iconDefinitions" not in data:
        print("Error: 'iconDefinitions' object not found in JSON.")
        return

    icon_definitions = data["iconDefinitions"]
    modifications_made = 0

    print("--- Scanning for Christmas variants ---")

    for key, value in icon_definitions.items():
        original_path = value.get("iconPath")
        if not original_path:
            continue

        filename = os.path.basename(original_path)
        name, ext = os.path.splitext(filename)

        xmas_filename = f"{name}_xmas{ext}"
        xmas_file_path = os.path.join(icons_dir, xmas_filename)

        if os.path.exists(xmas_file_path):
            new_path = original_path.replace(filename, xmas_filename)
            
            # Target the exact JSON value string to avoid accidental replacements elsewhere
            target_str = f'"{original_path}"'
            replacement_str = f'"{new_path}"'
            
            # Replace the string in the raw text block
            if target_str in raw_content:
                raw_content = raw_content.replace(target_str, replacement_str)
                modifications_made += 1
                print(f"  [UPDATED] '{key}': {filename} -> {xmas_filename}")

    print(f"\nWriting to {xmas_json_path}...")
    
    # Write the modified raw text back to the file
    with open(xmas_json_path, 'w', encoding='utf-8') as f:
        f.write(raw_content) 

    print(f"Done! Successfully created/updated xmas.json with {modifications_made} Christmas icons.")

if __name__ == "__main__":
    create_xmas_theme()