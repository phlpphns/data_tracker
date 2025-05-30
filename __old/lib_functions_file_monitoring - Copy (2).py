import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import numpy as np
import os
import pandas as pd
import sys

import tkinter as tk
from tkinter import ttk, filedialog, messagebox


def convert_time_stamp(aaa, subtractor=None):
    aaa["time"] = pd.to_datetime(aaa["time"], format="%a %b %d %H:%M:%S %Y")
    if not subtractor:
        subtractor = aaa["time"][0]
    aaa["time"] -= subtractor
    aaa["time"] = aaa["time"].dt.total_seconds()
    aaa["time"] /= 3600
    return subtractor


def get_newest_file(file_list):
    """Returns the newest file from a list based on modification date."""
    if not file_list:
        return None  # Return None if the list is empty

    return max(file_list, key=os.path.getmtime)


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


def initial_frames(dict_global):
    paned_window = ttk.PanedWindow(dict_global["root"], orient=tk.VERTICAL)
    # paned_window.pack(expand=False, fill=None)#"both")
    paned_window.grid(row=0, column=0, padx=5, pady=5)
    # (expand=False, fill=None)#"both")

    # Left side (Figure frame)
    figure_frame = ttk.Frame(paned_window, relief="sunken")
    paned_window.add(figure_frame)

    # Right side (Notebook frame)
    notebook_frame = ttk.Frame(paned_window, relief="sunken")
    paned_window.add(notebook_frame)

    dict_global["figure_frame"] = figure_frame
    dict_global["notebook_frame"] = notebook_frame
    dict_global["paned_window"] = paned_window


def first_read(dict_global):
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

        dict_global["first_time"] = convert_time_stamp(aaa)
    except Exception as e:
        print("error   ", e)


def initial_plot(dict_global):
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

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Values")


def read_fresh_file(dict_global):
    first_read(dict_global)
    initial_plot(dict_global)
    dict_global["canvas"].draw()


def _set_up_plot(dict_global):
    # Create Matplotlib Figure
    root = dict_global["root"]

    # fig, ax = plt.subplots(figsize=(16, 10))
    # fig, ax = plt.subplots(figsize=(10, 7))
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.tight_layout()

    dict_global["fig"] = fig
    dict_global["ax"] = ax
    dict_global["ax"].set_xlabel("Time [h]")
    dict_global["ax"].set_ylabel("Value")

    # Embed Matplotlib figure in Tkinter window
    canvas = FigureCanvasTkAgg(dict_global["fig"], master=root)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Add Matplotlib toolbar (Zoom, Pan, Save)
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    toolbar.pack(side=tk.TOP, fill=tk.X)

    dict_global["canvas"] = canvas
    dict_global["toolbar"] = toolbar


def set_up_plot(dict_global):
    """Creates and embeds a Matplotlib figure inside the figure_frame."""
    figure_frame = dict_global["figure_frame"]  # Use the left pane frame

    # Create Matplotlib Figure
    fig, ax = plt.subplots(figsize=(8, 6))
    # fig.tight_layout()

    dict_global["fig"] = fig
    dict_global["ax"] = ax
    dict_global["ax"].set_xlabel("Time [h]")
    dict_global["ax"].set_ylabel("Value")

    # Embed Matplotlib figure in Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=figure_frame)  # Set master to figure_frame
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Add Matplotlib toolbar (Zoom, Pan, Save)
    toolbar = NavigationToolbar2Tk(canvas, figure_frame)  # Set master to figure_frame
    toolbar.update()
    toolbar.pack(side=tk.TOP, fill=tk.X)

    # Store references
    dict_global["canvas"] = canvas
    dict_global["toolbar"] = toolbar


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
        df.columns = dict_global["column_names"]
        # try:
        #     df.columns = dict_global["column_names"] + ["aeae"]
        # except:
        #     df.columns = dict_global["column_names"]
        convert_time_stamp(df, subtractor=dict_global["first_time"])

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


# from test_resize import configure_output_panel


