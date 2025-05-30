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
    dict_user_settings["name_png"] = "test.png"
    dict_user_settings["streaming"] = True  # Controls the animation loop
    dict_user_settings["json_filepath"] = "./instructions_json.json"  # Default filepath
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
        yield [i * value_to_add, (i + 1) * value_to_add]


def create_data_generator():
    state = {"gen": gen_yield_line_numbers(), "last_value": None}

    def get_new_data():
        try:
            state["last_value"] = next(state["gen"])
            print(state["last_value"])
            return state["last_value"]
        except StopIteration:
            return state["last_value"]  # Return last valid value when exhausted

    return get_new_data


# get_new_data = create_data_generator(dict_global)

# gen_yield_line = gen_yield_line_numbers()

# def get_new_data():
#     return next(gen_yield_line)


def create_gui_elements(dict_global):
    def adjust_pane_ratios(event=None, dict_global=dict_global):
        """Dynamically adjust sash positions to maintain height ratios."""
        total_height = dict_global["root"].winfo_height()
        paned_window.sashpos(0, int(total_height * 0.57))  # 67% to frame_holding_figure
        paned_window.sashpos(
            1, int(total_height * 0.73)
        )  # 13% to frame_holding_buttons, 20% to frame_holding_consoles

    root = dict_global["root"]

    # Main container (grid-based)
    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, sticky="nsew")

    # Main PanedWindow (Vertical) to divide top and bottom
    paned_window = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
    paned_window.grid(row=0, column=0, sticky="nsew")

    # Top section (Figure Frame)
    frame_holding_figure = ttk.Frame(paned_window, borderwidth=2, relief="sunken")
    # frame_holding_figure.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    # paned_window.add(frame_holding_figure, weight=3)  # Plot gets more space

    frame_holding_buttons = ttk.Frame(paned_window, borderwidth=2, relief="sunken")
    frame_holding_buttons.grid(row=0, column=0, sticky="nsew")
    # paned_window.add(frame_holding_buttons)#, weight=
    # Bottom section (Two Notebooks)1)  # Bottom section takes 1/3 of the height

    frame_holding_consoles = ttk.Frame(paned_window, borderwidth=2, relief="sunken")
    frame_holding_consoles.grid(row=1, column=0, sticky="nsew")
    # paned_window.add(frame_holding_consoles, weight=0)  # Bottom section takes 1/3 of the height

    paned_window.add(frame_holding_figure)
    paned_window.add(frame_holding_buttons)
    paned_window.add(frame_holding_consoles)

    dict_global["gui_elements"]["paned_window"] = paned_window
    dict_global["gui_elements"]["frame_holding_figure"] = frame_holding_figure
    dict_global["gui_elements"]["frame_holding_buttons"] = frame_holding_buttons
    dict_global["gui_elements"]["frame_holding_consoles"] = frame_holding_consoles

    # configure_output_panel(dict_global['frame_holding_consoles'])
    # configure_button_panel(dict_global["frame_holding_buttons"])

    if False:
        # # Bind resizing event
        # root.bind("<Configure>", adjust_pane_ratios)

        selection_height = frame_holding_buttons.winfo_height()
        # selection_height = dict_global.get("frame_holding_buttons_height", 0)
        dict_global["frame_holding_buttons_height"] = selection_height
        # Bind resizing event
        root.bind("<Configure>", adjust_pane_ratios)

        # # Adjust sash position manually
        # # Adjust sash position manually
        # root.update_idletasks()  # Ensure sizes are updated before positioning
        # paned_window.sashpos(0, int(root.winfo_height() * 0.47))  # First sash at 67% height
        # paned_window.sashpos(1, int(root.winfo_height() * 0.70))  # Second sash at 80%
        # # paned_window.sashpos(2, int(root.winfo_height() * 0.80))  # Second sash at 80%

    # Make main_frame expandable
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    frame_holding_figure.grid_rowconfigure(0, weight=1)
    frame_holding_figure.grid_columnconfigure(0, weight=1)

    frame_holding_buttons.grid_rowconfigure(0, weight=1)
    frame_holding_buttons.grid_columnconfigure(0, weight=1)

    frame_holding_consoles.grid_rowconfigure(0, weight=1)
    frame_holding_consoles.grid_columnconfigure(0, weight=1)

    # frame_holding_consoles.columnconfigure(0, weight=1)
    # frame_holding_consoles.rowconfigure(0, weight=1)

    # Configure frame_holding_consoles to expand
    # # Configure resizing behavior for main_frame
    # # Configure resizing behavior for frame_holding_figure

    # # # Configure resizing behavior for frame_holding_consoles

    configure_button_panel(
        dict_global["gui_elements"]["frame_holding_buttons"], dict_global
    )
    configure_output_panel(
        dict_global["gui_elements"]["frame_holding_consoles"], dict_global
    )
    configure_figure_panel(
        dict_global["gui_elements"]["frame_holding_figure"], dict_global
    )

    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========


