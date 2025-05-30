# TODOS:
# eliminate global variables; adapt file opening procedures?
# reloading of files needs to be improved
# automatical searching and loading of files
# update get_new_data
# we need to handle different
# we could enforce that dictionary keys must be present!
# check streaming button
# done - implement strategy + facade patterns for file loading
# done - we could store each button in a function and store it in the dict.
# contains keys; using keys:
# done - dict_global['gui_elements'] = ''
# done - concurrent mode so gui becomes less laggy
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
# bring config file to yaml
#
# watchdog, observer for data processing pipelines
# multifile options?
#
# done - pyproject.toml
# started - splitting in more modules
#

import asyncio

import json

import numpy as np
import os
import pandas as pd
import sys

import time

import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# from gui.buttons import button_function_autosearch_file
# from buttons import *
# from .. import buttons
# from functools import partial
from editors.text_editors import *  # json_editor_functions, text_editor_functions
from in_and_output.redirecting import RedirectText


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


def read_fresh_file(dict_global):
    dict_global["ax"].clear()
    print(type(dict_global["pandas_main_dataframe_read_data"]))
    read_file_for_first_time(dict_global)
    # print(2234234324324)
    fill_initial_plot(dict_global)
    dict_global["canvas"].draw()


# def data_feeder():
#         problem potentially: data format not fixed? can we press each input into a scheme? columns, arrays ... ?
#         refresh_feature_checkboxes
#         convert_time_stamp

#         pass


def read_file_for_first_time(dict_global):
    try:
        dat_file = dict_global["dat_file"]

        dict_global["pandas_main_dataframe_read_data"] = pd.DataFrame()  # None
        column_names = (
            dict_global["data_reader"]
            .read(
                file_path=dict_global["dat_file"],
                file_type=dict_global[
                    "file_type"
                ],  # detect_file_type(path_=dict_global["dat_file"]),
                # file_type="csv",
                delimiter="\t",
                header=1,
                index_col=False,
                nrows=1,
            )
            .columns
        )

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
        if (
            dict_global.get("keys_of_interest") == None
            or len(dict_global.get("keys_of_interest")) == 0
        ):
            dict_global["keys_of_interest"] = dict_global["column_names"]
        print("selected keys:  ", dict_global["keys_of_interest"])
        print("\n")

        # print('NOW HERE')

        # print(type(dict_global["pandas_main_dataframe_read_data"]))
        rows = dict_global["function_get_new_data"]()
        # print(rows)
        # print('NOW HERE')

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
        refresh_feature_checkboxes(dict_global)
    except Exception as e:
        print("error   ", e)


# def _fill_initial_plot(dict_global):
#     fig = dict_global["fig"]
#     ax = dict_global["ax"]

#     try:
#         dict_global["lines_in_plot"] = {}
#         pandas_main_dataframe_read_data = dict_global["pandas_main_dataframe_read_data"]

#         # Plot initial data using the helper function
#         for key in dict_global["keys_of_interest"]:
#             add_plot_line_to_figure(dict_global, key, pandas_main_dataframe_read_data)

#     except Exception as e:
#         print("Error: ", e)


from conversions.time_conversions import convert_time_stamp

# def convert_time_stamp(pandas_main_dataframe_read_data, time_reference=None):
#     pandas_main_dataframe_read_data["time"] = pd.to_datetime(
#         pandas_main_dataframe_read_data["time"], format="%a %b %d %H:%M:%S %Y"
#     )
#     if not time_reference:
#         time_reference = pandas_main_dataframe_read_data["time"][0]
#     pandas_main_dataframe_read_data["time"] -= time_reference
#     pandas_main_dataframe_read_data["time"] = pandas_main_dataframe_read_data[
#         "time"
#     ].dt.total_seconds()
#     pandas_main_dataframe_read_data["time"] /= 3600
#     return time_reference


# def button_function_autosearch_file(dict_global):
#     find_newest_file_with_restraints(dict_global)
#     dict_global["gui_elements"]["text_input_entry_dat_filepath"].insert(
#         0, dict_global["dat_file"]
#     )