def configure_button_panel(selection_frame, dict_global):
    # toolbar_frame = ttk.Frame(selection_frame)
    # # ======== # ======= # =======
    # toolbar_frame.grid(row=0, column=0, sticky="nsew")
    frame_controls = selection_frame

    for i in range(7):  # Adjust range based on max columns used
        frame_controls.columnconfigure(i, weight=0)  # Keep buttons compact
    # frame_controls.columnconfigure(2, weight=1, uniform="group2")  # Allow file paths to expand

    # ======= # ========== # =========== # =========== # ===========
    # dat_file Filepath Entry
    ttk.Label(frame_controls, text="File:").grid(
        row=0, column=1, padx=5, pady=5, sticky="w"
    )
    entry_dat_filepath = ttk.Entry(frame_controls, width=50)
    entry_dat_filepath.insert(0, dict_global["dat_file"])
    entry_dat_filepath.grid(row=0, column=2, padx=5, pady=5, sticky="w")
    dict_global["entry_dat_filepath"] = entry_dat_filepath
    # ======= # ========== # =========== # =========== # ===========
    # Update Filepath Button
    update_filepath_button = ttk.Button(
        frame_controls,
        text="autosearch file",
        command=lambda: wrapper_find_files(dict_global),
    )
    update_filepath_button.grid(row=0, column=3, padx=5, pady=5, sticky="w")
    dict_global["update_filepath_button"] = update_filepath_button

    # ======= # ========== # =========== # =========== # ===========
    # Start/Stop Button
    read_fresh_file_button = ttk.Button(
        frame_controls,
        text="Read a fresh file",
        command=lambda: read_fresh_file(dict_global),
    )  # partial(bread_fresh_file, dict_global))
    read_fresh_file_button.grid(row=0, column=4, padx=5, pady=5, sticky="w")
    dict_global["read_fresh_file_button"] = read_fresh_file_button

    # ======= # ========== # =========== # =========== # ===========
    # Auto Zoom Button
    auto_zoom_button = ttk.Button(
        frame_controls,
        text=f"Auto Zoom: {dict_global['auto_zoom']}",
        command=lambda: reset_auto_zoom(dict_global),
    )
    auto_zoom_button.grid(row=0, column=5, padx=5, pady=5, sticky="w")
    dict_global["auto_zoom_button"] = auto_zoom_button

    # ======= # ========== # =========== # =========== # ===========
    # Start/Stop Streaming Button
    btn_start_stop = ttk.Button(
        frame_controls,
        text="Start Streaming",
        command=lambda: toggle_csv_stream(dict_global),
    )
    btn_start_stop.grid(row=0, column=6, padx=5, pady=5, sticky="w")
    dict_global["btn_start_stop"] = btn_start_stop

    # ======= # ========== # =========== # =========== # ===========
    # Exit Button
    exit_button = ttk.Button(
        frame_controls, text="Exit", command=lambda: fun_exit_app(dict_global)
    )
    exit_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    # ======= # ========== # =========== # =========== # ===========
    # JSON Filepath Entry
    ttk.Label(frame_controls, text="File:").grid(
        row=1, column=1, padx=5, pady=5, sticky="w"
    )

    # Use StringVar for dynamic updates
    json_filepath_var = tk.StringVar(value=dict_global["json_filepath"])
    entry_json_filepath = ttk.Entry(
        frame_controls, width=40, textvariable=json_filepath_var
    )
    # entry_json_filepath.grid(row=1, column=1, padx=5, pady=5)
    entry_json_filepath.grid(row=1, column=2, padx=5, pady=5, sticky="w")

    dict_global["entry_json_filepath"] = entry_json_filepath

    # Use StringVar for dynamic updates
    json_filepath_var = tk.StringVar(value=dict_global["json_filepath"])

    entry_json_filepath = ttk.Entry(
        frame_controls, width=50, textvariable=json_filepath_var
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
        frame_controls,
        text="Load user settings",
        command=lambda: wrapper_load_json_gui(dict_global),
    )
    load_json_button.grid(row=1, column=3, padx=5, pady=5, sticky="w")
    dict_global["load_json_button"] = load_json_button

    save_json_button = ttk.Button(
        frame_controls,
        text="save user settings",
        command=lambda: wrapper_load_json_gui(dict_global),
    )
    save_json_button.grid(row=1, column=4, padx=5, pady=5, sticky="w")
    dict_global["save_json_button"] = save_json_button

    # ======= # ========== # =========== # =========== # ===========
    # Save as PNG Button
    save_png_button = ttk.Button(
        frame_controls,
        text="Save as PNG",
        command=lambda: save_plot_as_png(dict_global),
    )
    save_png_button.grid(row=1, column=5, padx=5, pady=5)
    dict_global["save_png_button"] = save_png_button


