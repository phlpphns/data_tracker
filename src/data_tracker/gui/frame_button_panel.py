# blitting - https://stackoverflow.com/questions/57891219/how-to-make-a-fast-matplotlib-live-plot-in-a-pyqt5-gui
# https://www.pythonguis.com/tutorials/plotting-pyqtgraph/

from ..gui.functions_buttons import *
from ..in_and_output.read_write_text_files import load_json, write_json_file
from ..in_and_output.upon_startup import read_file_for_first_time
from ..plotting.set_lines_in_plot import set_axis_on_auto_zoom_respecting_user_limits

import tkinter as tk
from tkinter import ttk


def configure_button_panel(frame_holding_buttons, dict_global):
    for i in range(7):  # Adjust range based on max columns used
        frame_holding_buttons.columnconfigure(i, weight=0)  # Keep buttons compact
    # frame_holding_buttons.columnconfigure(2, weight=1, uniform="group2")  # Allow file paths to expand

    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========
    if True:
        # dat_file Filepath Entry
        ttk.Label(frame_holding_buttons, text="File:").grid(
            row=0, column=1, padx=5, pady=5, sticky="w"
        )
        # ======= # ========== # =========== # =========== # ===========
        # Use StringVar for dynamic updates
        dat_filepath_var = tk.StringVar(value=dict_global["dat_file"])
        
        file_path_input_entry_dat_filepath = ttk.Entry(frame_holding_buttons, width=50, textvariable=dat_filepath_var)
        # file_path_input_entry_dat_filepath.insert(0, dict_global["dat_file"])
        file_path_input_entry_dat_filepath.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        def update_dat_filepath(event=None):
            """Update dict_global when the user enters a new file path."""
            new_path = dat_filepath_var.get().strip().strip('"')
            if new_path:
                dict_global["dat_file"] = new_path
                print(f"Updated file path: {dict_global['dat_file']}")

        file_path_input_entry_dat_filepath.bind("<Return>", update_dat_filepath)
        dict_global["gui_elements"][
            "text_input_entry_dat_filepath"
        ] = file_path_input_entry_dat_filepath


    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========
    if True:
        # Update Filepath Button
        update_filepath_button = ttk.Button(
            frame_holding_buttons,
            text="autosearch file",
            command=lambda: button_function_autosearch_file(dict_global),
        )
        update_filepath_button.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        dict_global["gui_elements"]["update_filepath_button"] = update_filepath_button

    # ======= # ========== # =========== # =========== # ===========
    # Start/Stop Button
    if True:
        read_file_for_first_time_button = ttk.Button(
            frame_holding_buttons,
            text="Read a fresh file",
            command=lambda: read_file_for_first_time(dict_global),
        )  # partial(bread_file_for_first_time, dict_global))
        read_file_for_first_time_button.grid(row=0, column=4, padx=5, pady=5, sticky="w")
        dict_global["gui_elements"][
            "read_file_for_first_time_button"
        ] = read_file_for_first_time_button

        # ======= # ========== # =========== # =========== # ===========
        # Start/Stop Streaming Button
        button_switch_streaming = ttk.Button(
            frame_holding_buttons,
            text=f"Streaming: {dict_global['streaming']}",
            command=lambda: button_function_toggle_csv_stream(dict_global),
        )
        button_switch_streaming.grid(row=0, column=5, padx=5, pady=5, sticky="w")
        dict_global["gui_elements"]["button_switch_streaming"] = button_switch_streaming

    # ======= # ========== # =========== # =========== # ===========
    # Auto Zoom Button
    if True:
        auto_zoom_button = ttk.Button(
            frame_holding_buttons,
            text=f"Auto Zoom: {dict_global['auto_zoom']}",
            command=lambda: button_function_reset_auto_zoom(dict_global),
        )
        auto_zoom_button.grid(row=0, column=6, padx=5, pady=5, sticky="w")
        dict_global["gui_elements"]["auto_zoom_button"] = auto_zoom_button

    # ======= # ========== # =========== # =========== # ===========
    # Exit Button
    if True:
        exit_button = ttk.Button(
            frame_holding_buttons,
            text="Exit",
            command=lambda: button_function_exit_app(dict_global),
        )
        exit_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        dict_global["gui_elements"]["exit_button"] = exit_button


    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========
    if True:
        # JSON Filepath Entry
        ttk.Label(frame_holding_buttons, text="File:").grid(
            row=1, column=1, padx=5, pady=5, sticky="w"
        )
        # Use StringVar for dynamic updates
        json_filepath_var = tk.StringVar(value=dict_global["json_filepath"])

        file_path_input_entry_json_filepath = ttk.Entry(
            frame_holding_buttons, width=50, textvariable=json_filepath_var
        )
        file_path_input_entry_json_filepath.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        def update_json_filepath(event=None):
            """Update dict_global when the user enters a new file path."""
            new_path = json_filepath_var.get().strip().strip('"')
            if new_path:
                dict_global["json_filepath"] = new_path
                print(f"Updated file path: {dict_global['json_filepath']}")
                # open_json(new_path)

        # Bind "Enter" key to update the file path
        file_path_input_entry_json_filepath.bind("<Return>", update_json_filepath)
        dict_global["gui_elements"][
            "file_path_input_entry_json_filepath"
        ] = file_path_input_entry_json_filepath

    # ======= # ========== # =========== # =========== # ===========
    # Load JSON Button
    if True:
        load_json_button = ttk.Button(
            frame_holding_buttons,
            text="Load user settings",
            command=lambda: button_function_load_user_settings(dict_global),
        )
        load_json_button.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        dict_global["gui_elements"]["load_json_button"] = load_json_button

    # ======= # ========== # =========== # =========== # ===========
    # Button to save config dict
    if True:
        save_json_button = ttk.Button(
            frame_holding_buttons,
            text="save user settings",
            command=lambda: button_function_save_user_settings(dict_global),
        )
        save_json_button.grid(row=1, column=4, padx=5, pady=5, sticky="w")
        dict_global["gui_elements"]["save_json_button"] = save_json_button

    # ======= # ========== # =========== # =========== # ===========
    # Save as PNG Button
    if True:
        save_png_button = ttk.Button(
            frame_holding_buttons,
            text="Save as PNG",
            command=lambda: button_function_save_plot_as_png(dict_global),
        )
        save_png_button.grid(row=1, column=5, padx=5, pady=5)
        dict_global["gui_elements"]["save_png_button"] = save_png_button