# def find_newest_file_with_restraints(dict_global):
#     """
#     get list of files in the tree starting from a reference root
#     that correspond to a patten
#     get the newest file, and updata dict_global accordingly
#     """
#     file_ending = dict_global["pattern_auto_file_search"]
#     found_files = find_files(
#         source_dir=dict_global["root_dir_data_files"],
#         starts_with="",
#         contains="",
#         file_ending=file_ending,
#     )
#     dict_global["dat_file"] = get_newest_file_from_list(found_files)
#     # dict_global["dat_file"] = file
#     print(f"\nfound file {dict_global['dat_file']}")


# def find_files(source_dir, starts_with="", contains="", file_ending=""):
#     found_files = [
#         os.path.join(d, x)
#         for d, dirs, files in os.walk(source_dir)
#         for x in files
#         # if x.endswith(file_ending)
#         if x.startswith(starts_with) and x.endswith(file_ending)
#     ]
#     return found_files


# def get_newest_file_from_list(file_list):
#     """Returns the newest file from a list based on modification date."""
#     if not file_list:
#         return None  # Return None if the list is empty

#     return max(file_list, key=os.path.getmtime)


# def button_function_load_user_settings(dict_global):
#     try:
#         json_filepath = dict_global["json_filepath"]
#         dict_user_settings = load_json(json_filepath)
#         # dict_user_settings = {}
#         dict_global = {**dict_global, **dict_user_settings}
#         print("\n\n")
#         print(f"Loaded JSON user settings from disk: ")
#         print(json.dumps(dict_user_settings, indent=4, separators=(",", ": ")))

#     except Exception as e:
#         print("error in load_user_settings")
#         print(e)


# def button_function_save_user_settings(dict_global):
#     try:
#         dict_user_settings = {
#             key: dict_global[key] for key in dict_global["dict_user_settings_keys"]
#         }
#         # print(dict_user_settings)
#         # print("IMPLEMENT JSON SAVER")
#         write_json_file(dict_user_settings, dict_global["json_filepath"])
#         print("\n\n")
#         # print("IMPLEMENT PRETTY PRINT!!!")
#         print(f"Wrote JSON user settings to disk: ")
#         print(json.dumps(dict_user_settings, indent=4, separators=(",", ": ")))
#     except Exception as e:
#         print("error in save_user_settings")
#         print(e)


from plotting.set_lines_in_plot import *

def detect_file_type(path_):
    if not dict_global["file_type", "csv"]:
        file_type = os.path.splitext(path_)[-1]
    print(f"the detected file type is: {file_type}")
    return file_type


def refresh_feature_checkboxes(dict_global):
    """Refreshes the list of checkboxes for feature selection dynamically."""
    frame = dict_global["checkbox_frame"]

    # Ensure column_names exists
    if "column_names" not in dict_global or dict_global["column_names"] is None:
        dict_global["column_names"] = []  # Initialize as empty list
    if "keys_of_interest" not in dict_global or dict_global["keys_of_interest"] is None:
        dict_global["keys_of_interest"] = []  # Initialize as empty list

    # Clear existing checkboxes to prevent duplication
    for widget in frame.winfo_children():
        widget.destroy()

    # Synchronize keys with available columns
    sync_keys_with_columns(dict_global)

    # Store variables to track checkbox states
    dict_global["checkbox_vars"] = {}

    for feature in dict_global["column_names"]:
        var = tk.BooleanVar(value=(feature in dict_global["keys_of_interest"]))
        checkbox = tk.Checkbutton(
            frame,
            text=feature,
            variable=var,
            command=lambda f=feature, v=var: toggle_feature(f, v, dict_global),
        )
        checkbox.pack(anchor="w")

        dict_global["checkbox_vars"][feature] = var


def update_plot_manual(dict_global):
    """Manually updates the plot when streaming is disabled."""
    try:
        for key in dict_global["keys_of_interest"]:
            line = dict_global["lines_in_plot"].get(key)
            if line:
                line[0].set_xdata(
                    dict_global["pandas_main_dataframe_read_data"]["time"]
                )
                line[0].set_ydata(dict_global["pandas_main_dataframe_read_data"][key])

        if dict_global["auto_zoom"]:
            set_axis_on_auto_zoom_respecting_user_limits(dict_global)

        dict_global["canvas"].draw()
    except Exception as e:
        print(f"Error in update_plot_manual: {e}")