def configure_output_panel(bottom_frame, dict_global):
    
    def open_text_file():
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
                print(text_data)
                print(f"File content: {repr(text_data)}")  # Debug: Check if content is loaded

            print(f"Before insert: text_editor.winfo_exists() = {text_editor.winfo_exists()}")
            text_editor.delete("1.0", tk.END)  # Clear previous content
            text_editor.insert(tk.END, text_data)  # Insert new content
            print("Text inserted successfully.")  # Debug message

            current_file = file_path
            print(f"Loaded text file: {file_path}")

        except OSError as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")


    def save_text_file():
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


    def reload_text_file():
        """Reload the last opened text file."""
        if not current_file:
            messagebox.showwarning("Warning", "No file to reload.")
            return

        print(f"Reloading file: {current_file}")
        open_text_file()  # Reuse open_text_file function



    # ======== # ======= # =======

    def open_json():
        """Open a JSON file and display it in the editor."""
        global current_file
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                json_data = json.load(file)
                # print(json_data)

            # Pretty-print JSON into editor
            json_text_editor.delete("1.0", tk.END)
            json_text_editor.insert(tk.END, json.dumps(json_data, indent=4))

            current_file = file_path
            print(f"Loaded JSON file: {file_path}")

        except (json.JSONDecodeError, OSError) as e:
            messagebox.showerror("Error", f"Failed to open JSON file:\n{e}")

    def save_json():
        """Save the edited JSON data back to file."""
        global current_file
        if not current_file:
            messagebox.showwarning("Warning", "No file loaded. Use 'Open JSON' first.")
            return

        try:
            json_text = json_text_editor.get("1.0", tk.END).strip()
            json_data = json.loads(json_text)  # Validate JSON

            with open(current_file, "w", encoding="utf-8") as file:
                json.dump(json_data, file, indent=4)

            print(f"Saved JSON file: {current_file}")
            messagebox.showinfo("Success", "File saved successfully!")

        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Invalid JSON format:\n{e}")

    def reload_json():
        """Reload the last opened JSON file."""
        if not current_file:
            messagebox.showwarning("Warning", "No file to reload.")
            return

        print(f"Reloading file: {current_file}")
        open_json()  # Reuse open_json function

    def configure_editors_panel():
        pass

    # Create PanedWindow to hold both notebooks
    # bottom_frame.grid(row=1, column=0, sticky="nsew")  # Fill all available space

    bottom_paned = ttk.PanedWindow(bottom_frame, orient=tk.HORIZONTAL)
    bottom_paned.grid(row=0, column=0, sticky="nsew")  # Expand fully

    # Configure bottom_paned to expand
    bottom_paned.columnconfigure(0, weight=1)
    bottom_paned.columnconfigure(1, weight=1)

    # === Left Notebook Frame ===
    left_notebook_frame = ttk.Frame(bottom_paned, borderwidth=2, relief="sunken")
    bottom_paned.add(left_notebook_frame, weight=1)  # Set weight for resizing

    # Ensure the left notebook frame expands
    left_notebook_frame.columnconfigure(0, weight=1)
    left_notebook_frame.rowconfigure(0, weight=1)

    left_notebook = ttk.Notebook(left_notebook_frame)
    left_notebook.grid(row=0, column=0, sticky="nsew")  # Fill all available space

    # left_notebook_frame

    # Left Editor Tab
    left_text_editor_frame = ttk.Frame(left_notebook)
    left_notebook.add(left_text_editor_frame, text="Left Editor")

    # Text editor inside left notebook
    left_text_editor = tk.Text(left_text_editor_frame, wrap="word")
    left_text_editor.grid(
        row=0, column=0, sticky="nsew"
    )  # .pack(fill=tk.BOTH, expand=True)

    left_text_editor_frame.rowconfigure(0, weight=1)
    left_text_editor_frame.columnconfigure(0, weight=1)

    # ========= # ======= # =======
    # ========= # ======= # =======
    # ========= # ======= # =======
    # ========= # ======= # =======

    # # === Tab 1: Text Editor ===
    # output_frame = ttk.Frame(notebook)
    # notebook.add(output_frame, text="Output")

    # output_text = tk.Text(output_frame, wrap="word", state="normal")
    # output_text.pack(expand=True, fill="both")

    # === Right Notebook Frame ===
    right_notebook_frame = ttk.Frame(bottom_paned, borderwidth=2, relief="sunken")
    bottom_paned.add(right_notebook_frame, weight=1)

    # Ensure the right notebook frame expands
    right_notebook_frame.rowconfigure(0, weight=1)
    right_notebook_frame.columnconfigure(0, weight=1)
    # left_text_editor_frame.rowconfigure(0, weight=1)
    # left_text_editor_frame.columnconfigure(0, weight=1)

    right_notebook = ttk.Notebook(right_notebook_frame)
    right_notebook.grid(row=0, column=0, sticky="nsew")  # Fill all available space

    # Right Editor Tab
    # another_frame = ttk.Frame(right_notebook)

    right_notebook.rowconfigure(0, weight=1)
    right_notebook.columnconfigure(0, weight=1)
    # right_notebook.add(another_frame, text="Another Tab")

    # Configure another_frame to expand
    # another_frame.columnconfigure(0, weight=1)
    # another_frame.columnconfigure(1, weight=1)
    # another_frame.columnconfigure(2, weight=1)
    # another_frame.rowconfigure(1, weight=1)

    # ttk.Button(another_frame, text="Open JSON", command=open_json).grid(
    #     row=1, column=0, sticky="nsew", padx=5, pady=2
    # )
    # ttk.Button(another_frame, text="Save JSON", command=save_json).grid(
    #     row=1, column=1, sticky="nsew", padx=5, pady=2
    # )
    # ttk.Button(another_frame, text="Reload", command=reload_json).grid(
    #     row=1, column=2, sticky="nsew", padx=5, pady=2
    # )

    # # Buttons inside right notebook
    # button_frame = ttk.Frame(another_frame)
    # button_frame.grid(row=0, column=0, columnspan=3, sticky="ew")

    # === Tab 2: JSON Editor ===
    json_editor_frame = ttk.Frame(right_notebook)
    right_notebook.add(json_editor_frame, text="JSON Editor")

    # JSON Text Editor
    json_text_editor = tk.Text(json_editor_frame, wrap="word", font=("Courier", 10))
    json_text_editor.grid(
        row=1, column=0, columnspan=3, sticky="ew"
    )  # .pack(expand=True, fill="both", padx=5, pady=5)

    # json_editor_frame.rowconfigure(0, weight=1)
    # json_editor_frame.columnconfigure(0, weight=1)

    # Button Frame for File Operations
    # button_frame = ttk.Frame(json_editor_frame)
    # button_frame.grid(row=2, column=0, columnspan=3, sticky="ew")  # .pack(fill="both")

    # button_frame.rowconfigure(0, weight=1)
    # button_frame.columnconfigure(0, weight=1)

    # # Add buttons for file operations
    # ttk.Button(button_frame, text="Open JSON", command=open_json).pack(side="left", padx=5, pady=2)
    # ttk.Button(button_frame, text="Save JSON", command=save_json).pack(side="left", padx=5, pady=2)
    # ttk.Button(button_frame, text="Reload", command=reload_json).pack(side="left", padx=5, pady=2)

    ttk.Button(json_editor_frame, text="Open JSON", command=open_json).grid(
        row=0, column=0, sticky="nsew", padx=5, pady=2
    )
    ttk.Button(json_editor_frame, text="Save JSON", command=save_json).grid(
        row=0, column=1, sticky="nsew", padx=5, pady=2
    )
    ttk.Button(json_editor_frame, text="Reload", command=reload_json).grid(
        row=0, column=2, sticky="nsew", padx=5, pady=2
    )

    # ttk.Button(button_frame, text="Open JSON", command=open_json).grid(
    #     row=0, column=0, sticky="nsew", padx=5, pady=2
    # )
    # ttk.Button(button_frame, text="Save JSON", command=save_json).grid(
    #     row=0, column=1, sticky="nsew", padx=5, pady=2
    # )
    # ttk.Button(button_frame, text="Reload", command=reload_json).grid(
    #     row=0, column=2, sticky="nsew", padx=5, pady=2
    # )
    right_text_editor_frame = ttk.Frame(right_notebook)
    right_notebook.add(right_text_editor_frame, text="Note pad - append mode")

    # Text editor inside right notebook
    text_editor = tk.Text(right_text_editor_frame, wrap="word", font=("Courier", 10))
    text_editor.grid(row=1, column=0, columnspan=3, sticky="ew")


    # Create buttons and place them inside the button_frame
    ttk.Button(right_text_editor_frame, text="Open text file", command=open_text_file).grid(
        row=0, column=0, padx=5, pady=2
    )
    ttk.Button(right_text_editor_frame, text="Save JSON").grid(
        row=0, column=1, padx=5, pady=2
    )
    ttk.Button(right_text_editor_frame, text="Reload").grid(
        row=0, column=2, padx=5, pady=2
    )

    # Configure another_frame to expand
    # another_frame.columnconfigure(0, weight=1)
    # another_frame.columnconfigure(1, weight=1)
    # another_frame.columnconfigure(2, weight=1)
    # another_frame.rowconfigure(1, weight=1)

    # right_text_editor_frame.rowconfigure(0, weight=1)
    # right_text_editor_frame.columnconfigure(0, weight=1)

    # dict_global["right_text_editor"] = tk.Text(right_text_editor_frame, wrap="word")
    # dict_global["right_text_editor"].grid(row=1, column=0, columnspan=3, sticky="nsew")
    # pack(fill=tk.BOTH, expand=True)

    # Redirect print statements to Output Window
    sys.stdout = RedirectText(left_text_editor)


