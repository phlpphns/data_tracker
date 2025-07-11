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
