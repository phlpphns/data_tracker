import sys
import os
import json
import traceback
import time

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QSplitter, QTabWidget, QLabel, QLineEdit,
    QPushButton, QTextEdit, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextOption

# Correct Matplotlib backend import for PySide6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
import matplotlib.pyplot as plt

# --- Mocking your data_tracker imports ---
# YOU WILL REPLACE THESE WITH YOUR ACTUAL IMPORTS AND LOGIC
# Example: from data_tracker.conversions import time_conversions
# Example: from data_tracker.async_elements.loops import start_data_streaming
# Example: from data_tracker.data_generators import create_data_generator_real, create_data_generator_for_testing
# Example: from data_tracker.gui import create_gui_elements, button_function_autosearch_file, button_function_load_user_settings
# Example: from data_tracker.in_and_output.redirecting import RedirectText as YourRedirectTextClass
# Example: from data_tracker.in_and_output.upon_startup import read_file_for_first_time, welcome_message_gui
# Example: from data_tracker.presets import define_dict_user_settings_jeol
# Example: from data_tracker.facades import DataReaderFacade

class MockFunctions:
    def read_file_for_first_time(dict_global):
        print("Mock: read_file_for_first_time called. Reading a fresh file...")
        if "ax" in dict_global and "canvas" in dict_global:
            dict_global["ax"].clear()
            dict_global["ax"].plot([5, 4, 3, 2, 1], [1, 2, 3, 4, 5], 'x--', label="Fresh Mock Data")
            dict_global["ax"].set_xlabel("Time [h]")
            dict_global["ax"].set_ylabel("Value")
            dict_global["ax"].legend()
            dict_global["canvas"].draw()
            print("Mock: Plot updated with fresh data.")
        else:
            print("Mock: Plot elements not yet available in dict_global for update.")

    def button_function_autosearch_file(dict_global):
        print("Mock: button_function_autosearch_file called. Autosearching file...")
        dict_global["dat_file"] = "mock_autosearched_file_pyqt.dat"
        if "text_input_entry_dat_filepath" in dict_global["gui_elements"]:
            text_input_entry = dict_global["gui_elements"]["text_input_entry_dat_filepath"]
            text_input_entry.setText(dict_global["dat_file"])
            print(f"Mock: Updated file path to {dict_global['dat_file']}")
        else:
            print("Mock: GUI element for file path not found.")

    def button_function_load_user_settings(dict_global):
        print("Mock: button_function_load_user_settings called. Loading user settings...")
        mock_settings = {
            "root_dir_data_files": "C:\\Mock\\PyQt_Log",
            "streaming": True,
            "auto_zoom": False,
            "json_filepath": "mock_loaded_settings.json",
            "auto_file_search_on_startup": True, # Ensure these mock settings are reflected
            "auto_run_on_startup": True,
        }
        dict_global.update(mock_settings)
        print(f"Mock: Loaded settings: {json.dumps(mock_settings, indent=4)}")
        # Update UI elements that depend on loaded settings
        if "gui_elements" in dict_global:
            if "auto_zoom_button" in dict_global["gui_elements"]:
                dict_global["gui_elements"]["auto_zoom_button"].setText(f"Auto Zoom: {dict_global['auto_zoom']}")
            if "button_switch_streaming" in dict_global["gui_elements"]:
                dict_global["gui_elements"]["button_switch_streaming"].setText(f"Streaming: {dict_global['streaming']}")
            if "file_path_input_entry_json_filepath" in dict_global["gui_elements"]:
                dict_global["gui_elements"]["file_path_input_entry_json_filepath"].setText(dict_global["json_filepath"])
        else:
            print("Mock: GUI elements not yet available for update from loaded settings.")


    def button_function_save_user_settings(dict_global):
        print("Mock: button_function_save_user_settings called. Saving user settings...")
        dict_user_settings = {
            key: dict_global[key] for key in dict_global.get("dict_user_settings_keys", [])
        }
        print(f"Mock: Saved settings: {json.dumps(dict_user_settings, indent=4)}")

    def button_function_exit_app(dict_global):
        print("Mock: button_function_exit_app called. Exiting application.")
        QApplication.instance().quit()

    def button_function_reset_auto_zoom(dict_global):
        print("Mock: button_function_reset_auto_zoom called.")
        dict_global["auto_zoom"] = not dict_global["auto_zoom"]
        if "auto_zoom_button" in dict_global["gui_elements"]:
            dict_global["gui_elements"]["auto_zoom_button"].setText(
                f"Auto Zoom: {dict_global['auto_zoom']}"
            )
        if dict_global["auto_zoom"]:
            print("Mock: Applying auto zoom.")
            if "ax" in dict_global and "canvas" in dict_global:
                dict_global["ax"].autoscale_view(True,True,True)
                dict_global["canvas"].draw()
        else:
            print("Mock: Auto zoom disabled.")

    def button_function_save_plot_as_png(dict_global):
        print("Mock: button_function_save_plot_as_png called.")
        timestr = time.strftime("%Y%m%d_%H%M%S")
        png_name = dict_global.get("name_png", "plot.png")
        a, b = os.path.splitext(png_name)
        png_name = f"{a}_{timestr}{b}"
        dict_global["fig"].savefig(png_name, bbox_inches="tight")
        print(f"Mock: Saved file as {png_name}")

    def button_function_toggle_csv_stream(dict_global):
        print("Mock: button_function_toggle_csv_stream called.")
        dict_global["streaming"] = not dict_global["streaming"]
        if "button_switch_streaming" in dict_global["gui_elements"]:
            dict_global["gui_elements"]["button_switch_streaming"].setText(
                "Start Streaming" if not dict_global["streaming"] else "Stop Streaming"
            )
        if dict_global["streaming"]:
            print("Mock: Starting data streaming.")
            MockClasses.start_data_streaming(dict_global) # Call mock streaming
        else:
            print("Mock: Stopping data streaming.")

    class JsonEditorFunctions:
        def open_json(text_editor_widget):
            print("Mock: Opening JSON file...")
            mock_json_content = json.dumps({"project": "my_app", "version": "1.0", "settings": {"theme": "dark", "loglevel": "info"}}, indent=4)
            text_editor_widget.setPlainText(mock_json_content)
            print("Mock: JSON content loaded into editor.")

        def save_json(text_editor_widget):
            print("Mock: Saving JSON file...")
            content = text_editor_widget.toPlainText()
            try:
                json_data = json.loads(content)
                print(f"Mock: JSON content saved: {json.dumps(json_data, indent=4)}")
            except json.JSONDecodeError:
                print("Mock Error: Invalid JSON format. Please correct the JSON in the editor.")

        def reload_json(text_editor_widget):
            print("Mock: Reloading JSON (re-opening previous mock for now)...")
            MockFunctions.JsonEditorFunctions.open_json(text_editor_widget)

    class TextEditorFunctions:
        def open_text_file(text_editor_widget):
            print("Mock: Opening text file...")
            mock_text_content = "This is some mock text for the notepad.\nLine 2.\nLine 3, with some more words to test wrapping."
            text_editor_widget.setPlainText(mock_text_content)
            print("Mock: Text content loaded into editor.")

        def save_text_file(text_editor_widget):
            print("Mock: Saving text file...")
            content = text_editor_widget.toPlainText()
            print(f"Mock: Text content saved: {content[:50]}...")

        def reload_text_file(text_editor_widget):
            print("Mock: Reloading text file (re-opening previous mock for now)...")
            MockFunctions.TextEditorFunctions.open_text_file(text_editor_widget)