def create_gui_elements(dict_global):
    # paned_window = dict_global['paned_window']
    # # figure_frame = dict_global['figure_frame']
    # notebook_frame = dict_global['notebook_frame']
    # # ======= # ========== # =========== # =========== # ===========
    # # Create Tkinter Controls
    # frame_controls = ttk.Frame(paned_window)
    # paned_window.add(frame_controls)

    root = dict_global["root"]
    # root.title("Adjustable Layout")
    # root.geometry("1200x1600")  # Increased size for better visibility

    # # Bind resizing event
    # root.bind("<Configure>", adjust_pane_ratios)

    # Main container (grid-based)
    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, sticky="nsew")

    # Main PanedWindow (Vertical) to divide top and bottom
    paned_window = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
    paned_window.grid(row=0, column=0, sticky="nsew")

    # Top section (Figure Frame)
    figure_frame = ttk.Frame(paned_window, borderwidth=2, relief="sunken")
    # paned_window.add(figure_frame, weight=3)  # Plot gets more space

    selection_frame = ttk.Frame(paned_window, borderwidth=2, relief="sunken")
    selection_frame.grid(row=0, column=0, sticky="nsew")
    # paned_window.add(selection_frame)#, weight=
    # Bottom section (Two Notebooks)1)  # Bottom section takes 1/3 of the height

    bottom_frame = ttk.Frame(paned_window, borderwidth=2, relief="sunken")
    bottom_frame.grid(row=1, column=0, sticky="nsew")
    # paned_window.add(bottom_frame, weight=0)  # Bottom section takes 1/3 of the height

    paned_window.add(figure_frame)
    paned_window.add(selection_frame)
    paned_window.add(bottom_frame)

    dict_global["paned_window"] = paned_window
    dict_global["figure_frame"] = figure_frame
    dict_global["selection_frame"] = selection_frame
    dict_global["bottom_frame"] = bottom_frame

    # configure_output_panel(dict_global['bottom_frame'])
    # configure_button_panel(dict_global["selection_frame"])

    if False:
        selection_height = selection_frame.winfo_height()
        # selection_height = dict_global.get("selection_frame_height", 0)
        dict_global["selection_frame_height"] = selection_height
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

    figure_frame.grid_rowconfigure(0, weight=1)
    figure_frame.grid_columnconfigure(0, weight=1)

    selection_frame.grid_rowconfigure(0, weight=1)
    selection_frame.grid_columnconfigure(0, weight=1)

    bottom_frame.grid_rowconfigure(0, weight=1)
    bottom_frame.grid_columnconfigure(0, weight=1)

    # bottom_frame.columnconfigure(0, weight=1)
    # bottom_frame.rowconfigure(0, weight=1)

    # Configure bottom_frame to expand
    # # Configure resizing behavior for main_frame
    # # Configure resizing behavior for figure_frame

    # # # Configure resizing behavior for bottom_frame

    configure_button_panel(dict_global["selection_frame"], dict_global)
    configure_output_panel(dict_global["bottom_frame"], dict_global)

    if False:
        # ======= # ========== # =========== # =========== # ===========
        # dat_file Filepath Entry
        ttk.Label(frame_controls, text="File:").grid(row=0, column=1, padx=5, pady=5)
        entry_dat_filepath = ttk.Entry(frame_controls, width=30)
        entry_dat_filepath.insert(0, dict_global["dat_file"])
        entry_dat_filepath.grid(row=0, column=2, padx=5, pady=5)
        dict_global["entry_dat_filepath"] = entry_dat_filepath
        # ======= # ========== # =========== # =========== # ===========
        # Update Filepath Button
        update_filepath_button = ttk.Button(
            frame_controls,
            text="autosearch file",
            command=lambda: wrapper_find_files(dict_global),
        )
        update_filepath_button.grid(row=0, column=3, padx=5, pady=5)
        dict_global["update_filepath_button"] = update_filepath_button

        # ======= # ========== # =========== # =========== # ===========
        # Start/Stop Button
        read_fresh_file_button = ttk.Button(
            frame_controls,
            text="Read a fresh file",
            command=lambda: read_fresh_file(dict_global),
        )  # partial(bread_fresh_file, dict_global))
        read_fresh_file_button.grid(row=0, column=4, padx=5, pady=5)
        dict_global["read_fresh_file_button"] = read_fresh_file_button

        # ======= # ========== # =========== # =========== # ===========
        # Auto Zoom Button
        auto_zoom_button = ttk.Button(
            frame_controls,
            text=f"Auto Zoom: {dict_global['auto_zoom']}",
            command=lambda: reset_auto_zoom(dict_global),
        )
        auto_zoom_button.grid(row=0, column=5, padx=5, pady=5)
        dict_global["auto_zoom_button"] = auto_zoom_button

        # ======= # ========== # =========== # =========== # ===========
        # Start/Stop Streaming Button
        btn_start_stop = ttk.Button(
            frame_controls,
            text="Start Streaming",
            command=lambda: toggle_csv_stream(dict_global),
        )
        btn_start_stop.grid(row=0, column=6, padx=5, pady=5)
        dict_global["btn_start_stop"] = btn_start_stop

        # ======= # ========== # =========== # =========== # ===========
        # Exit Button
        exit_button = ttk.Button(
            frame_controls, text="Exit", command=lambda: fun_exit_app(dict_global)
        )
        exit_button.grid(row=1, column=0, padx=5, pady=5)

        # ======= # ========== # =========== # =========== # ===========
        # JSON Filepath Entry
        ttk.Label(frame_controls, text="File:").grid(row=1, column=1, padx=5, pady=5)
        # entry_json_filepath = ttk.Entry(frame_controls, width=30)
        # # ---->>>>> PAY ATTENTION?
        # # json_filepath = entry_json_filepath.get()
        # # if not json_filepath:
        # #     entry_json_filepath.insert(0, dict_global["json_filepath"])
        # dict_global["json_filepath"] = entry_json_filepath.get()
        # # I think we need to make an update function
        # # dict_global["entry_dat_filepath"].insert(0, file)
        # dict_global["entry_json_filepath"] =

        # Use StringVar for dynamic updates
        json_filepath_var = tk.StringVar(value=dict_global["json_filepath"])
        entry_json_filepath = ttk.Entry(
            frame_controls, width=40, textvariable=json_filepath_var
        )
        # entry_json_filepath.grid(row=1, column=1, padx=5, pady=5)
        entry_json_filepath.grid(row=1, column=2, padx=5, pady=5)

        dict_global["entry_json_filepath"] = entry_json_filepath

        # Use StringVar for dynamic updates
        json_filepath_var = tk.StringVar(value=dict_global["json_filepath"])

        entry_json_filepath = ttk.Entry(
            frame_controls, width=50, textvariable=json_filepath_var
        )
        entry_json_filepath.grid(row=1, column=2, padx=5, pady=5)

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
            frame_controls,
            text="Load user settings",
            command=lambda: wrapper_load_json_gui(dict_global),
        )
        load_json_button.grid(row=1, column=3, padx=5, pady=5)
        dict_global["load_json_button"] = load_json_button

        save_json_button = ttk.Button(
            frame_controls,
            text="save user settings",
            command=lambda: wrapper_load_json_gui(dict_global),
        )
        save_json_button.grid(row=1, column=4, padx=5, pady=5)
        dict_global["save_json_button"] = save_json_button

        # ======= # ========== # =========== # =========== # ===========
        # Save as PNG Button
        save_png_button = ttk.Button(
            frame_controls,
            text="Save as PNG",
            command=lambda: save_plot_as_png(dict_global),
        )
        save_png_button.grid(row=1, column=5, padx=5, pady=5)
        dict_global["save_png_button"] = save_png_button

    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========


