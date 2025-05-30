from ..async_elements.loops import start_data_streaming
from ..in_and_output.read_write_text_files import (
    json,
    load_json,
    write_json_file,
    find_newest_file_with_restraints,
)
from ..plotting.set_lines_in_plot import set_axis_on_auto_zoom_respecting_user_limits

import os
import sys
import traceback


def button_function_autosearch_file(dict_global):
    find_newest_file_with_restraints(dict_global)
    text_input_entry = dict_global["gui_elements"]["text_input_entry_dat_filepath"]
    print(type(text_input_entry))
    # print(ddddd)
    # Clear the existing content
    text_input_entry.delete(0, "end")

    # Insert the new filename
    # TODO: this needs some refinement: does not act well if the path is not valid or so, ??? if None???
    text_input_entry.insert(0, dict_global.get("dat_file", "empty"))


def button_function_load_user_settings(dict_global):
    try:
        json_filepath = dict_global["json_filepath"]
        dict_user_settings = load_json(json_filepath)
        # dict_user_settings = {}
        dict_global = {**dict_global, **dict_user_settings}
        print("\n\n")
        print(f"Loaded JSON user settings from disk: ")
        print(json.dumps(dict_user_settings, indent=4, separators=(",", ": ")))

    except Exception as e:
        print("error in load_user_settings")
        print(e)
        traceback.print_exc()


def button_function_save_user_settings(dict_global):
    try:
        dict_user_settings = {
            key: dict_global[key] for key in dict_global["dict_user_settings_keys"]
        }
        # print(dict_user_settings)
        # print("IMPLEMENT JSON SAVER")
        write_json_file(dict_user_settings, dict_global["json_filepath"])
        print("\n\n")
        # print("IMPLEMENT PRETTY PRINT!!!")
        print(f"Wrote JSON user settings to disk: ")
        print(json.dumps(dict_user_settings, indent=4, separators=(",", ": ")))
    except Exception as e:
        print("error in save_user_settings")
        traceback.print_exc()
        print(e)


# def start_data_streaming(dict_global):
#     """Ensures the asyncio loop is running and starts the data streaming task."""
#     start_asyncio_loop(dict_global)  # Ensure event loop is running
#     async_loop = dict_global["threading"]["async_loop"]
#     asyncio.run_coroutine_threadsafe(update_plot_async(dict_global), async_loop)


def button_function_exit_app(dict_global):
    print("Exiting application")
    dict_global["root"].quit()
    dict_global["root"].destroy()
    # sys.exit()


def button_function_reset_auto_zoom(dict_global):
    dict_global["auto_zoom"] = not dict_global["auto_zoom"]
    dict_global["gui_elements"]["auto_zoom_button"].config(
        text=f"Auto Zoom: {dict_global['auto_zoom']}"
    )
    if dict_global["auto_zoom"]:
        set_axis_on_auto_zoom_respecting_user_limits(dict_global)
        dict_global["canvas"].draw()


def button_function_save_current_settings():
    dict_filtered = {}
    for key, value in dict_settings.items():
        dict_filtered[key] = value
    return dict_filtered


import time


def button_function_save_plot_as_png(dict_global):
    timestr = time.strftime("%Y%m%d_%H%M%S")
    png_name = dict_global["name_png"]
    a, b = os.path.splitext(png_name)
    # print(a, b)
    png_name = f"{a}_{timestr}{b}"
    dict_global["fig"].savefig(png_name, bbox_inches="tight")
    print(f"Saved file as {png_name}")


def button_function_toggle_csv_stream(dict_global):
    """Toggle the data streaming on/off when clicking the button."""
    dict_global["streaming"] = not dict_global["streaming"]
    dict_global["gui_elements"]["button_switch_streaming"].config(
        text="Start Streaming" if not dict_global["streaming"] else "Stop Streaming"
    )

    if dict_global["streaming"]:
        start_data_streaming(dict_global)
