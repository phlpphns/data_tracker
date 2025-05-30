from ..editors.text_editors import *

import tkinter as tk
from tkinter import ttk

def configure_bottom_panel(frame_holding_consoles, dict_global):
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

        # Ensure the notebook frame expands
        right_notebook_paned_frame.rowconfigure(0, weight=1)
        right_notebook_paned_frame.columnconfigure(0, weight=1)

        # === Right Editor Tab ===
        right_side_json_editor_frame = ttk.Frame(right_notebook)
        right_notebook.add(right_side_json_editor_frame, text="JSON Editor")

        # JSON Text Editor
        json_text_editor = tk.Text(
            right_side_json_editor_frame, wrap="word", font=("Courier", 10)
        )
        json_text_editor.grid(
            row=0, column=0, columnspan=3, sticky="nsew"
        )  # Expand in all directions

        # Buttons
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

        # Ensure the text editor expands inside the tab
        right_side_json_editor_frame.rowconfigure(0, weight=1)
        right_side_json_editor_frame.columnconfigure(0, weight=1)

        # === Tab 2: Text Editor ===
        right_side_text_editor_frame = ttk.Frame(right_notebook)
        right_notebook.add(right_side_text_editor_frame, text="Note pad - append mode")

        # Text Editor
        text_editor = tk.Text(
            right_side_text_editor_frame, wrap="word", font=("Courier", 10)
        )
        text_editor.grid(row=0, column=0, columnspan=3, sticky="nsew")  # Expand fully

        # Buttons
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

        # Ensure the text editor expands inside the tab
        right_side_text_editor_frame.rowconfigure(0, weight=1)
        right_side_text_editor_frame.columnconfigure(0, weight=1)

    # ========= # ======= # =======
    # ========= # ======= # =======
    # ========= # ======= # =======
    # ========= # ======= # =======
