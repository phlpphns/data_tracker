# TODOS:
# eliminate global variables; adapt file opening procedures?
# automatical searching and loading of files
# update get_new_data
# we need to handle different
# we could enforce that dictionary keys must be present!
# check streaming button
# implement strategy pattern
# we could store each button in a function and store it in the dict.

import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import numpy as np
import os
import pandas as pd
import sys

import time

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# from functools import partial


class RedirectText:
    """Class to redirect print output to a Tkinter Text widget."""

    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)  # Auto-scroll

    def flush(self):
        pass  # Required for compatibility with sys.stdout


class editor_functions:
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


get_new_data = create_data_generator()

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

    dict_global["paned_window"] = paned_window
    dict_global["frame_holding_figure"] = frame_holding_figure
    dict_global["frame_holding_buttons"] = frame_holding_buttons
    dict_global["frame_holding_consoles"] = frame_holding_consoles

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

    configure_button_panel(dict_global["frame_holding_buttons"], dict_global)
    configure_output_panel(dict_global["frame_holding_consoles"], dict_global)
    configure_figure_panel(dict_global["frame_holding_figure"], dict_global)

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
    entry_dat_filepath = ttk.Entry(frame_holding_buttons, width=50)
    entry_dat_filepath.insert(0, dict_global["dat_file"])
    entry_dat_filepath.grid(row=0, column=2, padx=5, pady=5, sticky="w")
    dict_global["entry_dat_filepath"] = entry_dat_filepath

    # ======= # ========== # =========== # =========== # ===========
    # Update Filepath Button
    update_filepath_button = ttk.Button(
        frame_holding_buttons,
        text="autosearch file",
        command=lambda: button_function_autosearch_file(dict_global),
    )
    update_filepath_button.grid(row=0, column=3, padx=5, pady=5, sticky="w")
    dict_global["update_filepath_button"] = update_filepath_button

    # ======= # ========== # =========== # =========== # ===========
    # Start/Stop Button
    read_fresh_file_button = ttk.Button(
        frame_holding_buttons,
        text="Read a fresh file",
        command=lambda: read_fresh_file(dict_global),
    )  # partial(bread_fresh_file, dict_global))
    read_fresh_file_button.grid(row=0, column=4, padx=5, pady=5, sticky="w")
    dict_global["read_fresh_file_button"] = read_fresh_file_button

    # ======= # ========== # =========== # =========== # ===========
    # Start/Stop Streaming Button
    button_switch_streaming = ttk.Button(
        frame_holding_buttons,
        text=f"Streaming: {dict_global['streaming']}",
        command=lambda: button_function_toggle_csv_stream(dict_global),
    )
    button_switch_streaming.grid(row=0, column=5, padx=5, pady=5, sticky="w")
    dict_global["button_switch_streaming"] = button_switch_streaming

    # ======= # ========== # =========== # =========== # ===========
    # Auto Zoom Button
    auto_zoom_button = ttk.Button(
        frame_holding_buttons,
        text=f"Auto Zoom: {dict_global['auto_zoom']}",
        command=lambda: button_function_reset_auto_zoom(dict_global),
    )
    auto_zoom_button.grid(row=0, column=6, padx=5, pady=5, sticky="w")
    dict_global["auto_zoom_button"] = auto_zoom_button

    # ======= # ========== # =========== # =========== # ===========
    # Exit Button
    exit_button = ttk.Button(
        frame_holding_buttons, text="Exit", command=lambda: button_function_exit_app(dict_global)
    )
    exit_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    # ======= # ========== # =========== # =========== # ===========
    # JSON Filepath Entry
    ttk.Label(frame_holding_buttons, text="File:").grid(
        row=1, column=1, padx=5, pady=5, sticky="w"
    )

    # ======= # ========== # =========== # =========== # ===========
    # Use StringVar for dynamic updates
    json_filepath_var = tk.StringVar(value=dict_global["json_filepath"])
    entry_json_filepath = ttk.Entry(
        frame_holding_buttons, width=40, textvariable=json_filepath_var
    )

    # ======= # ========== # =========== # =========== # ===========
    # entry_json_filepath.grid(row=1, column=1, padx=5, pady=5)
    entry_json_filepath.grid(row=1, column=2, padx=5, pady=5, sticky="w")

    dict_global["entry_json_filepath"] = entry_json_filepath

    # ======= # ========== # =========== # =========== # ===========
    # Use StringVar for dynamic updates
    json_filepath_var = tk.StringVar(value=dict_global["json_filepath"])

    entry_json_filepath = ttk.Entry(
        frame_holding_buttons, width=50, textvariable=json_filepath_var
    )
    entry_json_filepath.grid(row=1, column=2, padx=5, pady=5, sticky="w")

    def update_json_filepath(event=None):
        """Update dict_global when the user enters a new file path."""
        new_path = json_filepath_var.get().strip().strip('"')
        if new_path:
            dict_global["json_filepath"] = new_path
            print(f"Updated file path: {dict_global['json_filepath']}")
            # open_json(new_path)

    # Bind "Enter" key to update the file path
    entry_json_filepath.bind("<Return>", update_json_filepath)

    # ======= # ========== # =========== # =========== # ===========
    # Load JSON Button
    load_json_button = ttk.Button(
        frame_holding_buttons,
        text="Load user settings",
        command=lambda: button_function_load_user_settings(dict_global),
    )
    load_json_button.grid(row=1, column=3, padx=5, pady=5, sticky="w")
    dict_global["load_json_button"] = load_json_button

    # ======= # ========== # =========== # =========== # ===========
    # Button to save config dict
    save_json_button = ttk.Button(
        frame_holding_buttons,
        text="save user settings",
        command=lambda: button_function_save_user_settings(dict_global),
    )
    save_json_button.grid(row=1, column=4, padx=5, pady=5, sticky="w")
    dict_global["save_json_button"] = save_json_button

    # ======= # ========== # =========== # =========== # ===========
    # Save as PNG Button
    save_png_button = ttk.Button(
        frame_holding_buttons,
        text="Save as PNG",
        command=lambda: button_function_save_plot_as_png(dict_global),
    )
    save_png_button.grid(row=1, column=5, padx=5, pady=5)
    dict_global["save_png_button"] = save_png_button


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
        left_notebook.add(left_text_editor_frame, text="Left Editor")

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
            command=lambda: editor_functions.open_json(json_text_editor),
        ).grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        ttk.Button(
            right_side_json_editor_frame,
            text="Save JSON",
            command=lambda: editor_functions.save_json(json_text_editor),
        ).grid(row=1, column=1, sticky="nsew", padx=5, pady=2)
        ttk.Button(
            right_side_json_editor_frame,
            text="Reload",
            command=lambda: editor_functions.reload_json(json_text_editor),
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
            command=lambda: editor_functions.open_text_file(text_editor),
        ).grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        ttk.Button(
            right_side_text_editor_frame,
            text="Save text file",
            command=lambda: editor_functions.save_text_file(text_editor),
        ).grid(row=1, column=1, sticky="nsew", padx=5, pady=2)
        ttk.Button(
            right_side_text_editor_frame,
            text="Reload text file",
            command=lambda: editor_functions.reload_text_file(text_editor),
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
    read_file_for_first_time(dict_global)
    fill_initial_plot(dict_global)
    dict_global["canvas"].draw()


def read_file_for_first_time(dict_global):
    try:
        dat_file = dict_global["dat_file"]

        aaa = read_file = pd.read_csv(
            dat_file, delimiter="\t", header=1, index_col=False, nrows=1
        )
        list_column_names = column_names = read_file.columns  # aaa[:10][0]

        leading_delimiter = True
        if leading_delimiter:
            starting_index = 1
        else:
            starting_index = 0

        column_names = column_names[starting_index:].tolist()
        print(column_names, len(column_names))

        dict_global["column_names"] = column_names

        a, b = get_new_data()

        aaa = read_file = pd.read_csv(
            dat_file, delimiter="\t", header=2, index_col=False, skiprows=a, nrows=b - a
        )
        # list_column_names = column_names = read_file.columns  # aaa[:10][0]
        aaa.columns = column_names  # [:-1]  # Set new column names
        # aaa.reset_index(drop=True, inplace=True)  # Reset index
        # print(aaa.columns)
        # print(aaaaaa)
        dict_global["aaa"] = aaa

        dict_global["time_reference"] = convert_time_stamp(aaa, time_reference=None)
    except Exception as e:
        print("error   ", e)


def fill_initial_plot(dict_global):
    fig = dict_global["fig"]
    ax = dict_global["ax"]

    try:
        dict_global["lines_in_plot"] = {}
        aaa = dict_global["aaa"]
        # Plot initial data
        for index_key, key in enumerate(dict_global["keys_of_interest"]):
            column = aaa[key]
            dict_global["lines_in_plot"][key] = ax.plot(
                aaa["time"], aaa[key], label=key
            )
        ax.legend()
    except Exception as e:
        print("error   ", e)

    # ax.set_xlabel("Time (s)")
    # ax.set_ylabel("Values")




def update_plot(frame, dict_global):
    # Update function for animation
    if not dict_global["streaming"]:
        return list(
            dict_global["lines_in_plot"].values()
        )  # Stop updating if streaming is off

    try:
        a, b = get_new_data()  # Get next row indices
        df = pd.read_csv(
            dict_global["dat_file"],
            delimiter="\t",
            header=1,
            index_col=False,
            skiprows=a,
            nrows=b - a,
        )
        # ATTENTION: HERE we had sometimes the problem that we did not
        # yield the right dimension of the column names
        df.columns = dict_global["column_names"]
        # try:
        #     df.columns = dict_global["column_names"] + ["aeae"]
        # except:
        #     df.columns = dict_global["column_names"]
        convert_time_stamp(df, time_reference=dict_global["time_reference"])

        dict_global["aaa"] = pd.concat([dict_global["aaa"], df]).drop_duplicates()

        # Update plot lines
        for key in dict_global["keys_of_interest"]:
            line = dict_global["lines_in_plot"][key]
            line[0].set_xdata(dict_global["aaa"]["time"])
            line[0].set_ydata(dict_global["aaa"][key])

        if dict_global["auto_zoom"]:
            set_axis_on_auto_zoom_respecting_user_limits(dict_global)
    except Exception as e:
        print(e)

    dict_global["canvas"].draw()
    return list(dict_global["lines_in_plot"].values())


def set_axis_on_auto_zoom_respecting_user_limits(dict_global):
    aaa = dict_global["aaa"]

    dict_global["ax"].set_xlim(
        [0, max(dict_global["user_defined_max_x_threshold"], np.max(aaa["time"]) * 1.1)]
    )
    dict_global["ax"].set_ylim(
        [
            0,
            max(
                dict_global["user_defined_max_y_threshold"],
                np.max(aaa[dict_global["keys_of_interest"]]) * 1.1,
            ),

        ]
    )


def load_json(json_filepath):
    try:
        dict_settings = {}
        with open(json_filepath, "r", encoding="utf-8") as j:
            dict_settings = json.loads(j.read())
        print(f"Loaded JSON: {dict_settings}")
    except Exception as e:
        print(f"Error loading JSON: {e}")
    return dict_settings


# def write_json(json_filepath, json_dat):
def write_json_file(dict_json, json_name):
    # formerly: json_name, json_file
    try:
        with open(json_name, "w") as outfile:
            json.dump(dict_json, outfile, sort_keys=True, indent=4)
        print(f"wrote JSON: {dict_json}")
    except Exception as e:
        print(f"Error writingJSON: {e}")




def convert_time_stamp(aaa, time_reference=None):
    aaa["time"] = pd.to_datetime(aaa["time"], format="%a %b %d %H:%M:%S %Y")
    if not time_reference:
        time_reference = aaa["time"][0]
    aaa["time"] -= time_reference
    aaa["time"] = aaa["time"].dt.total_seconds()
    aaa["time"] /= 3600
    return time_reference


def button_function_autosearch_file(dict_global):
    find_newest_file_with_restraints(dict_global)
    dict_global["entry_dat_filepath"].insert(0, file)


def find_newest_file_with_restraints(dict_global):
    """
    get list of files in the tree starting from a reference root
    that correspond to a patten
    get the newest file, and updata dict_global accordingly
    """
    file_ending = dict_global["pattern_auto_file_search"]
    found_files = find_files(
        source_dir=dict_global['root_dir_data_files'], starts_with="", contains="", file_ending=file_ending
    )
    file = get_newest_file_from_list(found_files)
    dict_global["dat_file"] = file
    print(f"found file {dict_global['dat_file']}")


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
    except:
        print("error in load_user_settings")


def button_function_save_user_settings(dict_global):
    try:
        dict_user_settings = {
            key: dict_global[key] for key in dict_global["dict_user_settings_keys"]
        }
        print(dict_user_settings)
        # print("IMPLEMENT JSON SAVER")
        write_json_file(dict_user_settings, dict_global["json_filepath"])
    except:
        print("error in save_user_settings")


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


# Function to toggle CSV streaming
def button_function_toggle_csv_stream(dict_global):
    dict_global["streaming"] = not dict_global["streaming"]
    dict_global["button_switch_streaming"].config(
        text="Start Streaming" if not dict_global["streaming"] else "Stop Streaming"
    )
    start_data_streaming(dict_global)


def button_function_exit_app(dict_global):
    print("Exiting application")
    dict_global["root"].quit()
    sys.exit()

def button_function_reset_auto_zoom(dict_global):
    dict_global["auto_zoom"] = not dict_global["auto_zoom"]
    dict_global["auto_zoom_button"].config(
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
        We have a set of standard parameters that can be saved and changed by reading the respective json file.\
        \n\n\n May the electrons be with you - have fun!!! \n\n\n"
    )


