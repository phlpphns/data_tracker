import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import os


def set_up_plot(dict_global):
    """Creates and embeds a Matplotlib figure inside figure_frame."""
    figure_frame = dict_global["figure_frame"]

    fig, ax = plt.subplots()  # figsize=(3, 2))  # Adjusted default size
    # fig.tight_layout()

    ax.set_xlabel("Time [h]")
    ax.set_ylabel("Value")

    # Embed Matplotlib figure in Tkinter window
    # Create a dedicated frame for the toolbar to avoid conflicts

    canvas = FigureCanvasTkAgg(fig, master=figure_frame)
    canvas.draw()
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=0, column=0, sticky="nsew")

    toolbar_frame = ttk.Frame(figure_frame)
    toolbar_frame.grid(row=1, column=0, sticky="ew")

    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
    toolbar.update()

    dict_global["fig"] = fig
    dict_global["ax"] = ax
    dict_global["canvas"] = canvas
    dict_global["toolbar"] = toolbar


# def create_gui_elements(dict_global):
#     paned_window = dict_global["paned_window"]
#     # figure_frame = dict_global['figure_frame']
#     notebook_frame = dict_global["notebook_frame"]
#     # ======= # ========== # =========== # =========== # ===========
#     # Create Tkinter Controls
#     frame_controls = ttk.Frame(paned_window)
#     paned_window.add(frame_controls)


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


import sys

def adjust_pane_ratios(event=None):
    """Dynamically adjust sash positions while keeping selection_frame height constant."""

    def get_selection_frame_height():
        """Retrieve the automatically assigned height of selection_frame."""
        selection_height = selection_frame.winfo_height()
        if selection_height > 0:
            dict_global["selection_frame_height"] = selection_height
            print(f"Selection Frame Height: {selection_height}")  # Debug output
        else:
            root.after(
                50, get_selection_frame_height
            )  # Retry after 50ms if height is not available

    # Schedule retrieval after UI is drawn
    # root.after(100,
    # get_selection_frame_height()

    total_height = root.winfo_height()
    # selection_height = selection_frame.winfo_height()
    selection_height = dict_global.get("selection_frame_height", 0)
    # selection_height = selection_frame.winfo_height()

    if selection_height > 0:
        paned_window.sashpos(0, int(total_height * 0.67))  # Adjust Figure frame
        paned_window.sashpos(
            1, paned_window.sashpos(0) + selection_height
        )  # Keep selection_frame fixed

def adjust_pane_ratios(event=None):
    """Dynamically adjust sash positions to maintain height ratios."""
    total_height = root.winfo_height()
    paned_window.sashpos(0, int(total_height * 0.67))  # 67% to figure_frame
    paned_window.sashpos(
        1, int(total_height * 0.73)
    )  # 13% to selection_frame, 20% to bottom_frame

def create_gui_elements(dict_global):
    # dict_global["root"] = tk.Tk()
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


    dict_global["paned_window"] = paned_window
    dict_global["figure_frame"] = figure_frame
    dict_global["selection_frame"] = selection_frame
    dict_global["bottom_frame"] = bottom_frame

    configure_output_panel(dict_global['bottom_frame'])
    configure_button_panel(dict_global["selection_frame"])

    # Setup the plot
    set_up_plot(dict_global)

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


class RedirectText:
    """Class to redirect print output to a Tkinter Text widget."""

    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)  # Auto-scroll

    def flush(self):
        pass  # Required for compatibility with sys.stdout


# def configure_button_panel(selection_frame):
#     # toolbar_frame = ttk.Frame(selection_frame)
#     # # ======== # ======= # =======
#     # toolbar_frame.grid(row=0, column=0, sticky="nsew")
#     frame_controls = selection_frame

#     for i in range(7):  # Adjust range based on max columns used
#         frame_controls.columnconfigure(i, weight=0)  # Keep buttons compact
#     # frame_controls.columnconfigure(2, weight=1, uniform="group2")  # Allow file paths to expand