def configure_figure_panel(frame_holding_figure, dict_global):
    """Creates and embeds a Matplotlib figure inside the frame_holding_figure."""
    # frame_holding_figure =   # Use the left pane frame

    # Create Matplotlib Figure
    fig, ax = plt.subplots(figsize=(8, 6))
    # fig.tight_layout()

    dict_global["fig"] = fig
    dict_global["ax"] = ax
    dict_global["ax"].set_xlabel("Time [h]")
    dict_global["ax"].set_ylabel("Value")

    # Embed Matplotlib figure in Tkinter window
    canvas = FigureCanvasTkAgg(
        fig, master=frame_holding_figure
    )  # Set master to frame_holding_figure
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Add Matplotlib toolbar (Zoom, Pan, Save)
    toolbar = NavigationToolbar2Tk(
        canvas, frame_holding_figure
    )  # Set master to frame_holding_figure
    toolbar.update()
    toolbar.pack(side=tk.TOP, fill=tk.X)

    # Store references
    dict_global["canvas"] = canvas
    dict_global["toolbar"] = toolbar


def configure_button_panel(frame_holding_buttons, dict_global):
    for i in range(7):  # Adjust range based on max columns used
        frame_holding_buttons.columnconfigure(i, weight=0)  # Keep buttons compact
    # frame_holding_buttons.columnconfigure(2, weight=1, uniform="group2")  # Allow file paths to expand

    # ======= # ========== # =========== # =========== # ===========
    # dat_file Filepath Entry
    ttk.Label(frame_holding_buttons, text="File:").grid(
        row=0, column=1, padx=5, pady=5, sticky="w"
    )
    text_input_entry_dat_filepath = ttk.Entry(frame_holding_buttons, width=50)
    text_input_entry_dat_filepath.insert(0, dict_global["dat_file"])
    text_input_entry_dat_filepath.grid(row=0, column=2, padx=5, pady=5, sticky="w")
    dict_global["gui_elements"][
        "text_input_entry_dat_filepath"
    ] = text_input_entry_dat_filepath

    # ======= # ========== # =========== # =========== # ===========
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
    read_fresh_file_button = ttk.Button(
        frame_holding_buttons,
        text="Read a fresh file",
        command=lambda: read_fresh_file(dict_global),
    )  # partial(bread_fresh_file, dict_global))
    read_fresh_file_button.grid(row=0, column=4, padx=5, pady=5, sticky="w")
    dict_global["gui_elements"]["read_fresh_file_button"] = read_fresh_file_button

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
    auto_zoom_button = ttk.Button(
        frame_holding_buttons,
        text=f"Auto Zoom: {dict_global['auto_zoom']}",
        command=lambda: button_function_reset_auto_zoom(dict_global),
    )
    auto_zoom_button.grid(row=0, column=6, padx=5, pady=5, sticky="w")
    dict_global["gui_elements"]["auto_zoom_button"] = auto_zoom_button

    # ======= # ========== # =========== # =========== # ===========
    # Exit Button
    exit_button = ttk.Button(
        frame_holding_buttons,
        text="Exit",
        command=lambda: button_function_exit_app(dict_global),
    )
    exit_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    dict_global["gui_elements"]["exit_button"] = exit_button

    # ======= # ========== # =========== # =========== # ===========
    # JSON Filepath Entry
    ttk.Label(frame_holding_buttons, text="File:").grid(
        row=1, column=1, padx=5, pady=5, sticky="w"
    )

    # ======= # ========== # =========== # =========== # ===========
    # Use StringVar for dynamic updates
    json_filepath_var = tk.StringVar(value=dict_global["json_filepath"])
    text_input_entry_json_filepath = ttk.Entry(
        frame_holding_buttons, width=40, textvariable=json_filepath_var
    )

    # ======= # ========== # =========== # =========== # ===========
    # text_input_entry_json_filepath.grid(row=1, column=1, padx=5, pady=5)
    text_input_entry_json_filepath.grid(row=1, column=2, padx=5, pady=5, sticky="w")
    dict_global["gui_elements"][
        "text_input_entry_json_filepath"
    ] = text_input_entry_json_filepath

    # ======= # ========== # =========== # =========== # ===========
    # Use StringVar for dynamic updates
    json_filepath_var = tk.StringVar(value=dict_global["json_filepath"])

    text_input_entry_json_filepath = ttk.Entry(
        frame_holding_buttons, width=50, textvariable=json_filepath_var
    )
    text_input_entry_json_filepath.grid(row=1, column=2, padx=5, pady=5, sticky="w")

    def update_json_filepath(event=None):
        """Update dict_global when the user enters a new file path."""
        new_path = json_filepath_var.get().strip().strip('"')
        if new_path:
            dict_global["json_filepath"] = new_path
            print(f"Updated file path: {dict_global['json_filepath']}")
            # open_json(new_path)

    # Bind "Enter" key to update the file path
    text_input_entry_json_filepath.bind("<Return>", update_json_filepath)

    # ======= # ========== # =========== # =========== # ===========
    # Load JSON Button
    load_json_button = ttk.Button(
        frame_holding_buttons,
        text="Load user settings",
        command=lambda: button_function_load_user_settings(dict_global),
    )
    load_json_button.grid(row=1, column=3, padx=5, pady=5, sticky="w")
    dict_global["gui_elements"]["load_json_button"] = load_json_button

    # ======= # ========== # =========== # =========== # ===========
    # Button to save config dict
    save_json_button = ttk.Button(
        frame_holding_buttons,
        text="save user settings",
        command=lambda: button_function_save_user_settings(dict_global),
    )
    save_json_button.grid(row=1, column=4, padx=5, pady=5, sticky="w")
    dict_global["gui_elements"]["save_json_button"] = save_json_button

    # ======= # ========== # =========== # =========== # ===========
    # Save as PNG Button
    save_png_button = ttk.Button(
        frame_holding_buttons,
        text="Save as PNG",
        command=lambda: button_function_save_plot_as_png(dict_global),
    )
    save_png_button.grid(row=1, column=5, padx=5, pady=5)
    dict_global["gui_elements"]["save_png_button"] = save_png_button