class MockClasses:
    # Mimic your module structure
    class time_conversions:
        @staticmethod
        def convert_time(value):
            print(f"Mock: time_conversions.convert_time called with {value}")
            return value * 2 # Mock conversion

    class async_elements:
        class loops:
            @staticmethod
            def start_data_streaming(dict_global):
                print("Mock: start_data_streaming called. (In a real app, this would start your async loop)")
                dict_global["threading"]["loop_running"] = True # Set flag in mock
                print(f"Mock: Streaming status: {dict_global['streaming']}, Loop running: {dict_global['threading']['loop_running']}")

    class data_generators:
        @staticmethod
        def create_data_generator_real(dict_global):
            print("Mock: create_data_generator_real called.")
            return lambda: "real_data_mock" # Return a mock callable

        @staticmethod
        def create_data_generator_for_testing():
            print("Mock: create_data_generator_for_testing called.")
            return lambda: "test_data_mock" # Return a mock callable

    class in_and_output:
        class redirecting:
            # Our StreamRedirector will serve this purpose
            pass
        class upon_startup:
            @staticmethod
            def read_file_for_first_time(dict_global):
                print("Mock: upon_startup.read_file_for_first_time called.")
                MockFunctions.read_file_for_first_time(dict_global) # Use the same logic
            @staticmethod
            def welcome_message_gui():
                print("Mock: welcome_message_gui called. Welcome to the PySide6 app!")

    class presets:
        @staticmethod
        def define_dict_user_settings_jeol():
            print("Mock: define_dict_user_settings_jeol called.")
            return {
                "dat_file": "initial_mock_data.dat",
                "json_filepath": "initial_user_settings.json",
                "streaming": False,
                "auto_zoom": True,
                "name_png": "initial_plot.png",
                "auto_file_search_on_startup": True,
                "auto_run_on_startup": False, # Changed to False for initial testing of behavior
                "root_dir_data_files": "C:\\Mock\\Default"
            }

    class facades:
        class DataReaderFacade:
            def __init__(self, path_user_scripts):
                print(f"Mock: DataReaderFacade initialized with paths: {path_user_scripts}")
            def some_method(self):
                print("Mock: DataReaderFacade some_method called.")

