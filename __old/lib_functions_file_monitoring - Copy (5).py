# TODOS:
# eliminate global variables; adapt file opening procedures?
# reloading of files needs to be improved
# automatical searching and loading of files
# update get_new_data
# we need to handle different
# we could enforce that dictionary keys must be present!
# check streaming button
# implement strategy pattern
# we could store each button in a function and store it in the dict.
# contains keys; using keys:
# dict_global['gui_elements'] = ''
# concurrent mode so gui becomes less laggy
#
# replace printing by logging?
# no concatenate if new df is empty. -> better: check file stamps and file not read if
#
# option to open multiple file types, command line multiple json files, maybe even monitoring multiple files... :-oooooooo
#
# the normalizer from "DataReaderStrategy" works but is not helpful
# get one function
#
# to make it more robust, we need to somehow automatically check headers and rest
#
#
#

import asyncio

import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import numpy as np
import os
import pandas as pd
import sys

import time

import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# from functools import partial


def define_dict_user_settings_jeol():
    dict_user_settings = {}
    dict_user_settings["keys_of_interest"] = [
        # "Unnamed",
        # "time",
        "HT [kV]",
        "Beam Current [uA]",
        "Filament Current [A]",
        "Penning PeG1",
        "Column PiG1",
        "Gun PiG2",
        "Detector PiG3",
        "Specimen PiG4",
        "RT1 PiG5",
    ]
    dict_user_settings["name_png"] = "figures/test.png"
    dict_user_settings["streaming"] = True  # Controls the animation loop
    dict_user_settings[
        "json_filepath"
    ] = "./config_files/instructions_json.json"  # Default filepath
    # dict_user_settings["json_filepath"] = r"C:\Users\pkbv190\Dropbox\CODES\playground\arianna_monitoring_file\instructions_json - Copy.json"
    # Global Dictionary for Settings
    dict_user_settings["refresh_rate_in_ms"] = 50
    dict_user_settings["user_defined_max_x_threshold"] = 100 / 3600
    dict_user_settings["user_defined_max_y_threshold"] = 200
    dict_user_settings["auto_zoom"] = True
    dict_user_settings["root_dir_data_files"] = "."
    dict_user_settings["pattern_auto_file_search"] = "EDAutoLog.dat"
    dict_user_settings["auto_file_search_on_startup"] = True
    dict_user_settings["auto_run_on_startup"] = True
    dict_user_settings["leading_delimiter"] = True
    dict_user_settings["file_type"] = "csv"

    # read user settings from a json file (try!)
    # dict_user_settings[
    #     "dat_file"
    # ] = r"C:\Users\pkv190\Dropbox\CODES\playground\arianna_monitoring_file\Fri-Mar-07-21-31-13-2025_EDAutoLog\EDAutoLog.dat"

    dict_user_settings["dat_file"] = r"./test.dat"

    return dict_user_settings


class RedirectText:
    """Class to redirect print output to a Tkinter Text widget."""

    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)  # Auto-scroll

    def flush(self):
        pass  # Required for compatibility with sys.stdout


class text_editor_functions:
    def open_text_file(text_editor):
        """Open a text file and display it in the editor."""
        global current_file
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                text_data = file.read()  # Read entire file as plain text
                # print(text_data)
                # print(
                #     f"File content: {repr(text_data)}"
                # )  # Debug: Check if content is loaded

            print(
                f"Before insert: text_editor.winfo_exists() = {text_editor.winfo_exists()}"
            )
            text_editor.delete("1.0", tk.END)  # Clear previous content
            text_editor.insert(tk.END, text_data)  # Insert new content
            print("Text inserted successfully.")  # Debug message

            current_file = file_path
            print(f"Loaded text file: {file_path}")

        except OSError as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def save_text_file(text_editor):
        """Save the edited text data back to file."""
        global current_file
        if not current_file:
            messagebox.showwarning("Warning", "No file loaded. Use 'Open' first.")
            return

        try:
            text_data = text_editor.get("1.0", tk.END).strip()

            with open(current_file, "w", encoding="utf-8") as file:
                file.write(text_data)  # Write text back to file

            print(f"Saved text file: {current_file}")
            messagebox.showinfo("Success", "File saved successfully!")

        except OSError as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def reload_text_file(text_editor):
        """Reload the last opened text file."""
        if not current_file:
            messagebox.showwarning("Warning", "No file to reload.")
            return

        print(f"Reloading file: {current_file}")
        open_text_file()  # Reuse open_text_file function

    # ======== # ======= # =======