def configure_output_panel(frame_holding_consoles, dict_global):
    # def configure_editors_panel():

    # Create PanedWindow to hold both notebooks
    # frame_holding_consoles.grid(row=1, column=0, sticky="nsew")  # Fill all available space

    bottom_paned = ttk.PanedWindow(frame_holding_consoles, orient=tk.HORIZONTAL)
    bottom_paned.grid(row=0, column=0, sticky="nsew")  # Expand fully

    # Configure bottom_paned to expand

    create_left_notebook_paned_frame = True
    # create_left_notebook_paned_frame = not create_left_notebook_paned_frame

    if create_left_notebook_paned_frame:
        # === Left Notebook Frame ===
        left_notebook_paned_frame = ttk.Frame(
            bottom_paned, borderwidth=2, relief="sunken"
        )
        bottom_paned.add(left_notebook_paned_frame, weight=1)  # Set weight for resizing

        # Ensure the left notebook frame expands

        left_notebook = ttk.Notebook(left_notebook_paned_frame)
        left_notebook.grid(row=0, column=0, sticky="nsew")  # Fill all available space

        # left_notebook_frame

        # Left Editor Tab
        left_text_editor_frame = ttk.Frame(left_notebook)
        left_notebook.add(left_text_editor_frame, text="Output Console")

        # Text editor inside left notebook
        output_console = tk.Text(left_text_editor_frame, wrap="word")
        output_console.grid(row=0, column=0, sticky="nsew")

        left_notebook_paned_frame.columnconfigure(0, weight=1)
        left_notebook_paned_frame.rowconfigure(0, weight=1)

        left_text_editor_frame.rowconfigure(0, weight=1)
        left_text_editor_frame.columnconfigure(0, weight=1)

        dict_global["redirect_error"] = output_console
        dict_global["redirect_output"] = output_console

    # ========= # ======= # =======
    # ========= # ======= # =======
    # ========= # ======= # =======
    # ========= # ======= # =======

    create_right_side_json_editor_frame = True
    # create_right_side_json_editor_frame = not create_right_side_json_editor_frame

    if create_right_side_json_editor_frame:
        # === Tab 1: JSON Editor ===

        # === Right Notebook Frame ===
        right_notebook_paned_frame = ttk.Frame(
            bottom_paned, borderwidth=2, relief="sunken"
        )
        bottom_paned.add(right_notebook_paned_frame, weight=1)

        right_notebook = ttk.Notebook(right_notebook_paned_frame)
        right_notebook.grid(row=0, column=0, sticky="nsew")  # Fill all available space

        # Right Editor Tab
        right_side_json_editor_frame = ttk.Frame(right_notebook)
        right_notebook.add(right_side_json_editor_frame, text="JSON Editor")

        # JSON Text Editor
        json_text_editor = tk.Text(
            right_side_json_editor_frame, wrap="word", font=("Courier", 10)
        )
        json_text_editor.grid(row=0, column=0, columnspan=3, sticky="ew")

        ttk.Button(
            right_side_json_editor_frame,
            text="Open JSON",
            command=lambda: json_editor_functions.open_json(json_text_editor),
        ).grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        ttk.Button(
            right_side_json_editor_frame,
            text="Save JSON",
            command=lambda: json_editor_functions.save_json(json_text_editor),
        ).grid(row=1, column=1, sticky="nsew", padx=5, pady=2)
        ttk.Button(
            right_side_json_editor_frame,
            text="Reload",
            command=lambda: json_editor_functions.reload_json(json_text_editor),
        ).grid(row=1, column=2, sticky="nsew", padx=5, pady=2)

        # === Tab 2: text Editor ===

        right_side_text_editor_frame = ttk.Frame(right_notebook)
        right_notebook.add(right_side_text_editor_frame, text="Note pad - append mode")

        # Text editor inside right notebook
        text_editor = tk.Text(
            right_side_text_editor_frame, wrap="word", font=("Courier", 10)
        )
        text_editor.grid(row=0, column=0, columnspan=3, sticky="ew")

        # Create buttons and place them inside the button_frame
        ttk.Button(
            right_side_text_editor_frame,
            text="Open text file",
            command=lambda: text_editor_functions.open_text_file(text_editor),
        ).grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        ttk.Button(
            right_side_text_editor_frame,
            text="Save text file",
            command=lambda: text_editor_functions.save_text_file(text_editor),
        ).grid(row=1, column=1, sticky="nsew", padx=5, pady=2)
        ttk.Button(
            right_side_text_editor_frame,
            text="Reload text file",
            command=lambda: text_editor_functions.reload_text_file(text_editor),
        ).grid(row=1, column=2, sticky="nsew", padx=5, pady=2)

        # Ensure the right notebook frame expands
        right_notebook_paned_frame.rowconfigure(0, weight=1)
        right_notebook_paned_frame.columnconfigure(0, weight=1)

        right_notebook.rowconfigure(0, weight=1)
        right_notebook.columnconfigure(0, weight=1)

        right_side_json_editor_frame.rowconfigure(0, weight=1)
        right_side_json_editor_frame.columnconfigure(0, weight=1)

        right_side_text_editor_frame.rowconfigure(0, weight=1)
        right_side_text_editor_frame.columnconfigure(0, weight=1)

    # ========= # ======= # =======
    # ========= # ======= # =======
    # ========= # ======= # =======
    # ========= # ======= # =======