# Assign mock functions/classes to global scope as per your original script
json_editor_functions = MockFunctions.JsonEditorFunctions()
text_editor_functions = MockFunctions.TextEditorFunctions()

# Your original functions that are now mapped to mocks
button_function_autosearch_file = MockFunctions.button_function_autosearch_file
button_function_load_user_settings = MockFunctions.button_function_load_user_settings
button_function_save_user_settings = MockFunctions.button_function_save_user_settings
button_function_exit_app = MockFunctions.button_function_exit_app
button_function_reset_auto_zoom = MockFunctions.button_function_reset_auto_zoom
button_function_save_plot_as_png = MockFunctions.button_function_save_plot_as_png
button_function_toggle_csv_stream = MockFunctions.button_function_toggle_csv_stream
read_file_for_first_time = MockClasses.in_and_output.upon_startup.read_file_for_first_time
welcome_message_gui = MockClasses.in_and_output.upon_startup.welcome_message_gui
define_dict_user_settings_jeol = MockClasses.presets.define_dict_user_settings_jeol
start_data_streaming = MockClasses.async_elements.loops.start_data_streaming
create_data_generator_real = MockClasses.data_generators.create_data_generator_real
create_data_generator_for_testing = MockClasses.data_generators.create_data_generator_for_testing
DataReaderFacade = MockClasses.facades.DataReaderFacade # Keep the class directly

# The `create_gui_elements` function is defined below in the PySide6 specific part.
# --- End Mocking ---


# --- PySide6 GUI Configuration Functions (mostly unchanged from last iteration) ---