class RedirectText:
    """Class to redirect print output to a Tkinter Text widget."""

    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)  # Auto-scroll

    def flush(self):
        pass  # Required for compatibility with sys.stdout


# class JSONEditorApp(ttk.Frame):
#     """JSON Editor embedded in a notebook tab."""
#     def __init__(self, parent):
#         super().__init__(parent)

#         self.current_file = None  # Store the last opened file

#         # JSON Text Editor
#         self.text_editor = tk.Text(self, wrap="word", font=("Courier", 10))
#         self.text_editor.pack(expand=True, fill="both", padx=5, pady=5)

#         # Button Frame for File Operations
#         self.button_frame = ttk.Frame(self)
#         self.button_frame.pack(fill="x")

#         ttk.Button(self.button_frame, text="Open JSON", command=self.open_json).pack(side="left", padx=5, pady=2)
#         ttk.Button(self.button_frame, text="Save JSON", command=self.save_json).pack(side="left", padx=5, pady=2)
#         ttk.Button(self.button_frame, text="Reload", command=self.reload_json).pack(side="left", padx=5, pady=2)

#     def open_json(self):
#         """Open a JSON file and display it in the editor."""
#         file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
#         if not file_path:
#             return

#         try:
#             with open(file_path, "r", encoding="utf-8") as file:
#                 json_data = json.load(file)