#     # ======= # ========== # =========== # =========== # ===========
#     # dat_file Filepath Entry
#     ttk.Label(frame_controls, text="File:").grid(
#         row=0, column=1, padx=5, pady=5, sticky="w"
#     )
#     entry_dat_filepath = ttk.Entry(frame_controls, width=50)
#     entry_dat_filepath.insert(0, dict_global["dat_file"])
#     entry_dat_filepath.grid(row=0, column=2, padx=5, pady=5, sticky="w")
#     dict_global["entry_dat_filepath"] = entry_dat_filepath
#     # ======= # ========== # =========== # =========== # ===========
#     # Update Filepath Button
#     update_filepath_button = ttk.Button(
#         frame_controls,
#         text="autosearch file",
#         command=lambda: wrapper_find_files(dict_global),
#     )
#     update_filepath_button.grid(row=0, column=3, padx=5, pady=5, sticky="w")
#     dict_global["update_filepath_button"] = update_filepath_button

#     # ======= # ========== # =========== # =========== # ===========
#     # Start/Stop Button
#     read_fresh_file_button = ttk.Button(
#         frame_controls,
#         text="Read a fresh file",
#         command=lambda: read_fresh_file(dict_global),
#     )  # partial(bread_fresh_file, dict_global))
#     read_fresh_file_button.grid(row=0, column=4, padx=5, pady=5, sticky="w")
#     dict_global["read_fresh_file_button"] = read_fresh_file_button

#     # ======= # ========== # =========== # =========== # ===========
#     # Auto Zoom Button
#     auto_zoom_button = ttk.Button(
#         frame_controls,
#         text=f"Auto Zoom: {dict_global['auto_zoom']}",
#         command=lambda: reset_auto_zoom(dict_global),
#     )
#     auto_zoom_button.grid(row=0, column=5, padx=5, pady=5, sticky="w")
#     dict_global["auto_zoom_button"] = auto_zoom_button

#     # ======= # ========== # =========== # =========== # ===========
#     # Start/Stop Streaming Button
#     btn_start_stop = ttk.Button(
#         frame_controls,
#         text="Start Streaming",
#         command=lambda: toggle_csv_stream(dict_global),
#     )
#     btn_start_stop.grid(row=0, column=6, padx=5, pady=5, sticky="w")
#     dict_global["btn_start_stop"] = btn_start_stop

#     # ======= # ========== # =========== # =========== # ===========
#     # Exit Button
#     exit_button = ttk.Button(
#         frame_controls, text="Exit", command=lambda: fun_exit_app(dict_global)
#     )
#     exit_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")

#     # ======= # ========== # =========== # =========== # ===========
#     # JSON Filepath Entry
#     ttk.Label(frame_controls, text="File:").grid(
#         row=1, column=1, padx=5, pady=5, sticky="w"
#     )

#     # Use StringVar for dynamic updates
#     json_filepath_var = tk.StringVar(value=dict_global["json_filepath"])
#     entry_json_filepath = ttk.Entry(
#         frame_controls, width=40, textvariable=json_filepath_var
#     )
#     # entry_json_filepath.grid(row=1, column=1, padx=5, pady=5)
#     entry_json_filepath.grid(row=1, column=2, padx=5, pady=5, sticky="w")

#     dict_global["entry_json_filepath"] = entry_json_filepath

#     # Use StringVar for dynamic updates
#     json_filepath_var = tk.StringVar(value=dict_global["json_filepath"])

#     entry_json_filepath = ttk.Entry(
#         frame_controls, width=50, textvariable=json_filepath_var
#     )
#     entry_json_filepath.grid(row=1, column=2, padx=5, pady=5, sticky="w")

#     def update_json_filepath(event=None):
#         """Update dict_global when the user enters a new file path."""
#         new_path = json_filepath_var.get().strip().strip('"')
#         if new_path:
#             dict_global["json_filepath"] = new_path
#             print(f"Updated file path: {dict_global['json_filepath']}")
#             # open_json(new_path)