class json_editor_functions:
    def open_json(json_text_editor):
        """Open a JSON file and display it in the editor."""
        global current_file
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            json_data = load_json(file_path)
            # with open(file_path, "r", encoding="utf-8") as file:
            #     json_data = json.load(file)
            #     # print(json_data)

            # Pretty-print JSON into editor
            json_text_editor.delete("1.0", tk.END)
            json_text_editor.insert(tk.END, json.dumps(json_data, indent=4))

            current_file = file_path
            print(f"Loaded JSON file: {file_path}")

        except (json.JSONDecodeError, OSError) as e:
            messagebox.showerror("Error", f"Failed to open JSON file:\n{e}")

    def save_json(json_text_editor):
        """Save the edited JSON data back to file."""
        global current_file
        if not current_file:
            messagebox.showwarning("Warning", "No file loaded. Use 'Open JSON' first.")
            return

        try:
            json_text = json_text_editor.get("1.0", tk.END).strip()
            json_data = json.loads(json_text)  # Validate JSON

            write_json_file(json_data, current_file)

            # with open(current_file, "w", encoding="utf-8") as file:
            #    json.dump(json_data, file, indent=4)

            print(f"Saved JSON file: {current_file}")
            messagebox.showinfo("Success", "File saved successfully!")

        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Invalid JSON format:\n{e}")

    def reload_json(json_text_editor):
        """Reload the last opened JSON file."""
        global current_file
        if not current_file:
            messagebox.showwarning("Warning", "No file to reload.")
            return

        print(f"Reloading file: {current_file}")
        editor_functions.open_json(json_text_editor)  # Reuse open_json function


def gen_yield_line_numbers():
    value_to_add = 1000
    i = -1
    while True:
        # for i in range(30):
        i += 1
        yield {"skiprows": i * value_to_add, "nrows": value_to_add}


def create_data_generator():
    state = {"gen": gen_yield_line_numbers(), "last_value": None}

    def get_new_data():
        try:
            state["last_value"] = next(state["gen"])
            # print(state["last_value"])
            return state["last_value"]
        except StopIteration:
            return state["last_value"]  # Return last valid value when exhausted

    return get_new_data


# get_new_data = create_data_generator(dict_global)

# gen_yield_line = gen_yield_line_numbers()

# def get_new_data():
#     return next(gen_yield_line)


def read_fresh_file(dict_global):
    dict_global["ax"].clear()
    dict_global["pandas_main_dataframe_read_data"] = None
    read_file_for_first_time(dict_global)
    fill_initial_plot(dict_global)
    dict_global["canvas"].draw()


