# VisualZ

**VisualZ** is a fast, beautiful search interface for your directories using a Python implementation of the `z` algorithm. It provides a minimal, always-on-top window with a search bar and dropdown for quick navigation to your most-used folders.

<p align="center">
<img width="496" height="204" alt="image" src="https://github.com/user-attachments/assets/cc245705-e962-4f1a-91ec-f85f3e4442bb" />
</p>

## Features

* **Instant search:** As you type, VisualZ's internal algorithm finds and shows matching directories from your history.

* **Dropdown navigation:** Use **Tab** or **Shift+Tab** to cycle results, and **Enter** to open the selected path in Explorer.

* **Add new directories:** If a folder is not in your history, you can optionally add it from the interface. After a while, the directory list will be populated with your most-visited folders.

* **Always on top:** The window stays above other windows for quick access.

* **Beautiful UI:** Custom title bar and modern styling, see [theming](#theming) for details.

* **No console window:** Launches as a GUI app without a terminal.

## Dependencies

* **Windows tested** (for now)

* **Python** (<https://www.python.org/downloads/>)

* **Tkinter**

## Installation

1. **Install Python**
   Download and install Python from [python.org](https://www.python.org/downloads/).

3. **Clone or download VisualZ**
    Clone the repository or download the ZIP file from here.

## How to Launch VisualZ

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

* **Change theme:** Press `Ctrl+t` to cycle through available themes.

* **Toggle last rule:** Press `Ctrl+l` to toggle the last component matching rule see **algorithm.md**.

* **Show help:** Press `Ctrl+h` to display available keyboard shortcuts.

## Theming

VisualZ uses a custom color palette for a modern look. You can add your own themes adding entries to the `themes.json` file in the same directory as `visualz.pyw`.
You can take inspiration from [Color Hunt](https://colorhunt.co/) for color combinations.

<p align="center">
<img width="387" height="125" alt="image" src="https://github.com/user-attachments/assets/a32d6bf0-dddb-471d-bc13-393e416d4270" />
</p>

It is possible to change the theme by pressing `Ctrl+t` or `Control+t` (Mac) while VisualZ is running. This will cycle through the available themes in `themes.json`, the last theme being used will be saved for the next launch.

If you want to add a new theme, you can do so by editing the `themes.json` file. The format is simple:

```json
{
    "theme_name": {
        "dominant": "#color",
        "accent": "#color",
        "secondary": "#color",
        "font": "font_name"
    }
}
``` 
**Enjoy fast, beautiful folder search!**

## Notes

* VisualZ is designed in Windows, should work in linux and macOs.

* If you want a standalone `.exe`, use [PyInstaller](https://pyinstaller.org/en/stable/) with the `--windowed` option.

The database needs time to populate with your most-used folders so the first times using it you may not see many results and you will have to add directories manually. After a while, it will become more useful as it learns from your usage patterns. 
If you want to quikly populate the database you can call the `populate_by_traversing` method in the `zoxide.py` file, this will traverse your filesystem starting from the root directory you provide and add all sub directories to the history. This is not recommended for large filesystems as it will fill the history with many directories you may never use reaching the max_age limit (see [algorithm.md](algorithm.md) for more details).

We are currently working on a more efficient way to automatically populate the history based on your usage patterns or user preferences. **We are open to contributions and suggestions for improving this feature**.

