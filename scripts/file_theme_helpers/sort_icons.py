import os
import re

def sort_theme_file():
    # Path to the file
    file_path = './file_icon_themes/default.json'
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find '{file_path}'.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # The objects we want to sort, now including iconDefinitions
    targets = ["iconDefinitions", "folderNames", "folderNamesExpanded", "fileExtensions", "fileNames"]
    
    content_modified = False
    new_content = content

    print("Checking sort order and chunk structure...\n")

    for target in targets:
        # Regex to capture the content block of the target object.
        pattern = re.compile(r'(\s*"' + re.escape(target) + r'":\s*\{)([\s\S]*?)(\n\s*\})', re.MULTILINE)
        match = pattern.search(new_content)
        
        if not match:
            print(f"[SKIP] Could not find object '{target}'")
            continue

        prefix = match.group(1)
        body = match.group(2)
        suffix = match.group(3)

        # 1. Parse the body into Chunks
        raw_chunks = re.split(r'\n\s*\n', body)
        
        parsed_chunks = []
        needs_sorting = False

        # Define specific parsing and sorting rules depending on the target
        if target == "iconDefinitions":
            # Matches: "key": {"iconPath": "..."}
            pair_pattern = re.compile(r'"([^"]+)"\s*:\s*(\{[^}]+\})')
            # Sort only by the key (icon name)
            sort_key_func = lambda x: x[0].lower()
        else:
            # Matches: "key": "value"
            pair_pattern = re.compile(r'"([^"]+)"\s*:\s*"([^"]+)"')
            # Sort by VALUE first, then KEY
            sort_key_func = lambda x: (x[1].lower(), x[0].lower())

        for chunk in raw_chunks:
            pairs = pair_pattern.findall(chunk)
            if not pairs:
                continue

            # 2. Check Sorting
            sorted_pairs = sorted(pairs, key=sort_key_func)
            
            if pairs != sorted_pairs:
                needs_sorting = True
            
            parsed_chunks.append(sorted_pairs)

        if needs_sorting:
            print(f"[-] '{target}' is NOT sorted correctly.")
            user_input = input(f"    >>> Do you want to sort '{target}' now? (y/n): ").strip().lower()
            
            if user_input == 'y':
                # 3. Reconstruct the Body
                new_body_parts = []
                
                for i, chunk_pairs in enumerate(parsed_chunks):
                    chunk_lines = []
                    for key, value in chunk_pairs:
                        if target == "iconDefinitions":
                            # value already contains the braces {}
                            chunk_lines.append(f'    "{key}": {value}')
                        else:
                            # value needs quotes
                            chunk_lines.append(f'    "{key}": "{value}"')
                    
                    chunk_text = ",\n".join(chunk_lines)
                    new_body_parts.append(chunk_text)

                full_body_text = ",\n\n".join(new_body_parts)
                
                if not full_body_text.startswith('\n'):
                    full_body_text = '\n' + full_body_text

                new_block = prefix + full_body_text + suffix
                
                new_content = new_content.replace(match.group(0), new_block)
                content_modified = True
                print(f"    [FIXED] '{target}' sorted locally (pending save).")
            else:
                print("    [SKIPPED] Keeping original order.")
        else:
            print(f"[OK] '{target}' is sorted correctly \u2713")

    # Final Save
    if content_modified:
        print("\nSaving changes to file...")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Done! File updated.")
    else:
        print("\nNo changes made.")

if __name__ == "__main__":
    sort_theme_file()