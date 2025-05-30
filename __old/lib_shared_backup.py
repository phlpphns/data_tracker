
def set_gui_elements_matplotlib_only(dict_global):
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


# Update function for animation
def _update_plot(frame, dict_global):
    # global dict_global
    aaa = dict_global["aaa"]
    dat_file = dict_global["dat_file"]
    streaming = dict_global["streaming"]

    if not streaming:
        return list(
            dict_global["lines_in_plot"].items()
        )  # line1, line2  # Do nothing if streaming is stopped

    a, b = next(gen_yield_line)
    print(a, b)

    # aaa = read_file = pd.read_csv(dat_file, delimiter="\t", header=1, index_col=False, skiprows=a, nrows=b-a)

    df = pd.read_csv(
        dat_file, delimiter="\t", header=1, index_col=False, skiprows=a, nrows=b - a
    )
    df.columns = dict_global["column_names"]#[:-1]
    convert_time_stamp(df, subtractor=dict_global["first_time"])
    aaa = pd.concat([aaa, df]).drop_duplicates()
    dict_global["aaa"] = aaa
    for key in dict_global["keys_of_interest"]:
        line = dict_global["lines_in_plot"][key]
        line[0].set_xdata(aaa["time"])
        line[0].set_ydata(aaa[key])

    if dict_global["auto_zoom"]:
        set_axis_on_auto_zoom_respecting_user_limits(dict_global)

    return list(dict_global["lines_in_plot"].items())




