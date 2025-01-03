
# takes the paperclip as an input, either from multi-line text or excel cells
# creates a list of strings (lines or cells) and displays the list in a tkinter interface
# detects when one element has been pasted (cmd + V), and moves to the next element

import tkinter as tk
from tkinter import messagebox
import pyperclip
from pynput import keyboard


class ClipboardToListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipboard to List")

        # Make the window always stay on top
        self.root.attributes("-topmost", True)

        # Initialize variables
        self.data_list = []
        self.current_index = 0
        self.cmd_pressed = False  # Track the state of the Cmd key

        # Create a Listbox to display strings (read-only behavior)
        self.listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=50, height=20, exportselection=False)
        self.listbox.pack(pady=10)

        # Allow selection changes via mouse or keyboard
        self.listbox.bind('<<ListboxSelect>>', self.on_selection_change)
        self.listbox.bind('<Key>', lambda e: "break")  # Prevent direct keyboard interactions

        # Load clipboard data into the listbox
        self.load_clipboard()

        # Set initial clipboard content to the first element
        if self.data_list:
            self.set_clipboard(self.data_list[0])

        # Start global key listener
        self.listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
        self.listener.start()

    def load_clipboard(self):
        """Load clipboard content into the list and display in the listbox."""
        try:
            # Read clipboard content
            clipboard_content = pyperclip.paste()
            rows = [row.split('\t') for row in clipboard_content.split('\n') if row.strip()]

            # Flatten the 2D list into a single list (row by row, cell by cell)
            self.data_list = [cell.strip() for row in rows for cell in row if cell.strip()]

            # Populate the listbox
            self.listbox.delete(0, tk.END)  # Clear any existing entries
            for item in self.data_list:
                self.listbox.insert(tk.END, item)

            # Select the first element
            if self.data_list:
                self.listbox.select_set(0)
                self.listbox.activate(0)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load clipboard content: {e}")

    def on_selection_change(self, event):
        """Update the current index when the selection changes."""
        try:
            self.current_index = self.listbox.curselection()[0]
        except IndexError:
            pass  # Ignore if no selection is available

    def on_key_press(self, key):
        """Handle key press events."""
        try:
            if key == keyboard.Key.cmd:
                self.cmd_pressed = True  # Track the Command key (macOS)

            # Check for Cmd+V or Ctrl+V
            if self.cmd_pressed and hasattr(key, 'char') and key.char == 'v':
                self.handle_paste()

        except AttributeError:
            pass  # Handle keys without 'char' attribute

    def on_key_release(self, key):
        """Handle key release events."""
        if key == keyboard.Key.cmd:
            self.cmd_pressed = False  # Reset the Command key state

    def handle_paste(self):
        """Handle the paste action to update the list."""
        if self.current_index < len(self.data_list):
            # Get the current list item to paste
            current_text = self.data_list[self.current_index]

            # Set clipboard content to the current list item
            self.set_clipboard(current_text)

            # Perform the paste action (e.g., in another application)
            print(f"Pasting: {current_text}")  # Debugging

            # Move to the next item after the paste
            self.current_index += 1
            if self.current_index < len(self.data_list):
                # Highlight the next item
                self.listbox.select_clear(0, tk.END)
                self.listbox.select_set(self.current_index)
                self.listbox.activate(self.current_index)
            else:
                # If the last item is reached, show a message
                self.listbox.select_clear(0, tk.END)
                messagebox.showinfo("Info", "You have completed pasting all items.")
        else:
            messagebox.showwarning("Warning", "No more items to paste.")

    def set_clipboard(self, text):
        """Set the clipboard content."""
        pyperclip.copy(text)

    def on_close(self):
        """Stop the listener when closing the app."""
        self.listener.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClipboardToListApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)  # Ensure the listener is stopped when the app closes
    root.mainloop()
