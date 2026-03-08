import os
import json

def check_default_theme():
    # Path to your JSON file
    json_path = './file_icon_themes/default.json'
    
    if not os.path.exists(json_path):
        print(f"Error: Could not find '{json_path}'. Make sure you are in the project root.")
        return

    print(f"Scanning {json_path}...\n")

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"FATAL: Could not parse JSON file.\nError: {e}")
        return

    # --- Get Defined Icons ---
    if "iconDefinitions" not in data:
        print("Error: 'iconDefinitions' object not found in JSON.")
        return

    icon_definitions = data["iconDefinitions"]
    # Create a set of all valid icon keys (e.g., "advancement_file", "folder_xmas")
    valid_keys = set(icon_definitions.keys())


    # ==========================================
    # PHASE 1: Check Icon Definitions (Files & Names)
    # ==========================================
    print("--- Phase 1: Checking Icon Files & Names ---")
    phase1_issues = False
    base_dir = os.path.dirname(json_path) # ./file_icon_themes

    for key, value in icon_definitions.items():
        # Check 1: File Existence
        relative_path = value.get("iconPath")
        if not relative_path:
            print(f"[ERROR] '{key}' is missing 'iconPath'")
            phase1_issues = True
            continue

        full_path = os.path.normpath(os.path.join(base_dir, relative_path))
        if not os.path.exists(full_path):
            print(f"[FILE MISSING] Key: '{key}' -> File not found: {full_path}")
            phase1_issues = True

        # Check 2: Naming Match (Key == Filename)
        filename = os.path.splitext(os.path.basename(relative_path))[0]
        if key != filename:
            print(f"[NAME MISMATCH] Key: '{key}' != Filename: '{filename}'")
            phase1_issues = True

    if not phase1_issues:
        print("Icon files and names are correct \u2713")


    # ==========================================
    # PHASE 2: Check Mappings (References)
    # ==========================================
    print("\n--- Phase 2: Checking Mappings (Linking) ---")
    
    # The sections you requested to check
    sections_to_check = ["folderNames", "folderNamesExpanded", "fileExtensions", "fileNames"]
    phase2_issues = False

    for section in sections_to_check:
        if section not in data:
            print(f"Warning: Section '{section}' not found in JSON, skipping...")
            continue
        
        print(f"Checking '{section}'...")
        section_obj = data[section]
        
        # Iterate through mappings like "advancement/json": "advancement_file"
        for map_key, icon_ref in section_obj.items():
            if icon_ref not in valid_keys:
                print(f"  [BROKEN LINK] In '{section}':")
                print(f"      Key '{map_key}' points to icon '{icon_ref}'")
                print(f"      BUT '{icon_ref}' does not exist in 'iconDefinitions'.")
                phase2_issues = True

    if not phase2_issues:
        print("All mappings are correct \u2713")


    # ==========================================
    # PHASE 3: Check for Unused Icons in Folder
    # ==========================================
    print("\n--- Phase 3: Checking for Unused Icons ---")
    phase3_issues = False
    icons_dir = './icons'

    if not os.path.exists(icons_dir):
        print(f"[ERROR] Could not find '{icons_dir}' folder. Skipping Phase 3.")
    else:
        # Collect all filenames that are actually used in the default JSON definitions
        used_icon_files = set()
        for value in icon_definitions.values():
            rel_path = value.get("iconPath")
            if rel_path:
                used_icon_files.add(os.path.basename(rel_path))

        # Check xmas.json and add its defined icons to the used set
        xmas_json_path = './file_icon_themes/xmas.json'
        if os.path.exists(xmas_json_path):
            try:
                with open(xmas_json_path, 'r', encoding='utf-8') as f:
                    xmas_data = json.load(f)
                    if "iconDefinitions" in xmas_data:
                        for value in xmas_data["iconDefinitions"].values():
                            rel_path = value.get("iconPath")
                            if rel_path:
                                used_icon_files.add(os.path.basename(rel_path))
            except json.JSONDecodeError as e:
                print(f"  [WARNING] Could not parse '{xmas_json_path}'. Error: {e}")
        else:
            print(f"  [WARNING] '{xmas_json_path}' not found. Christmas icons might be flagged as unused.")

        # Check all .svg files in the icons folder
        for filename in os.listdir(icons_dir):
            if filename.endswith(".svg"):
                if filename not in used_icon_files:
                    print(f"  [UNUSED ICON] '{filename}' is in the folder but not defined in default.json or xmas.json")
                    phase3_issues = True

        if not phase3_issues:
            print("No unused icons found \u2713")


if __name__ == "__main__":
    check_default_theme()