#             # Pretty-print JSON into editor
#             self.text_editor.delete("1.0", tk.END)
#             self.text_editor.insert(tk.END, json.dumps(json_data, indent=4))

#             self.current_file = file_path
#             print(f"Loaded JSON file: {file_path}")

#         except (json.JSONDecodeError, OSError) as e:
#             messagebox.showerror("Error", f"Failed to open JSON file:\n{e}")

#     def save_json(self):
#         """Save the edited JSON data back to file."""
#         if not self.current_file:
#             messagebox.showwarning("Warning", "No file loaded. Use 'Open JSON' first.")
#             return

#         try:
#             json_text = self.text_editor.get("1.0", tk.END).strip()
#             json_data = json.loads(json_text)  # Validate JSON

#             with open(self.current_file, "w", encoding="utf-8") as file:
#                 json.dump(json_data, file, indent=4)

#             print(f"Saved JSON file: {self.current_file}")
#             messagebox.showinfo("Success", "File saved successfully!")

#         except json.JSONDecodeError as e:
#             messagebox.showerror("Error", f"Invalid JSON format:\n{e}")

#     def reload_json(self):
#         """Reload the last opened JSON file."""
#         if not self.current_file:
#             messagebox.showwarning("Warning", "No file to reload.")
#             return

#         print(f"Reloading file: {self.current_file}")
#         self.open_json()  # Reuse open_json function


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


