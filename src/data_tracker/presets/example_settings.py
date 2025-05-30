def define_dict_user_settings_jeol():
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
    dict_user_settings["name_png"] = "screenshots/test.png"
    dict_user_settings["streaming"] = False  # Controls the animation loop
    dict_user_settings[
        "json_filepath"
    ] = "./config_files/instructions_json.json"  # Default filepath
    # dict_user_settings["json_filepath"] = r"C:\Users\pkbv190\Dropbox\CODES\playground\arianna_monitoring_file\instructions_json - Copy.json"
    # Global Dictionary for Settings
    dict_user_settings["refresh_rate_in_ms"] = 50
    dict_user_settings["user_defined_max_x_threshold"] = 100 / 3600
    dict_user_settings["user_defined_max_y_threshold"] = 200
    dict_user_settings["auto_zoom"] = True
    dict_user_settings["root_dir_data_files"] = "."
    dict_user_settings["pattern_auto_file_search"] = "EDAutoLog.dat"
    dict_user_settings["auto_file_search_on_startup"] = True
    dict_user_settings["auto_run_on_startup"] = True
    dict_user_settings["leading_delimiter"] = True
    dict_user_settings["file_type"] = "csv"
    dict_user_settings["dat_file"] = r"./test.dat"

    # read user settings from a json file (try!)
    # dict_user_settings[
    #     "dat_file"
    # ] = r"C:\Users\pkv190\Dropbox\CODES\playground\arianna_monitoring_file\Fri-Mar-07-21-31-13-2025_EDAutoLog\EDAutoLog.dat"


    return dict_user_settings