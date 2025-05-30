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


def gen_yield_line_numbers():
    value_to_add = 1000
    i = -1
    while True:
        # for i in range(30):
        i += 1
        yield [i * value_to_add, (i + 1) * value_to_add]


def get_newest_file(file_list):
    """Returns the newest file from a list based on modification date."""
    if not file_list:
        return None  # Return None if the list is empty

    return max(file_list, key=os.path.getmtime)


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


def set_up_plot(dict_global):
    # Create Matplotlib Figure
    root = dict_global["root"]

    fig, ax = plt.subplots(figsize=(16, 10))
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


def create_gui_elements(dict_global):
    # ======= # ========== # =========== # =========== # ===========
    # Create Tkinter Controls
    frame_controls = ttk.Frame(dict_global["root"])
    frame_controls.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

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
    entry_json_filepath = ttk.Entry(frame_controls, width=30)
    entry_json_filepath.insert(0, dict_global["json_filepath"])
    entry_json_filepath.grid(row=1, column=2, padx=5, pady=5)
    dict_global["entry_json_filepath"] = entry_json_filepath

    # ======= # ========== # =========== # =========== # ===========
    # Load JSON Button
    load_json_button = ttk.Button(
        frame_controls,
        text="Load JSON",
        command=lambda: wrapper_load_json_gui(dict_global),
    )
    load_json_button.grid(row=1, column=3, padx=5, pady=5)
    dict_global["load_json_button"] = load_json_button

    # ======= # ========== # =========== # =========== # ===========
    # Save as PNG Button
    save_png_button = ttk.Button(
        frame_controls,
        text="Save as PNG",
        command=lambda: save_plot_as_png(dict_global),
    )
    save_png_button.grid(row=1, column=4, padx=5, pady=5)
    dict_global["save_png_button"] = save_png_button


    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========

    root = dict_global['root']
    # root.geometry("600x400")
    # Create Notebook (Tabbed Interface)
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    # === Tab 1: Text Editor ===
    output_frame = ttk.Frame(notebook)
    notebook.add(output_frame, text="Output")

    output_text = tk.Text(output_frame, wrap="word", state="normal")
    output_text.pack(expand=True, fill="both")
    # Redirect print statements to the output window
    # sys.stdout = RedirectText(output_text)
    # # === Tab 3: Output Window ===
    # self.output_frame = ttk.Frame(self.notebook)
    # self.notebook.add(self.output_frame, text="Output")

    # self.output_text = tk.Text(self.output_frame, wrap="word", state="normal", font=("Courier", 10))
    # self.output_text.pack(expand=True, fill="both")

    # === Tab 2: Output Window ===
    text_editor_frame = ttk.Frame(notebook)
    notebook.add(text_editor_frame, text="Text Editor")

    text_editor = tk.Text(text_editor_frame, wrap="word")
    text_editor.pack(expand=True, fill="both")

    # # === Tab 1: Plain Text Editor ===
    # self.text_editor_frame = ttk.Frame(self.notebook)
    # self.notebook.add(self.text_editor_frame, text="Text Editor")

    # self.text_editor = tk.Text(self.text_editor_frame, wrap="word", font=("Courier", 10))
    # self.text_editor.pack(expand=True, fill="both")

    # === Tab 2: JSON Editor (Integrated) ===
    json_editor_frame = JSONEditorApp(notebook)
    notebook.add(json_editor_frame, text="JSON Editor")


    # Redirect print statements to Output Window
    sys.stdout = RedirectText(output_text)



class RedirectText:
    """Class to redirect print output to a Tkinter Text widget."""
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)  # Auto-scroll

    def flush(self):
        pass  # Required for compatibility with sys.stdout


class JSONEditorApp(ttk.Frame):
    """JSON Editor embedded in a notebook tab."""
    def __init__(self, parent):
        super().__init__(parent)

        self.current_file = None  # Store the last opened file

        # JSON Text Editor
        self.text_editor = tk.Text(self, wrap="word", font=("Courier", 10))
        self.text_editor.pack(expand=True, fill="both", padx=5, pady=5)

        # Button Frame for File Operations
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(fill="x")

        ttk.Button(self.button_frame, text="Open JSON", command=self.open_json).pack(side="left", padx=5, pady=2)
        ttk.Button(self.button_frame, text="Save JSON", command=self.save_json).pack(side="left", padx=5, pady=2)
        ttk.Button(self.button_frame, text="Reload", command=self.reload_json).pack(side="left", padx=5, pady=2)

    def open_json(self):
        """Open a JSON file and display it in the editor."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                json_data = json.load(file)

            # Pretty-print JSON into editor
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert(tk.END, json.dumps(json_data, indent=4))

            self.current_file = file_path
            print(f"Loaded JSON file: {file_path}")

        except (json.JSONDecodeError, OSError) as e:
            messagebox.showerror("Error", f"Failed to open JSON file:\n{e}")

    def save_json(self):
        """Save the edited JSON data back to file."""
        if not self.current_file:
            messagebox.showwarning("Warning", "No file loaded. Use 'Open JSON' first.")
            return

        try:
            json_text = self.text_editor.get("1.0", tk.END).strip()
            json_data = json.loads(json_text)  # Validate JSON

            with open(self.current_file, "w", encoding="utf-8") as file:
                json.dump(json_data, file, indent=4)

            print(f"Saved JSON file: {self.current_file}")
            messagebox.showinfo("Success", "File saved successfully!")

        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Invalid JSON format:\n{e}")

    def reload_json(self):
        """Reload the last opened JSON file."""
        if not self.current_file:
            messagebox.showwarning("Warning", "No file to reload.")
            return

        print(f"Reloading file: {self.current_file}")
        self.open_json()  # Reuse open_json function

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


def save_plot_as_png(dict_global):
    dict_global["fig"].savefig(dict_global["name_png"], bbox_inches="tight")
    print(f"Saved file as {dict_global['name_png']}")


def reset_auto_zoom(dict_global):
    dict_global["auto_zoom"] = not dict_global["auto_zoom"]
    dict_global["auto_zoom_button"].config(
        text=f"Auto Zoom: {dict_global['auto_zoom']}"
    )
    if dict_global["auto_zoom"]:
        set_axis_on_auto_zoom_respecting_user_limits(dict_global)
        dict_global["canvas"].draw()
