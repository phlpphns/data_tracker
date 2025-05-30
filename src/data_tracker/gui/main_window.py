#### THIS COULD BE MOVED TO THE MAIN SCRIPT

# blitting - https://stackoverflow.com/questions/57891219/how-to-make-a-fast-matplotlib-live-plot-in-a-pyqt5-gui
# https://www.pythonguis.com/tutorials/plotting-pyqtgraph/
#
#

import tkinter as tk
from tkinter import ttk
from .frame_bottom_panel import configure_bottom_panel
from .frame_figure_panel import configure_figure_panel
from .frame_button_panel import configure_button_panel


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

    add_elements_to_frames(dict_global)


def add_elements_to_frames(dict_global):
    configure_figure_panel(
        dict_global["gui_elements"]["frame_holding_figure"], dict_global
    )
    configure_button_panel(
        dict_global["gui_elements"]["frame_holding_buttons"], dict_global
    )
    configure_bottom_panel(
        dict_global["gui_elements"]["frame_holding_consoles"], dict_global
    )

    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========
    # ======= # ========== # =========== # =========== # ===========
