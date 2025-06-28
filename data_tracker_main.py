from data_tracker.conversions import time_conversions
from data_tracker.async_elements.loops import start_data_streaming
from data_tracker.data_generators import create_data_generator_real
from data_tracker.gui import (
    create_gui_elements,
    button_function_autosearch_file,
    button_function_load_user_settings,
    # start_data_streaming,
)
from data_tracker.in_and_output.redirecting import RedirectText
from data_tracker.in_and_output.upon_startup import (
    read_file_for_first_time,
    welcome_message_gui,
)
from data_tracker.presets import define_dict_user_settings_jeol
from data_tracker.facades import DataReaderFacade
from data_tracker.testing import create_data_generator_for_testing
import sys
import tkinter as tk
import traceback

from data_tracker.gui.script_prelim_convert_pyside6 import *

if False:
    dict_user_settings = define_dict_user_settings_jeol()

    # dict_user_settings["dict_settings"] = dict_settings = {}

    # dict_internal = {}
    # dict_internal["name_button_streaming_start"] = ""
    # dict_internal["name_button_streaming_stop"] = ""

    dict_global = {}
    dict_global["dict_user_settings_keys"] = list(dict_user_settings.keys())

    dict_global["asyncio_loop"] = None  # asyncio_loop

    # Create Tkinter GUI
    dict_global["root"] = tk.Tk()
    dict_global["root"].title("Live Plot Streaming")
    # dict_global["root"].geometry("800x600")
    # root.title("Adjustable Layout")
    dict_global["root"].geometry("1500x1000")  # Increased size for better visibility
    dict_global["redirect_output"] = None
    dict_global["redirect_error"] = None
    dict_global["gui_elements"] = {}

    dict_global["figsize"] = (8, 6)

    dict_global["threading"] = {}
    dict_global["threading"]["async_loop"] = False
    dict_global["threading"]["loop_running"] = False  # Flag to track loop state

    def _create_data_generator():
        # print("inside _create_data_generator")
        return create_data_generator_real(dict_global)

    dict_global["test_mode"] = True
    # dict_global['test_mode'] = False

    dict_global["function_get_new_data"] = _create_data_generator
    if dict_global["test_mode"]:
        dict_global["function_get_new_data"] = create_data_generator_for_testing()

    # dict_global['dict_global'] = dict_global
    # print(dict_global['dict_global'])
    dict_global["pipe_to_gui"] = True
    # dict_global["pipe_to_gui"] = False
    dict_global = {**dict_global, **dict_user_settings}
    # dict_global['root'] = root
    # create_gui_scaffold(dict_global)
    create_gui_elements(dict_global)
    # if True:
    if dict_global["pipe_to_gui"]:
        if dict_global["redirect_error"]:
            print("standard error redirected")
            sys.stderr = RedirectText(dict_global["redirect_error"])
        if dict_global["redirect_output"]:
            print("standard output redirected")
            sys.stdout = RedirectText(dict_global["redirect_output"])
    welcome_message_gui()
    dict_global["data_reader"] = DataReaderFacade(
        path_user_scripts=[
            r"C:\Users\pkv190\Dropbox\CODES\playground\arianna_monitoring_file\user_scripts"
        ],
    )

    print("sys.argv     ", sys.argv[1:])

    # dict_global['dict_global'] = dict_global

    #    pd.read_csv
    # print(dddd)
    # def load_settings_file(dict_global):
    #     pass
    # load_settings_file(dict_global)
    button_function_load_user_settings(dict_global)
    # dict_global["root"].grid_rowconfigure(0, weight=1)
    # dict_global["root"].grid_columnconfigure(0, weight=1)
    if dict_user_settings["auto_file_search_on_startup"]:
        button_function_autosearch_file(dict_global)
    if dict_user_settings["auto_run_on_startup"]:
        read_file_for_first_time(dict_global)
    if dict_user_settings["streaming"]:
        start_data_streaming(dict_global)
    # Run Tkinter main loop

    dict_global["root"].mainloop()

    # Define Functions
    # def toggle_csv_stream():
    #     dict_global["streaming"] = not dict_global["streaming"]
    #     start_stop_button.config(text="Start streaming" if not dict_global["streaming"] else "Stop streaming")
    # get_new_data

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    main_window.setWindowTitle("Live Plot Streaming (PySide6)") # Changed title
    main_window.setGeometry(100, 100, 1500, 1000) # Matched your desired geometry

    # Initialize dict_global with PySide6 root and other necessary items
    dict_global = {
        "root": main_window, # This is now the QMainWindow
        "main_window": main_window,
        "gui_elements": {},
        "figsize": (10, 6), # Default figsize
        "redirect_output": None, # Will be set later
        "redirect_error": None,  # Will be set later
        "threading": {
            "async_loop": False,
            "loop_running": False
        },
        "test_mode": True, # As per your startup script
        "pipe_to_gui": True, # As per your startup script
        "asyncio_loop": None, # For your asyncio integration
        "data_reader": None, # Will be set later
    }

    # Define user settings using your mock function
    dict_user_settings = define_dict_user_settings_jeol()
    dict_global["dict_user_settings_keys"] = list(dict_user_settings.keys())
    dict_global.update(dict_user_settings) # Merge user settings into dict_global

    def _create_data_generator_wrapper(): # Renamed to avoid conflict if `create_data_generator_real` exists
        return create_data_generator_real(dict_global)

    dict_global["function_get_new_data"] = _create_data_generator_wrapper
    if dict_global["test_mode"]:
        dict_global["function_get_new_data"] = create_data_generator_for_testing()

    # Create GUI elements (this populates dict_global["redirect_output"] and ["redirect_error"])
    create_gui_elements(dict_global)

    # Redirect stdout and stderr if pipe_to_gui is True
    if dict_global["pipe_to_gui"]:
        if dict_global["redirect_error"]:
            print("Standard error redirected to GUI console.")
            sys.stderr = StreamRedirector(dict_global["redirect_error"])
        if dict_global["redirect_output"]:
            print("Standard output redirected to GUI console.")
            sys.stdout = StreamRedirector(dict_global["redirect_output"])
    else:
        print("GUI redirection disabled.") # For debugging if not redirected

    welcome_message_gui() # Your welcome message
    print(f"sys.argv {sys.argv[1:]}") # Print command line args

    dict_global["data_reader"] = DataReaderFacade(
        path_user_scripts=[r"C:\Users\pkv190\Dropbox\CODES\playground\arianna_monitoring_file\user_scripts"]
    )

    button_function_load_user_settings(dict_global) # Load settings after GUI is ready

    if dict_global["auto_file_search_on_startup"]: # Use dict_global, which now contains user settings
        button_function_autosearch_file(dict_global)
    if dict_global["auto_run_on_startup"]:
        read_file_for_first_time(dict_global) # This will now update the plot if elements exist
    if dict_global["streaming"]:
        start_data_streaming(dict_global) # This will now set the streaming flag

    main_window.show() # Show the PySide6 main window

    # Start the PySide6 application event loop
    sys.exit(app.exec())