def read_file_for_first_time(dict_global):
    try:
        dat_file = dict_global["dat_file"]

        # pandas_main_dataframe_read_data = pd.read_csv(
        #     dat_file,
        #     delimiter="\t",
        #     header=1,
        #     index_col=False,
        #     nrows=1,
        # )
        # df = await asyncio.to_thread(
        # dict_global["data_reader"],
        column_names = (
            dict_global["data_reader"]
            .read(
                file_path=dict_global["dat_file"],
                file_type=dict_global[
                    "file_type"
                ],  # detect_file_type(path_=dict_global["dat_file"]),
                # file_type="csv",
                # delimiter=","
                delimiter="\t",
                header=1,
                index_col=False,
                nrows=1,
            )
            .columns
        )
        # list_column_names = (
        # column_names = (
        #     pandas_main_dataframe_read_data.columns
        # )  # pandas_main_dataframe_read_data[:10][0]

        leading_delimiter = dict_global["leading_delimiter"]
        if leading_delimiter:
            starting_index = 1
        else:
            starting_index = 0

        column_names = column_names[starting_index:].tolist()
        dict_global["column_names"] = column_names
        print("We are here.")
        print(dict_global["column_names"], len(column_names))
        print("\n")
        print("selected keys:  ", dict_global["keys_of_interest"])
        print("\n")

        rows = dict_global["function_get_new_data"]()

        pandas_main_dataframe_read_data = dict_global["data_reader"].read(
            file_path=dict_global["dat_file"],
            file_type=dict_global["file_type"],
            delimiter="\t",
            header=2,
            index_col=False,
            # skiprows=a,
            # nrows=b - a,
            **rows,
        )
        # list_column_names = column_names = read_file.columns  # pandas_main_dataframe_read_data[:10][0]
        pandas_main_dataframe_read_data.columns = (
            column_names  # [:-1]  # Set new column names
        )
        # pandas_main_dataframe_read_data.reset_index(drop=True, inplace=True)  # Reset index
        # print(pandas_main_dataframe_read_data.columns)
        # print(pandas_main_dataframe_read_datapandas_main_dataframe_read_data)
        dict_global["pandas_main_dataframe_read_data"] = pandas_main_dataframe_read_data

        dict_global["time_reference"] = convert_time_stamp(
            pandas_main_dataframe_read_data, time_reference=None
        )
    except Exception as e:
        print("error   ", e)


def fill_initial_plot(dict_global):
    fig = dict_global["fig"]
    ax = dict_global["ax"]

    try:
        dict_global["lines_in_plot"] = {}
        pandas_main_dataframe_read_data = dict_global["pandas_main_dataframe_read_data"]
        # Plot initial data
        for index_key, key in enumerate(dict_global["keys_of_interest"]):
            column = pandas_main_dataframe_read_data[key]
            dict_global["lines_in_plot"][key] = ax.plot(
                pandas_main_dataframe_read_data["time"],
                pandas_main_dataframe_read_data[key],
                label=key,
            )
        ax.legend()
    except Exception as e:
        print("error   ", e)

    # ax.set_xlabel("Time (s)")
    # ax.set_ylabel("Values")


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


def convert_time_stamp(pandas_main_dataframe_read_data, time_reference=None):
    pandas_main_dataframe_read_data["time"] = pd.to_datetime(
        pandas_main_dataframe_read_data["time"], format="%a %b %d %H:%M:%S %Y"
    )
    if not time_reference:
        time_reference = pandas_main_dataframe_read_data["time"][0]
    pandas_main_dataframe_read_data["time"] -= time_reference
    pandas_main_dataframe_read_data["time"] = pandas_main_dataframe_read_data[
        "time"
    ].dt.total_seconds()
    pandas_main_dataframe_read_data["time"] /= 3600
    return time_reference


def button_function_autosearch_file(dict_global):
    find_newest_file_with_restraints(dict_global)
    dict_global["gui_elements"]["text_input_entry_dat_filepath"].insert(
        0, dict_global["dat_file"]
    )


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
        print(e)


def get_async_loop(dict_global):
    """Ensure that the global asyncio loop exists and is initialized properly."""
    if "threading" not in dict_global:
        dict_global["threading"] = {}

    if "loop_running" not in dict_global:
        dict_global["threading"]["loop_running"] = False

    if not isinstance(
        dict_global["threading"].get("async_loop"), asyncio.AbstractEventLoop
    ):
        dict_global["threading"]["async_loop"] = asyncio.new_event_loop()

    return dict_global["threading"]["async_loop"]


def start_asyncio_loop(dict_global):
    """Start the asyncio event loop in a separate thread if not already running."""
    if dict_global["threading"]["loop_running"]:
        return  # Prevent duplicate loops

    async_loop = get_async_loop(dict_global)
    dict_global["threading"]["loop_running"] = True  # Mark loop as running

    def run_loop():
        try:
            asyncio.set_event_loop(async_loop)
            async_loop.run_forever()
        except Exception as e:
            print(f"Asyncio Loop Error: {e}")
        finally:
            dict_global["threading"]["loop_running"] = False  # Mark loop as stopped

    threading.Thread(target=run_loop, daemon=True).start()


