import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import io
import sys

# == # https://stackoverflow.com/questions/17108250/efficiently-read-last-n-rows-of-csv-into-dataframe

def get_csv_tail(filepath, max_rows=1):
    with open(filepath, "rb") as f:
        # first = f.readline()
        first = f.readline().decode(sys.stdout.encoding)  # Read the first line.
        f.seek(-2, 2)                                     # Jump to the second last byte.
        count = 0
        while count < max_rows:                           # Until we've gone max_rows back
            try:
                while f.read(1) != b"\n\r":                 # Until EOL is found...
                    f.seek(-2, 1)                         # ...jump back the read byte plus one more.
            except IOError:
                f.seek(-1, 1)
                if f.tell() == 0:
                    break
            count = count + 1
            f.seek(-2, 1)                                 # ...jump back the read byte plus one more.
        f.seek(1, 1)                                      # move forward one byte
        tail = f.read().decode(sys.stdout.encoding)       # We found our spot; read from here through to the end of the file.
        f.close()
                
def convert_time_stamp(aaa, subtractor=None):
    aaa["time"] = pd.to_datetime(aaa["time"], format="%a %b %d %H:%M:%S %Y")
    if not subtractor:
        subtractor = aaa["time"][0]
    aaa["time"] -= subtractor
    aaa["time"] = aaa["time"].dt.total_seconds()
    aaa["time"] /= 3600
    return subtractor


dat_file = r"C:\Users\pkv190\Dropbox\CODES\playground\arianna_monitoring_file\Fri-Mar-07-21-31-13-2025_EDAutoLog\EDAutoLog.dat"
aaa = read_file = pd.read_csv(dat_file, delimiter="\t", header=1, index_col=False)
list_column_names = column_names = read_file.columns  # aaa[:10][0]
print(column_names)
column_names = column_names[1:].tolist() + ["Unknown"]  # Shift left, fill last column
aaa.columns = column_names  # Set new column names
# aaa.reset_index(drop=True, inplace=True)  # Reset index
# print(aaa.columns)
# print(aaaaaa)


first_time = convert_time_stamp(aaa)

keys_of_interest = [
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




# print(aaa.iloc[:, 1])
# print(
#     aaa[
#     [    "Specimen PiG4",
#             "RT1 PiG5",]
#     ]
# )
# print(ddddd)


# fig, axes = plt.subplots(3,3, figsize=(20, 10))
# axes = axes.flatten()

fig, ax = plt.subplots()
plt.figure(figsize=(20, 10))

lines = []  # List to store line objects

# Plot multiple curves and store the line objects
lines.append(ax.plot(x, y1, label="sin(x)")[0])
lines.append(ax.plot(x, y2, label="cos(x)")[0])
lines.append(ax.plot(x, y3, label="sin(x) * cos(x)")[0])

def update_plot(new_y_values):
    for line, new_y in zip(lines, new_y_values):
        line.set_ydata(new_y)  # Update Y values of each curve

    fig.canvas.draw_idle()  # Redraw only the updated parts
    fig.canvas.flush_events()  # Ensure updates are visible

    
for index_key, key in enumerate(keys_of_interest):
    print(key)

    time_ = aaa["time"]
    column = aaa[key]
    # print(column)
    # plt.plot(list(range(len(time_))), column)
    # axes[index_key].plot(time_, column)
    # axes[index_key].set_title(key)
    plt.plot(time_, column, label=key)
plt.legend()

# plt.ylim([0, max(200, np.max(aaa[keys_of_interest]) * 1.1)])
# plt.ylim([0, max(200, np.max(aaa["Penning PeG1"]) * 1.1)])
plt.ion()  # Turn on interactive mode
plt.show()

# Function to update plot
def update_plot(new_y):
    line.set_ydata(new_y)  # Update Y values
    fig.canvas.draw_idle()  # Redraw only what's needed
    fig.canvas.flush_events()  # Ensure update in interactive mode

# Simulate updates without resetting zoom
import time
for i in [1, 2, 3]:
    # df = pd.read_csv(get_csv_tail(dat_file, max_rows=5), delimiter="\t", header=1, index_col=False)    # Get the last five rows as a df
    df = pd.read_csv(dat_file, skiprows=38359, delimiter="\t", header=1, index_col=False)
    df.columns = column_names[:-1]
    convert_time_stamp(df, subtractor=first_time)
    aaa = pd.concat([aaa, df]).drop_duplicates()
    print(df)
    print(aaa)
    for index_key, key in enumerate(keys_of_interest):
        # print(key)
        # time_ = aaa["time"]
        column = aaa[key]
        # new_y = np.sin(x + np.random.uniform(-0.5, 0.5))  # Example update
        update_plot(column)
    time.sleep(0.5)  # Pause to visualize updates