#     # Bind "Enter" key to update the file path
#     entry_json_filepath.bind("<Return>", update_json_filepath)

#     # ======= # ========== # =========== # =========== # ===========
#     # Load JSON Button
#     load_json_button = ttk.Button(
#         frame_controls,
#         text="Load user settings",
#         command=lambda: wrapper_load_json_gui(dict_global),
#     )
#     load_json_button.grid(row=1, column=3, padx=5, pady=5, sticky="w")
#     dict_global["load_json_button"] = load_json_button

#     save_json_button = ttk.Button(
#         frame_controls,
#         text="save user settings",
#         command=lambda: wrapper_load_json_gui(dict_global),
#     )
#     save_json_button.grid(row=1, column=4, padx=5, pady=5, sticky="w")
#     dict_global["save_json_button"] = save_json_button

#     # ======= # ========== # =========== # =========== # ===========
#     # Save as PNG Button
#     save_png_button = ttk.Button(
#         frame_controls,
#         text="Save as PNG",
#         command=lambda: save_plot_as_png(dict_global),
#     )
#     save_png_button.grid(row=1, column=5, padx=5, pady=5)
#     dict_global["save_png_button"] = save_png_button


# def configure_output_panel(bottom_frame, dict_global):
#     pass

#     def configure_editors_panel():
#         pass

#     # Create PanedWindow to hold both notebooks
#     # bottom_frame.grid(row=1, column=0, sticky="nsew")  # Fill all available space

#     bottom_paned = ttk.PanedWindow(bottom_frame, orient=tk.HORIZONTAL)
#     bottom_paned.grid(row=0, column=0, sticky="nsew")  # Expand fully

#     # Configure bottom_paned to expand
#     bottom_paned.columnconfigure(0, weight=1)
#     bottom_paned.columnconfigure(1, weight=1)

#     # === Left Notebook Frame ===
#     left_notebook_frame = ttk.Frame(bottom_paned, borderwidth=2, relief="sunken")
#     bottom_paned.add(left_notebook_frame, weight=1)  # Set weight for resizing

#     # Ensure the left notebook frame expands
#     left_notebook_frame.columnconfigure(0, weight=1)
#     left_notebook_frame.rowconfigure(0, weight=1)

#     left_notebook = ttk.Notebook(left_notebook_frame)
#     left_notebook.grid(row=0, column=0, sticky="nsew")  # Fill all available space

#     # left_notebook_frame

#     # Left Editor Tab
#     left_text_editor_frame = ttk.Frame(left_notebook)
#     left_notebook.add(left_text_editor_frame, text="Left Editor")

#     # Text editor inside left notebook
#     left_text_editor = tk.Text(left_text_editor_frame, wrap="word")
#     left_text_editor.pack(fill=tk.BOTH, expand=True)

#     # # === Tab 1: Text Editor ===
#     # output_frame = ttk.Frame(notebook)
#     # notebook.add(output_frame, text="Output")

#     # output_text = tk.Text(output_frame, wrap="word", state="normal")
#     # output_text.pack(expand=True, fill="both")

#     # === Right Notebook Frame ===
#     right_notebook_frame = ttk.Frame(bottom_paned, borderwidth=2, relief="sunken")
#     bottom_paned.add(right_notebook_frame, weight=1)

#     # Ensure the right notebook frame expands
#     right_notebook_frame.columnconfigure(0, weight=1)
#     right_notebook_frame.rowconfigure(0, weight=1)

#     right_notebook = ttk.Notebook(right_notebook_frame)
#     right_notebook.grid(row=0, column=0, sticky="nsew")  # Fill all available space

#     # Right Editor Tab
#     another_frame = ttk.Frame(right_notebook)
#     right_notebook.add(another_frame, text="Another Tab")

#     # Configure another_frame to expand
#     another_frame.columnconfigure(0, weight=1)
#     another_frame.columnconfigure(1, weight=1)
#     another_frame.columnconfigure(2, weight=1)
#     another_frame.rowconfigure(1, weight=1)

