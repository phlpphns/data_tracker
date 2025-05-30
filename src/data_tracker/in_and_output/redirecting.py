import tkinter as tk

class RedirectText:
        """Class to redirect print output to a Tkinter Text widget."""

        def __init__(self, text_widget):
                self.text_widget = text_widget

        def write(self, string):
                self.text_widget.insert(tk.END, string)
                self.text_widget.see(tk.END)  # Auto-scroll

        def flush(self):
                pass  # Required for compatibility with sys.stdout
