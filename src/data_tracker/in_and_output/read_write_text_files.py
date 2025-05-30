import json
import os

def load_json(json_filepath):
    try:
        dict_settings = {}
        with open(json_filepath, "r", encoding="utf-8") as j:
            dict_settings = json.loads(j.read())
    except Exception as e:
        print(f"Error loading JSON: {e}")
    return dict_settings


def write_json_file(dict_json, json_name):
    # formerly: json_name, json_file
    try:
        with open(json_name, "w") as outfile:
            json.dump(dict_json, outfile, sort_keys=True, indent=4)
        print(f"wrote JSON: {dict_json}")
    except Exception as e:
        print(f"Error writingJSON: {e}")


def find_newest_file_with_restraints(dict_global):
    """
    get list of files in the tree starting from a reference root
    that correspond to a patten
    get the newest file, and updata dict_global accordingly
    """
    file_ending = dict_global["pattern_auto_file_search"]
    found_files = find_files(
        source_dir=dict_global["root_dir_data_files"],
        starts_with="",
        contains="",
        file_ending=file_ending,
    )
    dict_global["dat_file"] = get_newest_file_from_list(found_files)
    # dict_global["dat_file"] = file
    print(f"\nfound file {dict_global['dat_file']}")


def find_files(source_dir, starts_with="", contains="", file_ending=""):
    found_files = [
        os.path.join(d, x)
        for d, dirs, files in os.walk(source_dir)
        for x in files
        # if x.endswith(file_ending)
        if x.startswith(starts_with) and x.endswith(file_ending)
    ]
    return found_files


def get_newest_file_from_list(file_list):
    """Returns the newest file from a list based on modification date."""
    if not file_list:
        return None  # Return None if the list is empty

    return max(file_list, key=os.path.getmtime)