def toggle_feature(feature, var, dict_global):
    """Handles selection/deselection of features dynamically."""
    if var.get():
        if feature not in dict_global["keys_of_interest"]:
            dict_global["keys_of_interest"].append(feature)
            # add_new_tab_for_plot(feature, dict_global)
            # is_checked =True
    else:
        if feature in dict_global["keys_of_interest"]:
            dict_global["keys_of_interest"].remove(feature)
            # remove_tab_for_plot(feature, dict_global)
            # is_checked = False
    # update_plot_on_checkbox_change(feature, is_checked, dict_global)
    # update_plot_on_checkbox_change(dict_global)

    # refresh_feature_checkboxes(dict_global)
    # If streaming is OFF, update plot manually
    if not dict_global.get("streaming", False):
        update_plot_manual(dict_global)






# def toggle_feature(feature, var, dict_global):
#     """Handles selection/deselection of features dynamically."""
#     if var.get():
#         if feature not in dict_global["keys_of_interest"]:
#             dict_global["keys_of_interest"].append(feature)
#     else:
#         if feature in dict_global["keys_of_interest"]:
#             dict_global["keys_of_interest"].remove(feature)

#     # Replot immediately if necessary
#     if dict_global.get("force_replot", True):
#         dict_global["update_plot_async"](dict_global)

def sync_keys_with_columns(dict_global):
    """Ensure keys_of_interest contains only valid column names."""
    valid_keys = set(dict_global["column_names"])
    dict_global["keys_of_interest"] = [
        key for key in dict_global["keys_of_interest"] if key in valid_keys
    ]

def update_lines_by_checked_boxes():
    pass

def change_lines_in_plot(dict_global):
    pass
def remove_curve_from_plot(key, dict_global):
    """Remove a curve from the plot based on the selected feature key."""
    line = dict_global["lines_in_plot"].get(key)
    if line:
        line[0].remove()  # Remove the line from the plot
        dict_global["lines_in_plot"].pop(key, None)  # Remove it from the dictionary

    # Redraw the plot after removal
    # dict_global['ax'].legend()
    # dict_global["canvas"].draw()



async def update_plot_async(dict_global):
    """Asynchronous function to update the plot periodically while streaming."""
    while dict_global["streaming"]:
        try:
            # print(1232234234234)
            # print(type(dict_global['pandas_main_dataframe_read_data']))
            rows = dict_global["function_get_new_data"]()
            # print(rows)
            df = await asyncio.to_thread(
                dict_global["data_reader"].read,
                file_path=dict_global["dat_file"],
                file_type=dict_global["file_type"],
                delimiter="\t",
                header=2,
                index_col=False,
                **rows,
            )

            # Synchronize feature selection if needed
            # sync_keys_with_columns(dict_global)

            # # Refresh UI but not every loop to prevent flickering
            # refresh_counter = dict_global.get("refresh_counter", 0)
            # if refresh_counter < 1:  # Adjust rate
            #     refresh_feature_checkboxes(dict_global)
            # dict_global["refresh_counter"] = refresh_counter + 1
            # # dict_global["refresh_counter"] += 1

            if len(df) > 0:
                df.columns = dict_global["column_names"]
                await asyncio.to_thread(
                    convert_time_stamp, df, time_reference=dict_global["time_reference"]
                )

                dict_global["pandas_main_dataframe_read_data"] = pd.concat(
                    [dict_global["pandas_main_dataframe_read_data"], df]
                ).drop_duplicates()

                for key in dict_global["keys_of_interest"]:
                    line = dict_global["lines_in_plot"].get(key)
                    if line:
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
            pass

        # await asyncio.sleep(1)


# async def _update_plot_async(dict_global):
#     """Asynchronous function to update the plot periodically while streaming."""
#     while dict_global["streaming"]:
#         try:
#             rows = dict_global["function_get_new_data"]()
#             df = await asyncio.to_thread(
#                 # dict_global["data_reader"],
#                 dict_global["data_reader"].read,
#                 file_path=dict_global["dat_file"],
#                 # file_type=detect_file_type(path_=dict_global["dat_file"]),
#                 # file_type="csv",
#                 file_type=dict_global["file_type"],
#                 # delimiter=","
#                 delimiter="\t",
#                 header=2,
#                 index_col=False,
#                 **rows,
#             )
#             refresh_feature_checkboxes(dict_global)

#             if len(df) > 0:
#                 df.columns = dict_global["column_names"]
#                 await asyncio.to_thread(
#                     convert_time_stamp, df, time_reference=dict_global["time_reference"]
#                 )

