import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import subprocess
import os

import sv_ttk
import threading, queue, time
import pprint
        
class PowerShellSession:
    def __init__(self):
        self.proc = subprocess.Popen(
            ["powershell", "-NoProfile", "-NoExit", "-WindowStyle", "Hidden"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW,
            universal_newlines=True
        )
        # check if the process started successfully
        if self.proc is None:
            raise RuntimeError("Failed to start PowerShell process.")
        
        self.output_queue = queue.Queue()
        self.delimiter = "END_OF_COMMAND_OUTPUT_VISUALZ" # Unique delimiter

        # Start a separate thread to read stdout
        self.stdout_thread = threading.Thread(target=self._read_stdout)
        self.stdout_thread.daemon = True # Thread will exit when main program exits
        self.stdout_thread.start()

        # Give PowerShell a moment to initialize and display its first prompt
        time.sleep(0.5)
        # Clear any initial output/prompt from the queue
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except queue.Empty:
                break

    def _read_stdout(self):
        while True:
            try:
                line = self.proc.stdout.readline()
                if line:
                    self.output_queue.put(line)
                else:
                    break # stdout closed
            except ValueError:
                break # stdin/stdout/stderr pipes are closed

    def run_command(self, command):
        # Send the command followed by the delimiter
        self.proc.stdout.flush()  # Ensure stdout is flushed before writing
        self.proc.stdin.write(command + "\n")
        self.proc.stdin.write(f'echo "{self.delimiter}"\n') # Echo the delimiter
        self.proc.stdin.flush()

        output = []
        while True:
            try:
                line = self.output_queue.get(timeout=5) # Add a timeout to prevent infinite waiting
                line_stripped = line.strip()
                if line_stripped == self.delimiter:
                    break # Found the delimiter, command output has ended
                if line_stripped: # Only add non-empty lines that are not the delimiter
                    output.append(line_stripped)
            except queue.Empty:
                print("Timeout waiting for command output or delimiter.")
                break # Timeout, something went wrong or command took too long
            except Exception as e:
                print(f"Error reading from queue: {e}")
                break
        return output

    def close(self):
        if self.proc.poll() is None: # Check if process is still running
            try:
                self.proc.stdin.write("exit\n")
                self.proc.stdin.flush()
                self.proc.terminate()
                self.proc.wait(timeout=5) # Wait for the process to terminate
            except Exception as e:
                print(f"Error closing PowerShell session: {e}")

def list_files(query):
    try:
        ps_command = f'z {query} -ListFiles'
        lines = ps_session.run_command(ps_command)
        valid_paths = []
        
        for line in lines:
            line = line.strip()
            
            part = line.split(" ", 1)[-1]  # Get the part after the first space
            part = part[:-19]
            part.strip()  # Remove any trailing spaces
            
            if os.path.exists(part):
                valid_paths.append(part)
        valid_paths.append("Add directory to z")  # Add "Add directory to z manually" option
        return valid_paths
        
    except Exception:
        print("Error executing z command or processing output.")
        return []

def open_in_explorer(path):
    # Open Windows Explorer at the given path
    os.startfile(path)
    
def add_to_z(path):
    try:
        ps_command = f'z {path}'
        ps_session.run_command(ps_command)
    except Exception as e:
        print(f"Error adding path to z: {e}")

class VisualZApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VisualZ Search")
        self.geometry("500x150")
        self.overrideredirect(True)  # Remove native title bar
        self.attributes('-topmost', True)  # Keep window always on top
        self.configure(bg="#161A20")
        # self.style = ttk.Style(self)
        sv_ttk.use_dark_theme()
        
        # Center window on screen
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Custom title bar
        title_bar = tk.Frame(self, bg="#222831", relief="raised", bd=0, height=28)
        title_bar.pack(fill=tk.X, side=tk.TOP)

        title_label = tk.Label(title_bar, text="VisualZ Search", bg="#222831", fg="#ececec", font=("Segoe UI", 11, "bold"))
        title_label.pack(side=tk.LEFT, padx=10)

        btn_close = tk.Button(title_bar, text="✕", bg="#222831", fg="#ececec", bd=0, font=("Segoe UI", 10), command=self.destroy)
        btn_close.pack(side=tk.RIGHT, padx=2)

        # Allow window dragging
        def start_move(event):
            self.x = event.x
            self.y = event.y
        def stop_move(event):
            self.x = None
            self.y = None
        def do_move(event):
            x = self.winfo_pointerx() - self.x
            y = self.winfo_pointery() - self.y
            self.geometry(f"+{x}+{y}")

        title_bar.bind("<ButtonPress-1>", start_move)
        title_bar.bind("<ButtonRelease-1>", stop_move)
        title_bar.bind("<B1-Motion>", do_move)

        self.search_var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.search_var, width=40)
        self.entry.pack(pady=5)
        self.entry.focus()

        #make the listbox dark themed
        self.listbox = tk.Listbox(self, font=("Cascadia Mono", 12), height=3, bg="#393e46", fg="#ececec", selectbackground="#005d82", selectforeground="#222831", bd=0, highlightthickness=0)
        self.listbox.pack(fill=tk.X, padx=20)
        self.listbox.pack_forget()  # Hide initially

        self.search_var.trace_add('write', self.on_search)
        self.entry.bind("<Down>", self.focus_listbox)
        self.entry.bind("<Tab>", self.select_next)
        self.entry.bind("<Return>", self.open_selected)
        self.entry.bind("<Escape>", lambda e: self.destroy())
        self.listbox.bind("<Return>", self.open_selected)
        self.listbox.bind("<Tab>", self.select_next)
        self.listbox.bind("<Double-Button-1>", self.open_selected)
        self.listbox.bind("<Escape>", lambda e: self.destroy())

        self.results = []

    def on_search(self, *args):
        query = self.search_var.get()
        self.results = list_files(query)
        self.listbox.delete(0, tk.END)
        for item in self.results:
            if item == "Add directory to z": display_item = "Add directory to z"
            else:
                # if the item has more than 4 parts, display only the first two and last two parts
                if len(item.split(os.sep)) > 4:
                    display_item = os.path.splitdrive(item)[0] + os.sep + item.split(os.sep)[1].strip() + os.sep + "..." + os.sep + item.split(os.sep)[-2].strip() + os.sep + os.path.basename(item)
                else:
                    display_item = item
            self.listbox.insert(tk.END, display_item)
            # self.listbox.insert(tk.END, item)
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

    def open_selected(self, event):
        if self.results:
            lb = self.listbox
            cur = lb.curselection()
            idx = cur[0] if cur else 0
            path = self.results[idx]
            if path == "Add directory to z":
                # If "Add directory to z" is selected, open a tk selectfolder dialog
                path = filedialog.askdirectory(title="Add directory to z")
            
            add_to_z(path)
            open_in_explorer(path)
            
            self.destroy()  # Close the app after opening the path
        return "break"

if __name__ == "__main__":
    ps_session = PowerShellSession()
    
    app = VisualZApp()
    app.mainloop()
    
    ps_session.close()