def detect_file_type(path_):
    if not dict_global["file_type", "csv"]:
        file_type = os.path.splitext(path_)[-1]
    print(f"the detected file type is: {file_type}")
    return file_type


async def update_plot_async(dict_global):
    """Asynchronous function to update the plot periodically while streaming."""
    while dict_global["streaming"]:
        try:
            rows = dict_global["function_get_new_data"]()
            df = await asyncio.to_thread(
                # dict_global["data_reader"],
                dict_global["data_reader"].read,
                file_path=dict_global["dat_file"],
                # file_type=detect_file_type(path_=dict_global["dat_file"]),
                # file_type="csv",
                file_type=dict_global["file_type"],
                # delimiter=","
                delimiter="\t",
                header=2,
                index_col=False,
                **rows,
            )

            if len(df) > 0:
                df.columns = dict_global["column_names"]
                await asyncio.to_thread(
                    convert_time_stamp, df, time_reference=dict_global["time_reference"]
                )

                dict_global["pandas_main_dataframe_read_data"] = pd.concat(
                    [dict_global["pandas_main_dataframe_read_data"], df]
                ).drop_duplicates()

                for key in dict_global["keys_of_interest"]:
                    line = dict_global["lines_in_plot"][key]
                    line[0].set_xdata(
                        dict_global["pandas_main_dataframe_read_data"]["time"]
                    )
                    line[0].set_ydata(
                        dict_global["pandas_main_dataframe_read_data"][key]
                    )

                if dict_global["auto_zoom"]:
                    await asyncio.to_thread(
                        set_axis_on_auto_zoom_respecting_user_limits, dict_global
                    )

            dict_global["canvas"].draw()
        except Exception as e:
            print(f"Error in update_plot_async: {e}")

        await asyncio.sleep(1)


def start_data_streaming(dict_global):
    """Ensures the asyncio loop is running and starts the data streaming task."""
    start_asyncio_loop(dict_global)  # Ensure event loop is running
    async_loop = dict_global["threading"]["async_loop"]
    asyncio.run_coroutine_threadsafe(update_plot_async(dict_global), async_loop)


def button_function_toggle_csv_stream(dict_global):
    """Toggle the data streaming on/off when clicking the button."""
    dict_global["streaming"] = not dict_global["streaming"]
    dict_global["gui_elements"]["button_switch_streaming"].config(
        text="Start Streaming" if not dict_global["streaming"] else "Stop Streaming"
    )

    if dict_global["streaming"]:
        start_data_streaming(dict_global)


def set_axis_on_auto_zoom_respecting_user_limits(dict_global):
    pandas_main_dataframe_read_data = dict_global["pandas_main_dataframe_read_data"]

    dict_global["ax"].set_xlim(
        [
            0,
            max(
                dict_global["user_defined_max_x_threshold"],
                np.max(pandas_main_dataframe_read_data["time"]) * 1.1,
            ),
        ]
    )
    dict_global["ax"].set_ylim(
        [
            0,
            max(
                dict_global["user_defined_max_y_threshold"],
                np.max(pandas_main_dataframe_read_data[dict_global["keys_of_interest"]])
                * 1.1,
            ),
        ]
    )


def button_function_exit_app(dict_global):
    print("Exiting application")
    dict_global["root"].quit()
    sys.exit()


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


def button_function_save_plot_as_png(dict_global):
    timestr = time.strftime("%Y%m%d_%H%M%S")
    png_name = dict_global["name_png"]
    a, b = os.path.splitext(png_name)
    # print(a, b)
    png_name = f"{a}_{timestr}{b}"
    dict_global["fig"].savefig(png_name, bbox_inches="tight")
    print(f"Saved file as {png_name}")


def welcome_message_gui():
    print(
        "Hallo and Welcome to the editor.\
        \nWe have a set of standard parameters that can be saved and changed by reading the respective json file.\
        \nMay the electrons be with you - have fun!!! \n\n\n"
    )