def configure_figure_panel(frame_holding_figure, dict_global):
    """Creates and embeds a Matplotlib figure inside the frame_holding_figure with dynamic feature selection."""

    if not frame_holding_figure.layout():
        figure_panel_layout = QVBoxLayout(frame_holding_figure)
    else:
        figure_panel_layout = frame_holding_figure.layout()

    upper_splitter = QSplitter(Qt.Horizontal)
    figure_panel_layout.addWidget(upper_splitter)

    left_pane = QFrame()
    left_pane.setFrameShape(QFrame.Shape.StyledPanel)
    left_pane.setFrameShadow(QFrame.Shadow.Sunken)
    left_layout = QVBoxLayout(left_pane)
    upper_splitter.addWidget(left_pane)
    upper_splitter.setStretchFactor(0, 5)

    right_pane = QFrame()
    right_pane.setFrameShape(QFrame.Shape.StyledPanel)
    right_pane.setFrameShadow(QFrame.Shadow.Sunken)
    right_layout = QVBoxLayout(right_pane)
    upper_splitter.addWidget(right_pane)
    upper_splitter.setStretchFactor(1, 1)

    dict_global["checkbox_frame"] = right_pane

    tab_widget = QTabWidget()
    left_layout.addWidget(tab_widget)
    dict_global["tab_widget"] = tab_widget

    main_tab = QWidget()
    tab_widget.addTab(main_tab, "Main Plot")
    main_tab_layout = QVBoxLayout(main_tab)

    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=dict_global['figsize'])
    ax.tick_params(axis='x', labelrotation=45)
    dict_global["fig"] = fig
    dict_global["ax"] = ax
    dict_global["ax"].set_xlabel("Time [h]")
    dict_global["ax"].set_ylabel("Value")

    canvas = FigureCanvasQTAgg(fig)
    main_tab_layout.addWidget(canvas)

    toolbar = NavigationToolbar2QT(canvas, main_tab)
    main_tab_layout.addWidget(toolbar)

    dict_global["canvas"] = canvas
    dict_global["toolbar"] = toolbar
    dict_global["tab_animations"] = {}


def configure_button_panel(frame_holding_buttons, dict_global):
    button_layout = QGridLayout(frame_holding_buttons)

    # Row 0
    button_layout.addWidget(QLabel("File:"), 0, 1, alignment=Qt.AlignLeft)

    dat_filepath_input = QLineEdit(dict_global.get("dat_file", "data.dat")) # Use .get for robustness
    dat_filepath_input.setFixedWidth(300)
    button_layout.addWidget(dat_filepath_input, 0, 2, alignment=Qt.AlignLeft)

    def update_dat_filepath():
        new_path = dat_filepath_input.text().strip().strip('"')
        if new_path:
            dict_global["dat_file"] = new_path
            print(f"Updated file path: {dict_global['dat_file']}")
    dat_filepath_input.editingFinished.connect(update_dat_filepath)

    dict_global["gui_elements"]["text_input_entry_dat_filepath"] = dat_filepath_input

    update_filepath_button = QPushButton("autosearch file")
    update_filepath_button.clicked.connect(lambda: button_function_autosearch_file(dict_global))
    button_layout.addWidget(update_filepath_button, 0, 3, alignment=Qt.AlignLeft)
    dict_global["gui_elements"]["update_filepath_button"] = update_filepath_button

    read_file_for_first_time_button = QPushButton("Read a fresh file")
    read_file_for_first_time_button.clicked.connect(lambda: read_file_for_first_time(dict_global)) # Connect to your actual function
    button_layout.addWidget(read_file_for_first_time_button, 0, 4, alignment=Qt.AlignLeft)
    dict_global["gui_elements"]["read_file_for_first_time_button"] = read_file_for_first_time_button

    button_switch_streaming = QPushButton(f"Streaming: {dict_global['streaming']}")
    button_switch_streaming.clicked.connect(lambda: button_function_toggle_csv_stream(dict_global))
    button_layout.addWidget(button_switch_streaming, 0, 5, alignment=Qt.AlignLeft)
    dict_global["gui_elements"]["button_switch_streaming"] = button_switch_streaming

    auto_zoom_button = QPushButton(f"Auto Zoom: {dict_global['auto_zoom']}")
    auto_zoom_button.clicked.connect(lambda: button_function_reset_auto_zoom(dict_global))
    button_layout.addWidget(auto_zoom_button, 0, 6, alignment=Qt.AlignLeft)
    dict_global["gui_elements"]["auto_zoom_button"] = auto_zoom_button

    # Row 1
    exit_button = QPushButton("Exit")
    exit_button.clicked.connect(lambda: button_function_exit_app(dict_global))
    button_layout.addWidget(exit_button, 1, 0, alignment=Qt.AlignLeft)
    dict_global["gui_elements"]["exit_button"] = exit_button

    button_layout.addWidget(QLabel("File:"), 1, 1, alignment=Qt.AlignLeft)

    json_filepath_input = QLineEdit(dict_global.get("json_filepath", "user_settings.json")) # Use .get
    json_filepath_input.setFixedWidth(300)
    button_layout.addWidget(json_filepath_input, 1, 2, alignment=Qt.AlignLeft)

    def update_json_filepath():
        new_path = json_filepath_input.text().strip().strip('"')
        if new_path:
            dict_global["json_filepath"] = new_path
            print(f"Updated JSON file path: {dict_global['json_filepath']}")
    json_filepath_input.editingFinished.connect(update_json_filepath)
    dict_global["gui_elements"]["file_path_input_entry_json_filepath"] = json_filepath_input

    load_json_button = QPushButton("Load user settings")
    load_json_button.clicked.connect(lambda: button_function_load_user_settings(dict_global))
    button_layout.addWidget(load_json_button, 1, 3, alignment=Qt.AlignLeft)
    dict_global["gui_elements"]["load_json_button"] = load_json_button

    save_json_button = QPushButton("save user settings")
    save_json_button.clicked.connect(lambda: button_function_save_user_settings(dict_global))
    button_layout.addWidget(save_json_button, 1, 4, alignment=Qt.AlignLeft)
    dict_global["gui_elements"]["save_json_button"] = save_json_button

    save_png_button = QPushButton("Save as PNG")
    save_png_button.clicked.connect(lambda: button_function_save_plot_as_png(dict_global))
    button_layout.addWidget(save_png_button, 1, 5, alignment=Qt.AlignLeft)
    dict_global["gui_elements"]["save_png_button"] = save_png_button

    button_layout.setColumnStretch(2, 1)


