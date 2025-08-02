# VisualZ

**VisualZ** is a fast, beautiful search interface for your directories using a Python implementation of the `z` algorithm. It provides a minimal, always-on-top window with a search bar and dropdown for quick navigation to your most-used folders.

<p align="center">
<img width="496" height="204" alt="image" src="https://github.com/user-attachments/assets/cc245705-e962-4f1a-91ec-f85f3e4442bb" />
</p>

## Features

* **Instant search:** As you type, VisualZ's internal algorithm finds and shows matching directories from your history.

* **Dropdown navigation:** Use **Tab** or **Down** to cycle results, and **Enter** to open the selected path in Explorer.

* **Add new directories:** If a folder is not in your history, you can optionally add it from the interface. After a while, the directory list will be populated with your most-visited folders.

* **Always on top:** The window stays above other windows for quick access.

* **Beautiful dark UI:** Custom title bar and modern styling.

* **No console window:** Launches as a GUI app without a terminal.

## Dependencies

* **Windows only** (for now)

* **Python** (<https://www.python.org/downloads/>)

## Installation

1. **Install Python**
   Download and install Python from [python.org](https://www.python.org/downloads/).

3. **Clone or download VisualZ**
    Clone the repository or download the ZIP file from here.

## How to Launch VisualZ

### Option 1: Shortcut with `pythonw.exe`

1. **Create a shortcut**

* Right-click in your folder, choose **New > Shortcut**.

* For the location, enter:

  ```
  pythonw.exe "X:/path/to/visualz.pyw"
  ```

  *(Adjust the path as needed.)*

2. **Name your shortcut**
For example, "VisualZ".

3. **(Optional) Assign a hotkey**

* Right-click the shortcut, choose **Properties**.

* Set a shortcut key (e.g., `Ctrl+Alt+Z`).
  *(Windows does not support Win+Z natively; use `Ctrl+Alt+Z` or a tool like AutoHotkey for Win+Z.)*

4. **(Optional) Add the shortcut to your taskbar**

* Drag the shortcut to your taskbar for quick access.

## Usage

* **Type to search:** Start typing a folder name; results appear instantly based on the z algorithm.

* **Navigate:** Use **Tab** or **Shift+Tab** to cycle through results.

* **Open:** Press **Enter** to open the selected folder in Explorer.

* **Add directory:** Select "Add directory to history" to add a new folder.

* **Close:** Press **Escape**.

## Theming

VisualZ uses a custom color palette for a modern look. You can modify the `themePalette` class in `visualz.pyw` to change colors.
You can take inspiration from [Color Hunt](https://colorhunt.co/) for color combinations.

## Notes

* VisualZ is designed for Windows.

* If you want a standalone `.exe`, use [PyInstaller](https://pyinstaller.org/en/stable/) with the `--windowed` option.

**Enjoy fast, beautiful folder search!**