#     # Buttons inside right notebook
#     button_frame = ttk.Frame(another_frame)
#     button_frame.grid(row=0, column=0, columnspan=3, sticky="ew")

#     ttk.Button(button_frame, text="Open JSON", command=hallo).grid(
#         row=0, column=0, sticky="nsew", padx=5, pady=2
#     )
#     ttk.Button(button_frame, text="Save JSON", command=hallo).grid(
#         row=0, column=1, sticky="nsew", padx=5, pady=2
#     )
#     ttk.Button(button_frame, text="Reload", command=hallo).grid(
#         row=0, column=2, sticky="nsew", padx=5, pady=2
#     )

#     # Text editor inside right notebook
#     text_editor = tk.Text(another_frame, wrap="word")
#     text_editor.grid(row=1, column=0, columnspan=3, sticky="nsew")

#     right_text_editor_frame = ttk.Frame(right_notebook)
#     right_notebook.add(right_text_editor_frame, text="Right Editor")

#     # Create buttons and place them inside the button_frame
#     ttk.Button(right_text_editor_frame, text="Open JSON").grid(
#         row=0, column=0, padx=5, pady=2
#     )
#     ttk.Button(right_text_editor_frame, text="Save JSON").grid(
#         row=0, column=1, padx=5, pady=2
#     )
#     ttk.Button(right_text_editor_frame, text="Reload").grid(
#         row=0, column=2, padx=5, pady=2
#     )

#     # Configure another_frame to expand
#     another_frame.columnconfigure(0, weight=1)
#     another_frame.columnconfigure(1, weight=1)
#     another_frame.columnconfigure(2, weight=1)
#     another_frame.rowconfigure(1, weight=1)

#     dict_global["right_text_editor"] = tk.Text(right_text_editor_frame, wrap="word")
#     dict_global["right_text_editor"].grid(
#         row=1, column=0, columnspan=3, sticky="nsew"
#     )
#     # pack(fill=tk.BOTH, expand=True)

#     # Redirect print statements to Output Window
#     sys.stdout = RedirectText(left_text_editor)

def hallo():
    pass

# Global dictionary for UI elements
dict_global = {}

dict_global = {}


dict_global["name_png"] = "iaetrnaieiatrn.png"
dict_global["dat_file"] = ""
dict_global["auto_zoom"] = ""
dict_global["json_filepath"] = ""


# Initialize Tkinter
dict_global["root"] = tk.Tk()
dict_global["root"].title("Live Plot Streaming")
# dict_global["root"].geometry("800x600")

# dict_global = {**dict_global, **dict_user_settings}
# dict_global['root'] = root
# initial_frames(dict_global)
# dict_global["root"].grid_rowconfigure(0, weight=1)
# dict_global["root"].grid_columnconfigure(0, weight=1)
# create_gui_elements(dict_global)
# set_up_plot(dict_global)
# first_read(dict_global)
# initial_plot(dict_global)
# # Run Tkinter main loop


# separate in dict_global (internal) and dict_user_settings?
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
dict_user_settings["dict_settings"] = dict_settings = {}

dict_internal = {}
dict_internal["name_button_streaming_start"] = ""
dict_internal["name_button_streaming_stop"] = ""

dict_user_settings["name_png"] = "test.png"
dict_user_settings["streaming"] = False  # Controls the animation loop
dict_user_settings["json_filepath"] = "./instructions_json.json"  # Default filepath
# dict_user_settings["json_filepath"] = r"C:\Users\pkbv190\Dropbox\CODES\playground\arianna_monitoring_file\instructions_json - Copy.json"
# Global Dictionary for Settings
dict_user_settings["refresh_rate_in_s"] = 100  # Default filepath
dict_user_settings["user_defined_max_x_threshold"] = 100 / 3600
dict_user_settings["user_defined_max_y_threshold"] = 200
dict_user_settings["auto_zoom"] = True
dict_user_settings["root_dir_data_files"] = "."
dict_user_settings["pattern_auto_file_search"] = "EDAutoLog.dat"