#                 dict_global["pandas_main_dataframe_read_data"] = pd.concat(
#                     [dict_global["pandas_main_dataframe_read_data"], df]
#                 ).drop_duplicates()

#                 for key in dict_global["keys_of_interest"]:
#                     line = dict_global["lines_in_plot"][key]
#                     line[0].set_xdata(
#                         dict_global["pandas_main_dataframe_read_data"]["time"]
#                     )
#                     line[0].set_ydata(
#                         dict_global["pandas_main_dataframe_read_data"][key]
#                     )

#                 if dict_global["auto_zoom"]:
#                     await asyncio.to_thread(
#                         set_axis_on_auto_zoom_respecting_user_limits, dict_global
#                     )

#             dict_global["canvas"].draw()

#         except Exception as e:
#             print(f"Error in update_plot_async: {e}")

#         # await asyncio.sleep(1)


# def add_new_tab_for_plot(tab_widget, plot_name):
#     """Add a new tab for the selected plot."""
#     tab_frame = ttk.Frame(tab_widget)
#     tab_widget.add(tab_frame, text=plot_name)  # Add tab
#     # Add plotting elements or canvas to this tab
#     plot_canvas = FigureCanvasTkAgg(figure, master=tab_frame)
#     plot_canvas.get_tk_widget().pack()


def add_new_tab_for_plot(feature, dict_global):
    # Create a new tab for the selected feature
    new_tab = tk.Frame(dict_global["tab_widget"])  # Assuming you have a tab widget
    # Create the plot for the new tab
    fig = plt.Figure(figsize=(5, 5))
    ax = fig.add_subplot(111)
    ax.plot(
        dict_global["pandas_main_dataframe_read_data"]["time"],
        dict_global["pandas_main_dataframe_read_data"][feature],
    )

    canvas = FigureCanvasTkAgg(fig, master=new_tab)
    canvas.get_tk_widget().pack()

    # Add the new tab to the tab widget (assuming you have a Tk notebook or similar widget)
    dict_global["tab_widget"].add(new_tab, text=feature)




def update_plot_on_checkbox_change(dict_global):
    """Update the plot when a checkbox is changed (added/removed)."""
    for key in dict_global["keys_of_interest"]:
        if key not in dict_global["lines_in_plot"]:
            # Add the new plot line
            dict_global["lines_in_plot"][key] = add_plot_line_to_figure(
                dict_global, key, dict_global["pandas_main_dataframe_read_data"]
            )
        else:
            # Remove the plot line
            remove_curve_from_plot(key, dict_global)

    dict_global["ax"].legend()
    dict_global["canvas"].draw()  # Redraw the canvas


# # In your checkbox handler:
# def _update_plot_on_checkbox_change(feature, is_checked, dict_global):
#     if is_checked:
#         dict_global["keys_of_interest"].append(feature)
#         add_new_tab_for_plot(feature, dict_global)
#     else:
#         dict_global["keys_of_interest"].remove(feature)
#         remove_tab_for_plot(feature, dict_global)

#     # Redraw the plot
#     dict_global["canvas"].draw()


def remove_tab_for_plot(feature, dict_global):
    for tab in dict_global["tab_widget"].tabs():
        if feature in tab.winfo_name():  # Or match based on some criteria
            dict_global["tab_widget"].forget(tab)


# def _update_plot_on_checkbox_change(feature, is_checked, dict_global):
#     tab_widget = dict_global["tab_widget"]

#     if is_checked:
#         # Add new tab for the feature
#         add_plot_to_tab(feature, dict_global)
#     else:
#         # Remove tab for the feature
#         for tab in tab_widget.tabs():
#             if feature in tab:  # Or use a custom identifier for the tab
#                 tab_widget.forget(tab)

#     # Redraw the plot
#     dict_global["canvas"].draw()


# checkbox = tk.Checkbutton(dict_global["checkbox_frame"], text="Feature 1", command=lambda: update_plot_on_checkbox_change("Feature 1", checkbox.var.get(), dict_global))
# checkbox.grid(row=0, column=0, sticky="w")



def start_data_streaming(dict_global):
    """Ensures the asyncio loop is running and starts the data streaming task."""
    start_asyncio_loop(dict_global)  # Ensure event loop is running
    async_loop = dict_global["threading"]["async_loop"]
    asyncio.run_coroutine_threadsafe(update_plot_async(dict_global), async_loop)


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