def find_files(source_dir, starts_with="", contains="", file_ending=""):
    found_files = [
        os.path.join(d, x)
        for d, dirs, files in os.walk(source_dir)
        for x in files
        # if x.endswith(file_ending)
        if x.startswith(starts_with) and x.endswith(file_ending)
    ]
    return found_files


def wrapper_find_files(dict_global):
    file_ending = dict_global["pattern_auto_file_search"]
    found_files = find_files(
        source_dir=".", starts_with="", contains="", file_ending=file_ending
    )
    file = get_newest_file(found_files)
    dict_global["dat_file"] = file
    dict_global["entry_dat_filepath"].insert(0, file)
    print(f"found file {dict_global['dat_file']}")


def load_json(json_filepath):
    try:
        dict_settings = {}
        with open(json_filepath, "r") as j:
            dict_settings = json.loads(j.read())
        print(f"Loaded JSON: {dict_settings}")
    except Exception as e:
        print(f"Error loading JSON: {e}")
    return dict_settings


def wrapper_load_json_gui(dict_global):
    # file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])

    # def update_json_filepath(new_path):
    #     """Update file path in dict_global and UI."""
    #     dict_global["json_filepath"] = new_path
    #     json_filepath_var.set(new_path)  # Automatically updates the entry field

    # update_json_filepath(file_path)

    json_filepath = dict_global["json_filepath"]
    dict_settings = load_json(json_filepath)


