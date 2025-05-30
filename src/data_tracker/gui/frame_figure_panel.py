# https://discourse.matplotlib.org/t/pure-matplotlib-implementation-of-crosshair-cursor-with-hovering-date-labels/22545

import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# from plotting.set_lines_in_plot import set_axis_on_auto_zoom_respecting_user_limits


def configure_figure_panel(frame_holding_figure, dict_global):
    """Creates and embeds a Matplotlib figure inside the frame_holding_figure with dynamic feature selection."""

    upper_paned = ttk.PanedWindow(frame_holding_figure, orient=tk.HORIZONTAL)
    upper_paned.grid(row=0, column=0, sticky="nsew")  # Expand fully

    # Left Pane: Holds the figure and tabs
    left_pane = ttk.Frame(upper_paned, borderwidth=2, relief="sunken")
    upper_paned.add(left_pane, weight=5)

    # Right Pane: Holds feature checkboxes
    right_pane = ttk.Frame(upper_paned, borderwidth=2, relief="sunken")
    upper_paned.add(right_pane, weight=1)

    # Store right pane in dict_global for dynamic access
    dict_global["checkbox_frame"] = right_pane

    # Create the tab widget inside the left pane.
    dict_global["tab_widget"] = ttk.Notebook(left_pane)
    dict_global["tab_widget"].pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Create the main tab for the main plot
    main_tab = ttk.Frame(dict_global["tab_widget"])
    dict_global["tab_widget"].add(main_tab, text="Main Plot")

    # dict_global["tab_widget"].grid_rowconfigure(0, weight=1)
    # dict_global["tab_widget"].grid_columnconfigure(0, weight=1)

    # Create Matplotlib Figure
    plt.style.use('ggplot')
    # plt.tight_layout()
    fig, ax = plt.subplots(figsize=dict_global['figsize'])
    ax.tick_params(axis='x', labelrotation=45)
    dict_global["fig"] = fig
    dict_global["ax"] = ax
    dict_global["ax"].set_xlabel("Time [h]")
    dict_global["ax"].set_ylabel("Value")

    # Embed Figure in Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=main_tab)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Add Matplotlib toolbar
    toolbar = NavigationToolbar2Tk(canvas, main_tab)
    toolbar.update()
    toolbar.pack(side=tk.TOP, fill=tk.X)

    # Store references
    dict_global["canvas"] = canvas
    dict_global["toolbar"] = toolbar
    dict_global["tab_animations"] = {} #initialize.
