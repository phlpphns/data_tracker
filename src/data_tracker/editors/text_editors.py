from ..in_and_output.read_write_text_files import json, load_json, write_json_file

import tkinter as tk
from tkinter import filedialog, messagebox

class text_editor_functions:
    def open_text_file(text_editor):
        """Open a text file and display it in the editor."""
        global current_file
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                text_data = file.read()  # Read entire file as plain text
                # print(text_data)
                # print(
                #     f"File content: {repr(text_data)}"
                # )  # Debug: Check if content is loaded

            print(
                f"Before insert: text_editor.winfo_exists() = {text_editor.winfo_exists()}"
            )
            text_editor.delete("1.0", tk.END)  # Clear previous content
            text_editor.insert(tk.END, text_data)  # Insert new content
            print("Text inserted successfully.")  # Debug message

            current_file = file_path
            print(f"Loaded text file: {file_path}")

        except OSError as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def save_text_file(text_editor):
        """Save the edited text data back to file."""
        global current_file
        if not current_file:
            messagebox.showwarning("Warning", "No file loaded. Use 'Open' first.")
            return

        try:
            text_data = text_editor.get("1.0", tk.END).strip()

            with open(current_file, "w", encoding="utf-8") as file:
                file.write(text_data)  # Write text back to file

            print(f"Saved text file: {current_file}")
            messagebox.showinfo("Success", "File saved successfully!")

        except OSError as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def reload_text_file(text_editor):
        """Reload the last opened text file."""
        if not current_file:
            messagebox.showwarning("Warning", "No file to reload.")
            return

        print(f"Reloading file: {current_file}")
        text_editor_functions.open_text_file(text_editor)  # Reuse open_text_file function

    # ======== # ======= # =======


class json_editor_functions:
    def open_json(json_text_editor):
        """Open a JSON file and display it in the editor."""
        global current_file
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            json_data = load_json(file_path)
            # with open(file_path, "r", encoding="utf-8") as file:
            #     json_data = json.load(file)
            #     # print(json_data)

            # Pretty-print JSON into editor
            json_text_editor.delete("1.0", tk.END)
            json_text_editor.insert(tk.END, json.dumps(json_data, indent=4))

            current_file = file_path
            print(f"Loaded JSON file: {file_path}")

        except (json.JSONDecodeError, OSError) as e:
            messagebox.showerror("Error", f"Failed to open JSON file:\n{e}")

    def save_json(json_text_editor):
        """Save the edited JSON data back to file."""
        global current_file
        if not current_file:
            messagebox.showwarning("Warning", "No file loaded. Use 'Open JSON' first.")
            return

        try:
            json_text = json_text_editor.get("1.0", tk.END).strip()
            json_data = json.loads(json_text)  # Validate JSON

            write_json_file(json_data, current_file)

            # with open(current_file, "w", encoding="utf-8") as file:
            #    json.dump(json_data, file, indent=4)

            print(f"Saved JSON file: {current_file}")
            messagebox.showinfo("Success", "File saved successfully!")

        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Invalid JSON format:\n{e}")

    def reload_json(json_text_editor):
        """Reload the last opened JSON file."""
        global current_file
        if not current_file:
            messagebox.showwarning("Warning", "No file to reload.")
            return

        print(f"Reloading file: {current_file}")
        json_editor_functions.open_json(json_text_editor)  # Reuse open_json function
