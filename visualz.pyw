import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import os
import json

from zoxide import ZoxideDB

# https://colorhunt.co/
class themePalette:
    font = ("Cascadia Mono", 12)
    
    dominant = "#113F67"
    accent = "#FDF5AA"
    secondary = "#34699A"
    
    def from_file(self, file_path, next=False):
        """
        Load theme from a file if needed
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Theme file {file_path} does not exist.")
        with open(file_path, "r", encoding="utf-8") as f:
            all = json.load(f)
            last_theme = all.get("last_theme", "Blallo")
            all_themes: dict = all["themes"]
            
        theme_name = last_theme
        
        if next:
            theme_names = list(all_themes.keys())
            if last_theme not in theme_names:
                last_theme = list(all_themes)[-1]
            next_index = (theme_names.index(last_theme) + 1) % len(theme_names)
            theme_name = theme_names[next_index]
        
        if theme_name not in all_themes:
            theme_name = list(all_themes)[0]
        
        theme = all_themes[theme_name]
        self.dominant = theme.get("dominant", self.dominant)
        self.accent = theme.get("accent", self.accent)
        self.secondary = theme.get("secondary", self.secondary)
        self.font = (theme.get("font", self.font), 12)
        
        all["last_theme"] = theme_name
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(all, f, indent=2) 
        return self

# Initialize ZoxideDB
db = ZoxideDB("zoxide_db.json")

# set Theme
current_theme = themePalette()

def list_files(query):
    try:
        results = db.search(query)
        valid_paths = [entry[0] for entry in results]
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
        # self.bind("<FocusOut>", lambda e: self.focus_destroy())

        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.search_var = tk.StringVar()
        
        self.entry = ttk.Entry(self, textvariable=self.search_var, width=40, justify="left")
        self.entry.pack(pady=15)
        self.entry.focus()

        self.listbox = tk.Listbox(self, height=3, bd=0, highlightthickness=0, activestyle="none")
        self.listbox.pack(fill=tk.X, padx=20)
        self.listbox.pack_forget()
        
        self.change_theme(next=False)

        self.search_var.trace_add('write', self.on_search)
        self.entry.bind("<Down>", self.focus_listbox)
        self.entry.bind("<Tab>", self.select_next)
        self.entry.bind("<Shift-Tab>", self.select_previous)
        self.entry.bind("<Return>", self.open_selected)
        self.entry.bind("<Control-t>", lambda e, n=True: self.change_theme(n))
        self.entry.bind("<Escape>", lambda e: self.destroy())

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
        
    def change_theme(self, next):
        current_theme.from_file("themes.json", next)
        
        self.configure(bg=current_theme.dominant, highlightthickness=3, highlightcolor=current_theme.accent)
        
        s = ttk.Style()
        s.theme_use("classic")
        s.configure("TEntry", 
                    foreground=current_theme.dominant, 
                    fieldbackground=current_theme.accent, 
                    font=current_theme.font, 
                    highlightthickness=0, 
                    highlightcolor=current_theme.secondary,
                    borderwidth=0,
                    insertcolor=current_theme.dominant,
                    padding=(4, 0, 0, 0)
                    )

        self.entry.configure(style="TEntry", font=current_theme.font)
        self.listbox.configure(font=current_theme.font, bg=current_theme.secondary, fg=current_theme.accent, selectbackground=current_theme.accent, selectforeground=current_theme.dominant)

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