# Function to toggle CSV streaming
def toggle_csv_stream(dict_global):
    animation = dict_global.get("animation")
    # animation = dict_global["animation"]

    dict_global["streaming"] = not dict_global["streaming"]
    dict_global["btn_start_stop"].config(
        text="Start Streaming" if not dict_global["streaming"] else "Stop Streaming"
    )

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


def fun_exit_app(dict_global):
    print("Exiting application")
    dict_global["root"].quit()
    sys.exit()


def save_current_settings():
    dict_filtered = {}
    for key, value in dict_settings.items():
        dict_filtered[key] = value
    return dict_filtered


import time


def save_plot_as_png(dict_global):
    timestr = time.strftime("%Y%m%d_%H%M%S")
    png_name = dict_global["name_png"]
    a, b = os.path.splitext(png_name)
    # print(a, b)
    png_name = f"{a}_{timestr}{b}"
    dict_global["fig"].savefig(png_name, bbox_inches="tight")
    print(f"Saved file as {png_name}")


def reset_auto_zoom(dict_global):
    dict_global["auto_zoom"] = not dict_global["auto_zoom"]
    dict_global["auto_zoom_button"].config(
        text=f"Auto Zoom: {dict_global['auto_zoom']}"
    )
    if dict_global["auto_zoom"]:
        set_axis_on_auto_zoom_respecting_user_limits(dict_global)
        dict_global["canvas"].draw()