def read_fresh_file(dict_global):
    dict_global["ax"].clear()
    dict_global["pandas_main_dataframe_read_data"] = None
    read_file_for_first_time(dict_global)
    fill_initial_plot(dict_global)
    dict_global["canvas"].draw()


def read_file_for_first_time(dict_global):
    try:
        dat_file = dict_global["dat_file"]

        pandas_main_dataframe_read_data = read_file = pd.read_csv(
            dat_file,
            delimiter="\t",
            header=1,
            index_col=False,
            nrows=1,
        )
        list_column_names = (
            column_names
        ) = read_file.columns  # pandas_main_dataframe_read_data[:10][0]

        leading_delimiter = True
        if leading_delimiter:
            starting_index = 1
        else:
            starting_index = 0

        column_names = column_names[starting_index:].tolist()
        print(column_names, len(column_names))

        dict_global["column_names"] = column_names

        a, b = dict_global["function_get_new_data"]()

        pandas_main_dataframe_read_data = read_file = pd.read_csv(
            dat_file,
            delimiter="\t",
            header=2,
            index_col=False,
            skiprows=a,
            nrows=b - a,
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


# Function to toggle CSV streaming
# def _button_function_toggle_csv_stream(dict_global):
#     dict_global["streaming"] = not dict_global["streaming"]
#     dict_global["gui_elements"]["button_switch_streaming"].config(
#         text="Start Streaming" if not dict_global["streaming"] else "Stop Streaming"
#     )
#     thread = threading.Thread(target=start_data_streaming(dict_global), daemon=True)
    
    
#     thread.start()

# def _button_function_toggle_csv_stream(dict_global):
#     dict_global["streaming"] = not dict_global["streaming"]
#     dict_global["gui_elements"]["button_switch_streaming"].config(
#         text="Start Streaming" if not dict_global["streaming"] else "Stop Streaming"
#     )

#     if dict_global["streaming"]:
#         # Start the async data streaming in a background task
#         asyncio.create_task(update_plot_async(dict_global))

# import asyncio
# import tkinter as tk

# def _button_function_toggle_csv_stream(dict_global):
#     dict_global["streaming"] = not dict_global["streaming"]
#     dict_global["gui_elements"]["button_switch_streaming"].config(
#         text="Start Streaming" if not dict_global["streaming"] else "Stop Streaming"
#     )

#     # Get or create the event loop
#     try:
#         loop = asyncio.get_running_loop()  # Try getting a running loop
#     except RuntimeError:
#         loop = asyncio.new_event_loop()  # If none exists, create a new one
#         asyncio.set_event_loop(loop)  # Set it as the current event loop

#     if dict_global["streaming"]:
#         asyncio.create_task(update_plot_async(dict_global))  # Properly create async task



def button_function_toggle_csv_stream(dict_global):
    dict_global["streaming"] = not dict_global["streaming"]
    dict_global["gui_elements"]["button_switch_streaming"].config(
        text="Start Streaming" if not dict_global["streaming"] else "Stop Streaming"
    )

    loop = asyncio.get_event_loop()  # Always get the existing running loop

    if dict_global["streaming"]:
        asyncio.run_coroutine_threadsafe(update_plot_async(dict_global), loop)  # Run async task in the loop


def start_data_streaming(dict_global):
    animation = dict_global.get("animation", None)
    if dict_global["streaming"]:
        if not animation:
            animation = FuncAnimation(
                dict_global["fig"],
                update_plot,
                fargs=(dict_global,),
                interval=1000,
                blit=False,
                cache_frame_data=False,
            )
        dict_global["canvas"].draw()
    else:
        if animation:
            animation.event_source.stop()
            animation = None
    dict_global["animation"] = animation


async def fetch_data_async(dict_global):
    # Update function for animation
    # time.sleep(5)
    # for i in range(200):
    # if not dict_global["streaming"]:
    #     return list(
    #         dict_global["lines_in_plot"].values()
    #     )  # Stop updating if streaming is off
    loop = asyncio.get_running_loop()

    try:
        a, b = dict_global["function_get_new_data"]()  # Get next row indices
        df =  await loop.run_in_executor(None,             lambda: pd.read_csv(
                dict_global["dat_file"],
                delimiter="\t",
                header=2,
                index_col=False,
                skiprows=a,
                nrows=b - a
            )
        )
        # ATTENTION: HERE we had sometimes the problem that we did not
        # yield the right dimension of the column names
        if len(df) > 0:
            df.columns = dict_global["column_names"]
            # try:
            #     df.columns = dict_global["column_names"] + ["aeae"]
            # except:
            #     df.columns = dict_global["column_names"]
            convert_time_stamp(df, time_reference=dict_global["time_reference"])

            dict_global["pandas_main_dataframe_read_data"] = pd.concat(
                [dict_global["pandas_main_dataframe_read_data"], df]
            ).drop_duplicates()

            # Update plot lines
            for key in dict_global["keys_of_interest"]:
                line = dict_global["lines_in_plot"][key]
                line[0].set_xdata(
                    dict_global["pandas_main_dataframe_read_data"]["time"]
                )
                line[0].set_ydata(dict_global["pandas_main_dataframe_read_data"][key])

            if dict_global["auto_zoom"]:
                set_axis_on_auto_zoom_respecting_user_limits(dict_global)
    except Exception as e:
        print(e)

    dict_global["canvas"].draw()
    return list(dict_global["lines_in_plot"].values())



# async def update_plot_async(frame, dict_global):
#     """Asynchronous function to update the plot without freezing the GUI."""
#     if not dict_global["streaming"]:
#         return list(dict_global["lines_in_plot"].values())

#     await fetch_data_async(dict_global)

#     # Schedule next update (instead of time.sleep)
#     await asyncio.sleep(1)  # Non-blocking wait
#     return list(dict_global["lines_in_plot"].values())

# async def _update_plot_async(dict_global):
#     """Continuously fetch data and update the plot asynchronously."""
#     while dict_global["streaming"]:
#         await fetch_data_async(dict_global)  # Fetch and process new data
#         dict_global["canvas"].draw()  # Redraw the updated plot
#         await asyncio.sleep(1)  # Adjust interval as needed

async def update_plot_async(dict_global):
    while dict_global["streaming"]:
        try:
            a, b = dict_global["function_get_new_data"]()
            df = await asyncio.to_thread(
                pd.read_csv, 
                dict_global["dat_file"], 
                delimiter="\t", 
                header=2, 
                index_col=False, 
                skiprows=a, 
                nrows=b - a
            )

            if len(df) > 0:
                df.columns = dict_global["column_names"]
                await asyncio.to_thread(convert_time_stamp, df, time_reference=dict_global["time_reference"])
                
                dict_global["pandas_main_dataframe_read_data"] = pd.concat(
                    [dict_global["pandas_main_dataframe_read_data"], df]
                ).drop_duplicates()

                for key in dict_global["keys_of_interest"]:
                    line = dict_global["lines_in_plot"][key]
                    line[0].set_xdata(dict_global["pandas_main_dataframe_read_data"]["time"])
                    line[0].set_ydata(dict_global["pandas_main_dataframe_read_data"][key])

                if dict_global["auto_zoom"]:
                    await asyncio.to_thread(set_axis_on_auto_zoom_respecting_user_limits, dict_global)

            dict_global["canvas"].draw()
        except Exception as e:
            print(e)

        await asyncio.sleep(1)  # Prevents excessive CPU usage



def start_data_streaming(dict_global):
    """Start the async event loop in a separate thread to avoid blocking Tkinter."""
    loop = asyncio.new_event_loop()
    threading.Thread(target=lambda: asyncio.run(update_plot_async(dict_global)), daemon=True).start()


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
