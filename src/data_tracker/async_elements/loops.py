from ..conversions.time_conversions import convert_time_stamp
from ..plotting.set_lines_in_plot import update_plot

import asyncio
import pandas as pd
import threading
import traceback


def start_data_streaming(dict_global):
    """Ensures the asyncio loop is running and starts the data streaming task."""
    start_asyncio_loop(dict_global)  # Ensure event loop is running
    async_loop = dict_global["threading"]["async_loop"]
    asyncio.run_coroutine_threadsafe(update_plot_async(dict_global), async_loop)


def start_asyncio_loop(dict_global):
    """Start the asyncio event loop in a separate thread if not already running."""
    if dict_global["threading"]["loop_running"]:
        return  # Prevent duplicate loops

    async_loop = get_async_loop(dict_global)
    dict_global["threading"]["loop_running"] = True  # Mark loop as running

    def run_loop():
        try:
            asyncio.set_event_loop(async_loop)
            async_loop.run_forever()
        except Exception as e:
            print(f"Asyncio Loop Error: {e}")
            traceback.print_exc()
        finally:
            dict_global["threading"]["loop_running"] = False  # Mark loop as stopped

    threading.Thread(target=run_loop, daemon=True).start()


def get_async_loop(dict_global):
    """Ensure that the global asyncio loop exists and is initialized properly."""
    if "threading" not in dict_global:
        dict_global["threading"] = {}

    if "loop_running" not in dict_global:
        dict_global["threading"]["loop_running"] = False

    if not isinstance(
        dict_global["threading"].get("async_loop"), asyncio.AbstractEventLoop
    ):
        dict_global["threading"]["async_loop"] = asyncio.new_event_loop()

    return dict_global["threading"]["async_loop"]


async def update_plot_async(dict_global):
    """Asynchronous function to update the plot periodically while streaming."""
    while dict_global["streaming"]:
        try:
            rows = dict_global["function_get_new_data"]()
            df = await asyncio.to_thread(
                dict_global["data_reader"].read,
                file_path=dict_global["dat_file"],
                file_type=dict_global["file_type"],
                delimiter="\t",
                header=2,
                index_col=False,
                **rows,
            )

            if len(df) > 0:
                df.columns = dict_global["column_names"]
                await asyncio.to_thread(
                    convert_time_stamp, df, time_reference=dict_global["time_reference"]
                )
                dict_global["pandas_main_dataframe_read_data"] = pd.concat(
                    [dict_global["pandas_main_dataframe_read_data"], df]
                ).drop_duplicates()
                update_plot(dict_global)

                for feature, tuple_ in dict_global["tab_animations"].items():
                    fig, ax, line, canvas = tuple_
                    try:
                        line.set_xdata(
                            dict_global["pandas_main_dataframe_read_data"]["time"]
                        )
                        line.set_ydata(
                            dict_global["pandas_main_dataframe_read_data"][feature]
                        )
                        ax.relim()
                        ax.autoscale_view()
                        canvas.draw()
                    except Exception as e:
                        print(f"Error animating {feature}: {e}")
                        traceback.print_exc()
                    # pass
        except Exception as e:
            print(f"Error in update_plot_async: {e}")
            traceback.print_exc()

