from ..conversions.time_conversions import convert_time_stamp
from ..plotting.set_lines_in_plot import (
    set_axis_on_auto_zoom_respecting_user_limits,
    update_plot,
)

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from tkinter import ttk
import traceback


def initalize_data_pool():
    pass


def read_file_for_first_time(dict_global):
    try:
        ax = dict_global["ax"]
        # Clear existing lines from the plot
        ax.clear()
        dict_global["lines_in_plot"] = {}

        dat_file = dict_global["dat_file"]
        dict_global["pandas_main_dataframe_read_data"] = pd.DataFrame()

        column_names = (
            dict_global["data_reader"]
            .read(
                file_path=dict_global["dat_file"],
                file_type=dict_global["file_type"],
                delimiter="\t",
                header=1,
                index_col=False,
                nrows=1,
            )
            .columns
        )

        leading_delimiter = dict_global["leading_delimiter"]
        starting_index = 1 if leading_delimiter else 0
        column_names = column_names[starting_index:].tolist()
        dict_global["column_names"] = column_names

        if not dict_global.get("keys_of_interest"):
            dict_global["keys_of_interest"] = column_names

        rows = dict_global["function_get_new_data"]()

        pandas_main_dataframe_read_data = dict_global["data_reader"].read(
            file_path=dict_global["dat_file"],
            file_type=dict_global["file_type"],
            delimiter="\t",
            header=2,
            index_col=False,
            **rows,
        )
        pandas_main_dataframe_read_data.columns = column_names
        dict_global["pandas_main_dataframe_read_data"] = pandas_main_dataframe_read_data

        dict_global["time_reference"] = convert_time_stamp(
            pandas_main_dataframe_read_data, time_reference=None
        )

        plot_for_first_time(dict_global)

    except Exception as e:
        print("error  ", e)
        traceback.print_exc()
        # source_function = func.__name__
        # error_message = f"Error in {source_function}: {e}"


def plot_for_first_time(dict_global):
    refresh_feature_checkboxes(dict_global)
    initialize_tabs(dict_global)
    update_plot(dict_global)


def refresh_feature_checkboxes(dict_global):
    """Refreshes the feature selection checkboxes."""
    frame = dict_global["checkbox_frame"]
    # Clear existing checkboxes using a loop
    for widget in frame.winfo_children():
        widget.destroy()

    columns = dict_global.setdefault("column_names", [])
    selected_features = set(dict_global.setdefault("keys_of_interest", []))
    checkbox_vars = dict_global["checkbox_vars"] = {}

    for feature in columns:
        var = tk.BooleanVar(value=feature in selected_features)
        checkbox = tk.Checkbutton(
            frame,
            text=feature,
            variable=var,
            command=lambda f=feature, v=var: toggle_feature(f, v, dict_global),
        )
        checkbox.pack(anchor="w")
        checkbox_vars[feature] = var

    # initialize_tabs(dict_global)


def initialize_tabs(dict_global):
    for feature in dict_global["keys_of_interest"]:
        add_new_tab_for_plot(feature, dict_global)


def toggle_feature(feature, var, dict_global):
    """Handles checkbox selection/deselection."""
    selected_features = dict_global.setdefault("keys_of_interest", [])
    if var.get():
        if feature not in selected_features:
            selected_features.append(feature)
            add_new_tab_for_plot(feature, dict_global)  # add the tab.
    else:
        if feature in selected_features:
            selected_features.remove(feature)
            remove_tab_for_plot(feature, dict_global)  # remove the tab.

    if not dict_global.get("streaming", False):
        update_plot(dict_global)


def add_new_tab_for_plot(feature, dict_global):
    if "tab_widget" not in dict_global or dict_global["tab_widget"] is None:
        print("Tab widget not initialized.")
        return

    new_tab = tk.Frame(dict_global["tab_widget"], name=f"tab_{feature}")
    fig = plt.Figure(figsize=dict_global["figsize"])
    # fig, ax = plt.subplots(figsize=dict_global['figsize'])
    ax = fig.add_subplot(111)
    df = dict_global["pandas_main_dataframe_read_data"]
    # (line,) = ax.plot([], [])  # Initialize empty line
    # if key not in lines:
    (line,) = ax.plot(df["time"], df[feature], label=feature)
    # lines[key] = line
    canvas = FigureCanvasTkAgg(fig, master=new_tab)
    canvas.get_tk_widget().pack()

    toolbar = NavigationToolbar2Tk(canvas, new_tab)
    toolbar.update()
    toolbar.pack(side=tk.TOP, fill=tk.X)

    dict_global["tab_widget"].add(new_tab, text=feature)
    dict_global["tab_animations"][feature] = (fig, ax, line, canvas)  # [fig, ax]


def remove_tab_for_plot(feature, dict_global):
    if "tab_widget" not in dict_global or dict_global["tab_widget"] is None:
        print("Tab widget not initialized.")
        return

    for tab in dict_global["tab_widget"].tabs():
        if dict_global["tab_widget"].tab(tab, "text") == feature:
            dict_global["tab_widget"].forget(tab)
            if feature in dict_global["tab_animations"]:
                # dict_global["tab_animations"][feature].event_source.stop()
                del dict_global["tab_animations"][feature]
            break


def welcome_message_gui():
    print(
        "Hallo and Welcome to the editor.\
        \nWe have a set of standard parameters that can be saved and changed by reading the respective json file.\
        \nMay the electrons be with you - have fun!!! \n\n\n"
    )
