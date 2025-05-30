import asyncio

import numpy as np

# from plotting.set_lines_in_plot import set_axis_on_auto_zoom_respecting_user_limits
def set_axis_on_auto_zoom_respecting_user_limits(dict_global):
    pandas_main_dataframe_read_data = dict_global["pandas_main_dataframe_read_data"]
    ax = dict_global["ax"]
    keys_of_interest = dict_global["keys_of_interest"]

    if False:
        ax.set_xlim(
            [
                0,
                max(
                    dict_global.get("user_defined_max_x_threshold", 0),
                    np.max(pandas_main_dataframe_read_data["time"]),# * 1.1,
                ),
            ]
        )

    start_limit = pandas_main_dataframe_read_data["time"].iloc[0]
    end_limit = pandas_main_dataframe_read_data["time"].iloc[-1]
    ax.set_xlim(start_limit, end_limit)

    if keys_of_interest:
        y_values = pandas_main_dataframe_read_data[keys_of_interest].values.flatten()
        min_y = np.min(y_values)
        max_y = np.max(y_values)
        padding = (max_y - min_y) * 0.1  # 10% padding
        ax.set_ylim([min_y - padding, max_y + padding])
    else:
        ax.set_ylim([0, 1])  # Default limits if no keys are selected


def update_plot(dict_global):
    """Updates the plot based on selected features."""
    ax = dict_global["ax"]
    df = dict_global["pandas_main_dataframe_read_data"]
    selected_features = dict_global["keys_of_interest"]
    lines = dict_global.setdefault("lines_in_plot", {})  # Initialize if not exists

    # Remove lines for unselected features
    keys_to_remove = [key for key in list(lines.keys()) if key not in selected_features]
    for key in keys_to_remove:
        line = lines.pop(key)
        line.remove()

    # Add/update lines for selected features
    if (
        len(df) > 0 and len(selected_features) > 0
    ):  # check if the data frame and selected features are not empty.
        for key in selected_features:
            if key not in lines:
                (line,) = ax.plot(df["time"], df[key], label=key, lw=3)
                lines[key] = line
            else:
                line = lines[key]
                line.set_xdata(df["time"])
                line.set_ydata(df[key])

        ax.legend(loc=2)
    else:
        pass
        # ax.legend() #still call legend so the warning is not shown.

    dict_global["canvas"].draw()

    if dict_global.get("auto_zoom", False):
        set_axis_on_auto_zoom_respecting_user_limits(dict_global)