def configure_bottom_panel(frame_holding_consoles, dict_global):
    if not frame_holding_consoles.layout():
        consoles_panel_layout = QVBoxLayout(frame_holding_consoles)
    else:
        consoles_panel_layout = frame_holding_consoles.layout()

    bottom_splitter = QSplitter(Qt.Horizontal)
    consoles_panel_layout.addWidget(bottom_splitter)

    left_notebook_paned_frame = QFrame()
    left_notebook_paned_frame.setFrameShape(QFrame.Shape.StyledPanel)
    left_notebook_paned_frame.setFrameShadow(QFrame.Shadow.Sunken)
    left_layout = QVBoxLayout(left_notebook_paned_frame)
    bottom_splitter.addWidget(left_notebook_paned_frame)
    bottom_splitter.setStretchFactor(0, 1)

    left_notebook = QTabWidget()
    left_layout.addWidget(left_notebook)

    left_text_editor_frame = QWidget()
    left_notebook.addTab(left_text_editor_frame, "Output Console")
    left_text_editor_layout = QVBoxLayout(left_text_editor_frame)

    output_console = QTextEdit()
    output_console.setReadOnly(True)
    # Corrected WordWrapMode usage
    # output_console.setWordWrapMode(QTextOption.WrapMode.WidgetWidth)
    left_text_editor_layout.addWidget(output_console)

    dict_global["redirect_error"] = output_console
    dict_global["redirect_output"] = output_console

    right_notebook_paned_frame = QFrame()
    right_notebook_paned_frame.setFrameShape(QFrame.Shape.StyledPanel)
    right_notebook_paned_frame.setFrameShadow(QFrame.Shadow.Sunken)
    right_layout = QVBoxLayout(right_notebook_paned_frame)
    bottom_splitter.addWidget(right_notebook_paned_frame)
    bottom_splitter.setStretchFactor(1, 1)

    right_notebook = QTabWidget()
    right_layout.addWidget(right_notebook)

    right_side_json_editor_frame = QWidget()
    right_notebook.addTab(right_side_json_editor_frame, "JSON Editor")
    json_editor_layout = QGridLayout(right_side_json_editor_frame)

    json_text_editor = QTextEdit()
    json_text_editor.setFontFamily("Courier")
    json_editor_layout.addWidget(json_text_editor, 0, 0, 1, 3)

    open_json_button = QPushButton("Open JSON")
    open_json_button.clicked.connect(lambda: json_editor_functions.open_json(json_text_editor))
    json_editor_layout.addWidget(open_json_button, 1, 0, alignment=Qt.AlignLeft)

    save_json_button = QPushButton("Save JSON")
    save_json_button.clicked.connect(lambda: json_editor_functions.save_json(json_text_editor))
    json_editor_layout.addWidget(save_json_button, 1, 1, alignment=Qt.AlignLeft)

    reload_json_button = QPushButton("Reload")
    reload_json_button.clicked.connect(lambda: json_editor_functions.reload_json(json_text_editor))
    json_editor_layout.addWidget(reload_json_button, 1, 2, alignment=Qt.AlignLeft)

    json_editor_layout.setRowStretch(0, 1)

    right_side_text_editor_frame = QWidget()
    right_notebook.addTab(right_side_text_editor_frame, "Note pad - append mode")
    text_editor_layout = QGridLayout(right_side_text_editor_frame)

    text_editor = QTextEdit()
    text_editor.setFontFamily("Courier")
    text_editor_layout.addWidget(text_editor, 0, 0, 1, 3)

    open_text_button = QPushButton("Open text file")
    open_text_button.clicked.connect(lambda: text_editor_functions.open_text_file(text_editor))
    text_editor_layout.addWidget(open_text_button, 1, 0, alignment=Qt.AlignLeft)

    save_text_button = QPushButton("Save text file")
    save_text_button.clicked.connect(lambda: text_editor_functions.save_text_file(text_editor))
    text_editor_layout.addWidget(save_text_button, 1, 1, alignment=Qt.AlignLeft)

    reload_text_button = QPushButton("Reload text file")
    reload_text_button.clicked.connect(lambda: text_editor_functions.reload_text_file(text_editor))
    text_editor_layout.addWidget(reload_text_button, 1, 2, alignment=Qt.AlignLeft)

    text_editor_layout.setRowStretch(0, 1)