# read user settings from a json file (try!)
# dict_user_settings[
#     "dat_file"
# ] = r"C:\Users\pkv190\Dropbox\CODES\playground\arianna_monitoring_file\Fri-Mar-07-21-31-13-2025_EDAutoLog\EDAutoLog.dat"

dict_user_settings["dat_file"] = r"./test.dat"

dict_global = {**dict_global, **dict_user_settings}


# from lib_functions_file_monitoring import *
# create_gui_elements(dict_global)
dict_global["root"].mainloop()


# =============   ###


# import tkinter as tk
# from tkinter import ttk

# root = tk.Tk()
# root.title("Tkinter Notebook Example")
# root.geometry("800x600")

# # Configure root grid
# root.columnconfigure(0, weight=1)
# root.rowconfigure(0, weight=1)

# # Create a PanedWindow
# paned_window = ttk.PanedWindow(root, orient=tk.VERTICAL)
# paned_window.grid(row=0, column=0, sticky="nsew")

# # Create a Frame for the Notebook
# notebook_frame = ttk.Frame(paned_window, relief="sunken", borderwidth=2)
# paned_window.add(notebook_frame)

# notebook_frame2 = ttk.Frame(paned_window, relief="sunken", borderwidth=2)
# paned_window.add(notebook_frame2)


# # Configure notebook_frame grid layout
# notebook_frame.columnconfigure(0, weight=1)
# notebook_frame.rowconfigure(0, weight=1)

# # Create Notebook inside the frame
# notebook = ttk.Notebook(notebook_frame)
# notebook.grid(row=1, column=1, sticky="nsew")

# # === Tab 1: Output ===
# output_frame = ttk.Frame(notebook)
# notebook.add(output_frame, text="Output")

# # === Tab 2: Another Tab ===
# another_frame = ttk.Frame(notebook)
# notebook.add(another_frame, text="Another Tab")


# # Configure notebook_frame grid layout
# notebook_frame2.columnconfigure(0, weight=1)
# notebook_frame2.rowconfigure(0, weight=1)

# # Create Notebook inside the frame
# notebook = ttk.Notebook(notebook_frame2)
# notebook.grid(row=0, column=0, sticky="nsew")

# # === Tab 1: Output ===
# output_frame = ttk.Frame(notebook)
# notebook.add(output_frame, text="Output")

# # === Tab 2: Another Tab ===
# another_frame = ttk.Frame(notebook)
# notebook.add(another_frame, text="Another Tab")

# text_editor = tk.Text(another_frame, wrap="word")
# text_editor.grid(row=1, column=0, columnspan=3)#expand=True, fill="both")


# text_editor_frame = ttk.Frame(notebook)
# notebook.add(text_editor_frame, text="Text Editor")

# text_editor = tk.Text(text_editor_frame, wrap="word")
# text_editor.grid(row=1, column=0, columnspan=3)#expand=True, fill="both")


# def hallo():
#     pass

# ttk.Button(another_frame, text="Open JSON", command=hallo).grid(row=0, column=0, sticky="nsew")#grid(side="left", padx=5, pady=2)
# ttk.Button(another_frame, text="Save JSON", command=hallo).grid(row=0, column=1, sticky="nsew")#pack(side="left", padx=5, pady=2)
# ttk.Button(another_frame, text="Reload", command=hallo).grid(row=0, column=2, sticky="nsew")#pack(side="left", padx=5, pady=2)

# ttk.Button(text_editor_frame, text="Open JSON", command=hallo).grid(row=0, column=0, sticky="nsew")#grid(side="left", padx=5, pady=2)
# ttk.Button(text_editor_frame, text="Save JSON", command=hallo).grid(row=0, column=1, sticky="nsew")#pack(side="left", padx=5, pady=2)
# ttk.Button(text_editor_frame, text="Reload", command=hallo).grid(row=0, column=2, sticky="nsew")#pack(side="left", padx=5, pady=2)


# root.mainloop()
