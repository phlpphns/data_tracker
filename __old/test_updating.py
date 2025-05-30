import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

# import pandas as pd
# import time

from lib_functions_file_monitoring import (
    convert_time_stamp,
    find_files,
    first_read,
    # gen_yield_line_numbers,
    initial_plot,
    set_axis_on_auto_zoom_respecting_user_limits,
    update_plot,
    # set_gui_elements,
)

dict_global = {}

# Global variables
dict_global["streaming"] = False  # Controls the animation loop
dict_global["json_filepath"] = "./instructions_json.json"  # Default filepath
dict_global["refresh_rate_in_s"] = 1000  # Default filepath
dict_global["user_defined_max_x_threshold"] = 100 / 3600
dict_global["user_defined_max_y_threshold"] = 200
dict_global["auto_zoom"] = True


if not os.path.isfile(""):
    pass


# gen_yield_line = gen_yield_line_numbers()

# print(next(gen_yield_line))
# print(next(gen_yield_line))
# print(next(gen_yield_line))

# print(ieaieiaeaieia)

dict_global[
    "dat_file"
] = r"C:\Users\pkv190\Dropbox\CODES\playground\arianna_monitoring_file\Fri-Mar-07-21-31-13-2025_EDAutoLog\EDAutoLog.dat"

dict_global["keys_of_interest"] = [
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
dict_global["dict_settings"] = dict_settings = {}
dict_internal = {}
dict_internal["name_button_streaming_start"] = ""
dict_internal["name_button_streaming_stop"] = ""

dict_global["name_png"] = "test.png"


first_read(dict_global)
initial_plot(dict_global)

fig = dict_global["fig"]
ax = dict_global["ax"]

import sys
from matplotlib.widgets import Button, TextBox

# def set_gui_elements(dict_global):
if True:
    # Toggle start/stop streaming
    def toggle_csv_stream(event, dict_global=dict_global):
        # global dict_global
        streaming = dict_global["streaming"] = not dict_global["streaming"]
        start_stop_button.label.set_text(
            "Start streaming" if not streaming else "Stop streaming"
        )

    def save_plot_as_png(event, dict_global=dict_global):
        for item in dict_global["figure_buttons"].values():
            item.set_visible(False)
        dict_global['fig'].savefig(dict_global["name_png"], bbox_inches="tight")
        print(f"saved file as {dict_global['name_png']}")
        for item in dict_global["figure_buttons"].values():
            item.set_visible(True)

    # Function to handle JSON file input
    def update_filepath(text, dict_global=dict_global):
        # global dict_global
        dict_global["json_filepath"] = text
        print(f"Filepath updated: {dict_global['json_filepath']}")

    # Function to load JSON (example placeholder)
    def load_json(event):
        global dict_settings
        try:
            with open(json_file, "r") as j:
                dict_settings = json.loads(j.read())
            print(f"Loaded JSON: {dict_settings}")  # Replace with actual processing
        except Exception as e:
            print(f"Error loading JSON: {e}")

    def reset_auto_zoom(event, dict_global=dict_global):
        # global dict_global
        auto_zoom = dict_global["auto_zoom"] = not dict_global["auto_zoom"]
        auto_zoom_button.label.set_text(
            f"{auto_zoom}"
        )  # if not streaming else "Stop streaming")
        if auto_zoom:
            set_axis_on_auto_zoom_respecting_user_limits(dict_global)

    def wrapper_find_files(event, dict_global=dict_global):
        found_files = find_files(
            source_dir=".", starts_with="", contains="", file_ending="EDAutoLog.dat"
        )
        dict_global["dat_file"] = found_files[0]
        print(f"found file {dict_global['dat_file']}")

    def fun_exit_app(event):
        print("exiting")
        sys.exit()

    y_line_upper = 0.15
    y_line_lower = 0.05

    dict_global["figure_buttons"] = {}
    work = dict_global["figure_buttons"]

    fig = dict_global["fig"]

    # Buttons and input fields
    # =============== # ==========================

    ax_textbox_json = fig.add_axes([0.15, y_line_upper, 0.3, 0.075])
    work["ax_textbox_json"] = ax_textbox_json
    text_box_json = TextBox(
        ax_textbox_json, "File: ", initial=dict_global["json_filepath"]
    )
    text_box_json.on_submit(update_filepath)

    # =============== # ==========================

    ax_load_json = fig.add_axes([0.55, y_line_upper, 0.1, 0.075])
    work["ax_load_json"] = ax_load_json
    load_json_button = Button(ax_load_json, "Load JSON")
    load_json_button.on_clicked(load_json)

    # =============== # ==========================

    ax_start_stop = fig.add_axes([0.7, y_line_upper, 0.1, 0.075])  # x, y, width, height
    work["ax_start_stop"] = ax_start_stop
    start_stop_button = Button(ax_start_stop, "Stop")
    start_stop_button.on_clicked(toggle_csv_stream)

    ax_save_png = fig.add_axes([0.825, y_line_upper, 0.1, 0.075])  # x, y, width, height
    work["ax_save_png"] = ax_save_png
    save_png_button = Button(ax_save_png, "Save_as_png")
    save_png_button.on_clicked(save_plot_as_png)

    # =============== # ==========================
    # =============== # ==========================

    ax_textbox_dat_file = fig.add_axes([0.15, y_line_lower, 0.3, 0.075])
    work["ax_textbox_dat_file"] = ax_textbox_dat_file
    textbox_dat_file = TextBox(
        ax_textbox_dat_file, "dat file: ", initial=dict_global["dat_file"]
    )
    textbox_dat_file.on_submit(update_filepath)


    ax_file_search = fig.add_axes([0.55, y_line_lower, 0.1, 0.075])
    work["ax_file_search"] = ax_file_search
    start_file_search_button = Button(ax_file_search, "search newest file")
    start_file_search_button.on_clicked(wrapper_find_files)

    # =============== # ==========================

    ax_auto_zoom = fig.add_axes([0.7, y_line_lower, 0.1, 0.075])  # x, y, width, height
    work["ax_auto_zoom"] = ax_auto_zoom
    auto_zoom_button = Button(
        ax_auto_zoom, f"auto_zoom: {dict_global['auto_zoom']}"
    )
    auto_zoom_button.on_clicked(reset_auto_zoom)


    # =============== # ==========================

    ax_exit_app = fig.add_axes([0.85, y_line_lower, 0.1, 0.075])  # x, y, width, height
    work["ax_exit_app"] = ax_exit_app
    exit_app_button = Button(ax_exit_app, f"exit app")
    exit_app_button.on_clicked(fun_exit_app)

    dict_global["figure_buttons"] = work
    dict_global["fig"] = fig

# set_gui_elements(dict_global)





# # Function to handle JSON file input
# def update_filepath(text, dict_global=dict_global):
#     # global dict_global
#     dict_global["json_filepath"] = text
#     print(f"Filepath updated: {dict_global['json_filepath']}")

# # Function to load JSON (example placeholder)
# def load_json(event):
#     global dict_settings
#     try:
#         with open(json_file, "r") as j:
#             dict_settings = json.loads(j.read())
#         print(f"Loaded JSON: {dict_settings}")  # Replace with actual processing
#     except Exception as e:
#         print(f"Error loading JSON: {e}")

# # def wrapper_find_files(event, dict_global=dict_global):
# #     found_files = find_files(
# #         source_dir=".", starts_with="", contains="", file_ending="EDAutoLog.dat"
# #     )
# #     dict_global["dat_file"] = found_files[0]
# #     print(f"found file {dict_global['dat_file']}")

# def fun_exit_app(event):
#     print("exiting")
#     sys.exit()

# y_line_upper = 0.15
# y_line_lower = 0.05

# dict_global["figure_buttons"] = {}
# work = dict_global["figure_buttons"]

# fig = dict_global["fig"]

# # Buttons and input fields
# # =============== # ==========================

# ax_textbox_json = fig.add_axes([0.15, y_line_upper, 0.3, 0.075])
# work["ax_textbox_json"] = ax_textbox_json
# text_box_json = TextBox(
#     ax_textbox_json, "File: ", initial=dict_global["json_filepath"]
# )
# text_box_json.on_submit(update_filepath)

# # =============== # ==========================

# ax_load_json = fig.add_axes([0.55, y_line_upper, 0.1, 0.075])
# work["ax_load_json"] = ax_load_json
# load_json_button = Button(ax_load_json, "Load JSON")
# load_json_button.on_clicked(load_json)

# =============== # ==========================

# ax_textbox = plt.axes([0.15, 0.05, 0.35, 0.075])
# text_box = TextBox(ax_textbox, "File: ", initial=dict_global['json_filepath'])
# text_box.on_submit(update_filepath)


# =============== # ==========================

# ax_file_search = fig.add_axes([0.55, y_line_lower, 0.1, 0.075])
# work["ax_file_search"] = ax_file_search
# start_file_search_button = Button(ax_file_search, "search newest file")
# start_file_search_button.on_clicked(wrapper_find_files)

# import sys
# ax_exit_app = fig.add_axes([0.85, y_line_lower, 0.1, 0.075])  # x, y, width, height
# work["ax_exit_app"] = ax_exit_app
# exit_app_button = Button(ax_exit_app, f"exit app")
# exit_app_button.on_clicked(fun_exit_app)
# =============== # ==========================

def update_plot_wrapper(frame, dict_global=dict_global):
    return update_plot(frame, dict_global)


ani = animation.FuncAnimation(
    fig, update_plot_wrapper, interval=dict_global["refresh_rate_in_s"], blit=False
)

# plt.tight_layout()
plt.show()


# # Function to reset the plot (zoomed out)
# def reset_zoom(event):
#     global zoomed_in
#     zoomed_in = False
#     ax.set_xlim(df["time"].min(), df["time"].max())  # Reset X limits to the data range
#     ax.set_ylim(
#         df[["value1", "value2"]].min().min(), df[["value1", "value2"]].max().max()
#     )  # Reset Y limits
#     fig.canvas.draw_idle()


# # Function to zoom in (example zoom behavior)
# def zoom_in(event):
#     global zoomed_in
#     if not zoomed_in:
#         zoomed_in = True
#         ax.set_xlim(
#             df["time"][20], df["time"][80]
#         )  # Zoom into a portion of the X range
#         ax.set_ylim(
#             df[["value1", "value2"]].min().min() + 0.5,
#             df[["value1", "value2"]].max().max() - 0.5,
#         )  # Zoom into the Y range
#         fig.canvas.draw_idle()

#     def write_json_file(dict_json, json_name):
#         # formerly: json_name, json_file
#         with open(json_name, "w") as outfile:
#             json.dump(dict_json, outfile, sort_keys=True, indent=4)


def search_files_and_return_youngest():
    pass


def read_standard_json(path_json):
    dict_json = {}
    return dict_json


def return_standard_parameters():
    dict_json = {}
    return dict_json


# write_json_file(dict_global, 'json_test__.json')


"""
import matplotlib.pyplot as plt
import numpy as np
import time

# Create initial data
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.sin(x) * np.cos(x)

# Create figure and axis
fig, ax = plt.subplots()
lines = []  # List to store line objects

# Plot multiple curves and store the line objects
lines.append(ax.plot(x, y1, label="sin(x)")[0])
lines.append(ax.plot(x, y2, label="cos(x)")[0])
lines.append(ax.plot(x, y3, label="sin(x) * cos(x)")[0])

ax.legend()
plt.ion()  # Turn on interactive mode
plt.show()

# Function to update the plots dynamically
def update_plot(new_y_values):
    for line, new_y in zip(lines, new_y_values):
        line.set_ydata(new_y)  # Update Y values of each curve

    fig.canvas.draw_idle()  # Redraw only the updated parts
    fig.canvas.flush_events()  # Ensure updates are visible

# Simulate updates over time
for _ in range(100):
    new_y1 = np.sin(x + np.random.uniform(-0.5, 0.5))
    new_y2 = np.cos(x + np.random.uniform(-0.5, 0.5))
    new_y3 = np.sin(x) * np.cos(x + np.random.uniform(-0.5, 0.5))

    update_plot([new_y1, new_y2, new_y3])
    time.sleep(5)  # Pause to visualize updates
"""


"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Generate an initial DataFrame with dummy data
def create_dataframe():
    time = np.linspace(0, 10, 100)  # Simulated time values
    value1 = np.sin(time)           # First data series
    value2 = np.cos(time)           # Second data series
    return pd.DataFrame({'time': time, 'value1': value1, 'value2': value2})

df = create_dataframe()  # Initialize DataFrame

# Create figure and axes
fig, ax = plt.subplots(figsize=(20, 10))
line1, = ax.plot(df['time'], df['value1'], label="sin(x)", color="r")
line2, = ax.plot(df['time'], df['value2'], label="cos(x)", color="b")
ax.legend()
ax.set_xlabel("Time (s)")
ax.set_ylabel("Values")

# Function to fetch new data and update the plot
def update(frame):
    global df
    # Simulate new data (you can replace this with actual data reading)
    df['value1'] = np.sin(df['time'] + np.random.uniform(-0.5, 0.5))
    df['value2'] = np.cos(df['time'] + np.random.uniform(-0.5, 0.5))

    # Update the plot with new DataFrame values
    line1.set_ydata(df['value1'])
    line2.set_ydata(df['value2'])

    return line1, line2  # Return updated lines

# Run animation: update every 1000ms (1s)
ani = animation.FuncAnimation(fig, update, interval=1000, blit=False)

plt.show()
"""
