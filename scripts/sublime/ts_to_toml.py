import re
import os

keyvalue = re.compile(r"(?s)(?P<key>\w+): (?P<value>\[.*?\]|\"[\w\.]+\")")

def convert_ts_to_toml(input_ts_file, output_toml_file):
    with open(input_ts_file, "r") as f:
        contents = f.read()

    icon_defs = re.findall(r"(?s){.*?}", contents)

    # cleanup
    open(output_toml_file, "w").close()

    with open(output_toml_file, "a") as f:

        for icon_def in icon_defs:
            toml_entry = ""
            items = dict(keyvalue.findall(icon_def))

            print("Processing", items["name"])

            name = items["name"]
            if not "." in name:
                name = name.replace('"', "")
            toml_entry += f"[{name}]\n"
            del items["name"]

            if len(items) == 0:
                continue
            for key, value in items.items():
                toml_entry += f"{key} = {value}\n"

            toml_entry += "\n"
            f.write(toml_entry)


    

if __name__ == "__main__":
    convert_ts_to_toml("defs/languageIcons.ts", "languageIcons.toml")
