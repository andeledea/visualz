import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import os

from zoxide import ZoxideDB

# https://colorhunt.co/
class themePalette:
    dominant = "#113F67"
    accent = "#FDF5AA"
    secondary = "#34699A"

# Initialize ZoxideDB
db = ZoxideDB("zoxide_db.json")

def list_files(query):
    try:
        results = db.search(query)
        valid_paths = [entry["path"] for entry in results]
        valid_paths.append("Add directory to z")
        return valid_paths
    except Exception:
        print("Error searching zoxide database.")
        return []

def open_in_explorer(path):
    os.startfile(path)

def add_to_z(path):
    try:
        if path and os.path.exists(path):
            db.add(path)
            print(f"Added {path} to zoxide database.")
        else:
            print("Invalid path, not added.")
    except Exception as e:
        print(f"Error adding path to zoxide: {e}")

class VisualZApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VisualZ Search")
        self.geometry("500x150")
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.configure(bg=themePalette.dominant, highlightthickness=3, highlightcolor=themePalette.accent)
        self.bind("<FocusOut>", lambda e: self.focus_destroy())

        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TEntry", foreground=themePalette.dominant, fieldbackground=themePalette.accent, font=("Cascadia Mono", 12))
        s.configure("TLabel", background=themePalette.dominant, foreground=themePalette.accent, font=("Segoe UI", 11, "bold"))

        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.search_var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.search_var, width=40, style="TEntry", font=("Cascadia Mono", 12))
        self.entry.pack(pady=15)
        self.entry.focus()

        self.listbox = tk.Listbox(self, font=("Cascadia Mono", 12), height=3, bd=0, highlightthickness=0,
                                  bg=themePalette.secondary, fg=themePalette.accent,
                                  selectbackground=themePalette.accent, selectforeground=themePalette.dominant,
                                  activestyle="none")
        self.listbox.pack(fill=tk.X, padx=20)
        self.listbox.pack_forget()

        self.search_var.trace_add('write', self.on_search)
        self.entry.bind("<Down>", self.focus_listbox)
        self.entry.bind("<Tab>", self.select_next)
        self.entry.bind("<Shift-Tab>", self.select_previous)
        self.entry.bind("<Return>", self.open_selected)
        self.entry.bind("<Escape>", lambda e: self.destroy())
        self.listbox.bind("<Return>", self.open_selected)
        self.listbox.bind("<Tab>", self.select_next)
        self.listbox.bind("<Shift-Tab>", self.select_previous)
        self.listbox.bind("<Double-Button-1>", self.open_selected)
        self.listbox.bind("<Escape>", lambda e: self.destroy())

        self.results = []
        
    def _path_to_display(self, path):
        if len(path.split(os.sep)) > 4:
            parts = path.split(os.sep)
            drive = os.path.splitdrive(path)[0]
            first = parts[1].strip()
            last = parts[-2].strip()
            if len(first) > 10:
                first = first[:4] + ".."
            if len(last) > 10:
                last = last[:4] + ".."
            return f"{drive}{os.sep}{first}{os.sep}...{os.sep}{last}{os.sep}{os.path.basename(path)}"
        else:
            return path

    def on_search(self, *args):
        query = self.search_var.get()
        self.results = list_files(query)
        self.listbox.delete(0, tk.END)
        for item in self.results:
            if item == "Add directory to z":
                display_item = "Add directory to z"
            else:
                display_item = self._path_to_display(item)
                
            self.listbox.insert(tk.END, " " + display_item)
        if self.results:
            self.listbox.pack(fill=tk.X, padx=20)
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(0)
        else:
            self.listbox.pack_forget()

    def focus_listbox(self, event):
        if self.results:
            self.listbox.focus_set()
            self.listbox.selection_set(0)
        return "break"

    def select_next(self, event):
        if self.results:
            lb = self.listbox
            cur = lb.curselection()
            next_idx = (cur[0] + 1) % len(self.results) if cur else 0
            lb.selection_clear(0, tk.END)
            lb.selection_set(next_idx)
            lb.activate(next_idx)
            lb.see(next_idx)
        return "break"

    def select_previous(self, event):
        if self.results:
            lb = self.listbox
            cur = lb.curselection()
            next_idx = (cur[0] - 1) if cur else 0
            if next_idx < 0:
                next_idx = len(self.results) - 1
            lb.selection_clear(0, tk.END)
            lb.selection_set(next_idx)
            lb.activate(next_idx)
            lb.see(next_idx)
        return "break"

    def open_selected(self, event):
        if self.results:
            lb = self.listbox
            cur = lb.curselection()
            idx = cur[0] if cur else 0
            path = self.results[idx]
            if path == "Add directory to z":
                path = filedialog.askdirectory(title="Add directory to z")
            path = path.strip()
            add_to_z(path)
            open_in_explorer(path)
        self.destroy()
        return "break"

    def focus_destroy(self):
        if self.results:
            lb = self.listbox
            cur = lb.curselection()
            idx = cur[0] if cur else 0
            path = self.results[idx]
            if path == "Add directory to z":
                return
        self.destroy()

if __name__ == "__main__":
    app = VisualZApp()
    app.on_search()  # Trigger initial search to populate listbox
    app.mainloop()