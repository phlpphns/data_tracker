import pandas as pd
import time

def convert_time_stamp(pandas_main_dataframe_read_data, convert_time_to_hours=False, time_reference=None, ):
    pandas_main_dataframe_read_data["time"] = pd.to_datetime(
        pandas_main_dataframe_read_data["time"], format="%a %b %d %H:%M:%S %Y"
    )
    if convert_time_to_hours:
        if not time_reference:
            time_reference = pandas_main_dataframe_read_data["time"][0]
        pandas_main_dataframe_read_data["time"] -= time_reference
        pandas_main_dataframe_read_data["time"] = pandas_main_dataframe_read_data[
            "time"
        ].dt.total_seconds()
        pandas_main_dataframe_read_data["time"] /= 3600
    return time_reference