def create_gui_elements(dict_global):
    main_window = dict_global["main_window"]

    main_frame = QWidget()
    main_window.setCentralWidget(main_frame)
    main_layout = QVBoxLayout(main_frame)

    paned_window = QSplitter(Qt.Vertical)
    main_layout.addWidget(paned_window)

    frame_holding_figure = QFrame()
    frame_holding_figure.setFrameShape(QFrame.Shape.StyledPanel)
    frame_holding_figure.setFrameShadow(QFrame.Shadow.Sunken)
    QVBoxLayout(frame_holding_figure) # Set layout here
    paned_window.addWidget(frame_holding_figure)

    frame_holding_buttons = QFrame()
    frame_holding_buttons.setFrameShape(QFrame.Shape.StyledPanel)
    frame_holding_buttons.setFrameShadow(QFrame.Shadow.Sunken)
    paned_window.addWidget(frame_holding_buttons) # Layout set in configure_button_panel

    frame_holding_consoles = QFrame()
    frame_holding_consoles.setFrameShape(QFrame.Shape.StyledPanel)
    frame_holding_consoles.setFrameShadow(QFrame.Shadow.Sunken)
    QVBoxLayout(frame_holding_consoles) # Set layout here
    paned_window.addWidget(frame_holding_consoles)

    paned_window.setSizes([500, 100, 200])
    paned_window.setStretchFactor(0, 5)
    paned_window.setStretchFactor(1, 1)
    paned_window.setStretchFactor(2, 2)

    dict_global["gui_elements"]["paned_window"] = paned_window
    dict_global["gui_elements"]["frame_holding_figure"] = frame_holding_figure
    dict_global["gui_elements"]["frame_holding_buttons"] = frame_holding_buttons
    dict_global["gui_elements"]["frame_holding_consoles"] = frame_holding_consoles

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

# This replaces your data_tracker.in_and_output.redirecting.RedirectText
class StreamRedirector(object):
    """Redirects stdout and stderr to a QTextEdit widget."""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.flush = sys.stdout.flush

    def write(self, text):
        self.text_widget.insertPlainText(text)
        self.text_widget.verticalScrollBar().setValue(self.text_widget.verticalScrollBar().maximum())
