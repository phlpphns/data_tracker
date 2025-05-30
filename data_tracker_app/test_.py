print('Hallo Philipp')

import data_tracker

import numpy

import os
import stat
import sys

import oxidized_importer

# Create a collector to help with managing resources.
collector = oxidized_importer.OxidizedResourceCollector(
    allowed_locations=["in-memory"]
)

print("ended sucessfully")
# for i in collector:
# 	print(i)

'''

import os
import stat
import sys

import oxidized_importer

# Create a collector to help with managing resources.
collector = oxidized_importer.OxidizedResourceCollector(
    allowed_locations=["in-memory"]
)

print(1)
# Add all known Python resources by scanning sys.path.
# Note: this will pull in the Python standard library and
# any other installed packages, which may not be desirable!
for path in sys.path:
    # Only directories can be scanned by oxidized_importer.
    if os.path.isdir(path):
        for resource in oxidized_importer.find_resources_in_path(path):
            collector.add_in_memory(resource)

print(2)

# Turn the collected resources into ``OxidizedResource`` and file
# install rules.
resources, file_installs = collector.oxidize()

print(3)

# Now index the resources so we can serialize them.
finder = oxidized_importer.OxidizedFinder()
finder.add_resources(resources)

print(4)

# Turn the indexed resources into an opaque blob.
packed_data = finder.serialize_indexed_resources()

# Write out that data somewhere.
with open("oxidized_resources", "wb") as fh:
    fh.write(packed_data)

print(5)


# Then for all the file installs, materialize those files.
for (path, data, executable) in file_installs:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("wb") as fh:
        fh.write(data)

    if executable:
        path.chmod(path.stat().st_mode | stat.S_IEXEC)


print(6)

'''


#'''
import sys
import oxidized_importer

finder = oxidized_importer.OxidizedFinder()

# You want to register the finder first so it has the highest priority.
sys.meta_path.insert(0, finder)


import tkinter as tk
from tkinter import ttk
import asyncio
import threading

# Global Variables
root = tk.Tk()
root.title("Async Tkinter App")
loop_running = False  # Flag to track loop state
animation = "░▒▒▒▒▒"
progress_value = 0

# UI Elements
label = tk.Label(root, text="")
label.grid(row=0, columnspan=2, padx=8, pady=16)

progressbar = ttk.Progressbar(root, length=280)
progressbar.grid(row=1, columnspan=2, padx=8, pady=16)

# Asyncio event loop reference
async_loop = None

def start_asyncio_loop():
    """Start the asyncio event loop in a separate thread."""
    global async_loop, loop_running
    if loop_running:
        return  # Prevent duplicate loops

    loop_running = True
    async_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(async_loop)
    
    # Run the event loop forever
    try:
        async_loop.run_forever()
    except Exception as e:
        print(f"Asyncio Loop Error: {e}")
    finally:
        loop_running = False

# Start the event loop in a separate thread
def ensure_loop():
    """Ensure that the asyncio loop is running before submitting tasks."""
    global loop_running
    if not loop_running:
        threading.Thread(target=start_asyncio_loop, daemon=True).start()

async def animate_label():
    """Async function to animate the label text."""
    global animation
    while True:
        label["text"] = animation
        animation = animation[1:] + animation[0]
        await asyncio.sleep(0.1)

async def calculate_async():
    """Async function to update progress bar smoothly."""
    global progress_value
    max_value = 3000000
    for i in range(1, max_value):
        progress_value = i / max_value * 100
        root.after(0, update_progressbar)
        if i % 1000 == 0:
            await asyncio.sleep(0)

def update_progressbar():
    """Update the progress bar in the Tkinter thread."""
    progressbar["value"] = progress_value

def restart_animation():
    """Restart the animation coroutine in the asyncio loop."""
    ensure_loop()
    if async_loop is not None:
        asyncio.run_coroutine_threadsafe(animate_label(), async_loop)

# Buttons
button_block = tk.Button(root, text="Restart Animation", width=15, command=restart_animation)
button_block.grid(row=2, column=0, padx=8, pady=8)

button_non_block = tk.Button(root, text="Calculate Async", width=15, command=lambda: asyncio.run_coroutine_threadsafe(calculate_async(), async_loop))
button_non_block.grid(row=2, column=1, padx=8, pady=8)

# Ensure event loop runs and start animation
ensure_loop()
root.after(500, restart_animation)  # Delayed start to ensure the loop is initialized

# Run Tkinter
root.mainloop()


def bar():
    return "baz"

def run():
    return 'test hallo'#bar()


#'''