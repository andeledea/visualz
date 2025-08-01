# VisualZ

**VisualZ** is a fast, beautiful search interface for your directories using the [z](https://github.com/vincpa/z) tool. It provides a minimal, always-on-top window with a search bar and dropdown for quick navigation to your most-used folders.

## Features

- **Instant search:** As you type, VisualZ calls `z -ListFiles` and shows matching directories.
- **Dropdown navigation:** Use Tab/Down to cycle results, Enter to open the selected path in Explorer.
- **Add new directories:** z needs to create a cd history, if the folder is not found optionally add a new directory to z from the interface. After a while the directory list will be populated with your visited folders.
- **Always on top:** The window stays above other windows for quick access.
- **Beautiful dark UI:** Custom title bar and modern styling.
- **No console window:** Launches as a GUI app without a terminal.

## Dependencies

- **Windows only** (for now)
- [Python](https://www.python.org/downloads/)
- [z](https://github.com/vincpa/z) (must be installed and available in your PATH)
- [`sv_ttk`](https://pypi.org/project/sv-ttk/) (`pip install sv-ttk`)

## Installation

1. **Install Python**  
   Download and install Python from [python.org](https://www.python.org/downloads/).

2. **Install z**  
   Follow instructions at [z's GitHub](https://github.com/vincpa/z) to install and set up z for Windows.

3. **Install sv_ttk**  
   Open a terminal and run:
   ```
   pip install sv-ttk
   ```

4. **Clone or download VisualZ**  
   Place `visualz.pyw` in your desired folder.

## How to Launch VisualZ

### Option 1: Shortcut with pythonw.exe

1. **Create a shortcut**  
   - Right-click in your folder, choose **New > Shortcut**.
   - For the location, enter:
     ```
     pythonw.exe "C:\Users\l.ribotta\Documents\visualz\visualz.pyw"
     ```
     *(Adjust the path as needed.)*

2. **Name your shortcut**  
   For example, "VisualZ".

3. **(Optional) Assign a hotkey**  
   - Right-click the shortcut, choose **Properties**.
   - Set a shortcut key (e.g., `Ctrl+Alt+Z`).  
     *(Windows does not support Win+Z natively; use Ctrl+Alt+Z or a tool like AutoHotkey for Win+Z.)*

4. **(Optional) Add the shortcut to your taskbar**  
   - Drag the shortcut to your taskbar for quick access. 

### Option 2: Double-click

Just double-click `visualz.pyw` to launch the search window.

## Usage

- **Type to search:** Start typing a folder name; results appear instantly based on z algorithm.
- **Navigate:** Use Tab or Down to cycle through results.
- **Open:** Press Enter to open the selected folder in Explorer.
- **Add directory:** Select "Add directory to z" to add a new folder to the z history.
- **Close:** Press Escape or click the close button.

## Notes

- VisualZ is designed for Windows and requires z to be installed and working.
- If you want a standalone `.exe`, use [PyInstaller](https://pyinstaller.org/en/stable/) with the `--windowed` option.

---

**Enjoy fast, beautiful folder search