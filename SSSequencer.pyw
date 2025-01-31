import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, Toplevel
from tkinter.ttk import Button, Frame, Label, Notebook, Scrollbar, Treeview

from tksheet import Sheet

from SSHelpers import (
    ss_sequencer_event_data,
    ss_sequencer_folder_data,
    ss_sequencer_object_data,
    ss_sequencer_channel_data,
    ss_sequencer_tempo_data,
)
from SSTypes import SSSeq


def folder_mode(root: tk.Tk):
    path = filedialog.askdirectory(title="Select beatmap folder")
    if not path:
        return
    path = Path(path)

    root.withdraw()
    seqs = path.rglob("*.seq", case_sensitive=True)
    stop_thread = False

    def destroy():
        root.destroy()
        nonlocal stop_thread
        stop_thread = True

    win = Toplevel(root)
    win.title("Sequencer")
    sheet = Sheet(
        win,
        show_top_left=False,
        show_row_index=False,
        headers=[
            "SEQ Name",
            "OGG Name",
            "Note Count",
            "Note Count Raw",
            "Invalid Count",
        ],
        empty_vertical=2,
        empty_horizontal=0,
    )
    sheet.enable_bindings(
        "single_select",
        "drag_select",
        "select_all",
        "column_select",
        "row_select",
        "double_click_column_resize",
        "column_width_resize",
        "row_width_resize",
        "column_height_resize",
        "row_height_resize",
        "double_click_row_resize",
        "copy",
    )
    sheet.pack(fill="both", expand=True)

    win.protocol("WM_DELETE_WINDOW", destroy)
    threading.Thread(
        target=ss_sequencer_folder_data, args=(sheet, win, seqs, lambda: stop_thread)
    ).start()


def file_mode(root: tk.Tk):
    path = filedialog.askopenfilename(
        title="Select beatmap file", filetypes=[("SSRG Beatmap Files", "*.seq")]
    )
    if not path:
        return
    path = Path(path)

    try:
        seq = SSSeq(path)
    except Exception as e:
        messagebox.showerror(title="Error", message=str(e))
        return

    root.withdraw()
    stop_thread = False

    def destroy():
        root.destroy()
        nonlocal stop_thread
        stop_thread = True

    win = Toplevel(root)
    win.title("Sequencer")
    notebook = Notebook(win)
    notebook.pack(fill="both", expand=True)

    info_tab = Frame(notebook)
    notebook.add(info_tab, text="General")

    for idx, (key, val) in enumerate(seq.SEQData_Info.items()):
        Label(info_tab, text=f"{key}:", padding=2).grid(
            row=idx, column=0, sticky="e", padx=(5, 0)
        )
        Label(info_tab, text=str(val), borderwidth=1, relief="sunken", padding=2).grid(
            row=idx, column=1, sticky="ew", padx=(0, 5)
        )
        info_tab.grid_rowconfigure(idx, weight=1)

    info_tab.grid_columnconfigure(0, weight=3)
    info_tab.grid_columnconfigure(1, weight=7)

    tempo_tab = Frame(notebook)
    notebook.add(tempo_tab, text="Tempos")

    tempo_tree = Treeview(tempo_tab, selectmode="browse")
    tempo_tree.pack(side="left", fill="both", expand=True)
    tempo_scroll = Scrollbar(tempo_tab, orient="vertical", command=tempo_tree.yview)
    tempo_scroll.pack(side="right", fill="y")
    tempo_tree.config(yscrollcommand=tempo_scroll.set)

    tempo_tree["columns"] = (
        "index",
        "tick",
        "tickEnd",
        "sec",
        "secEnd",
        "beatPerMinute",
        "beatPerMeasure",
        "measurePerBeat",
        "measurePerTick",
        "tickPerMeasure",
        "beatPerSec",
        "secPerBeat",
        "tickPerSec",
        "secPerTick",
        "measurePerSec",
        "secPerMeasure",
        "measureStart",
        "measureCount",
    )
    tempo_tree["show"] = "headings"
    for column in tempo_tree["columns"]:
        tempo_tree.column(column, width=120, stretch=False, anchor="center")
        tempo_tree.heading(column, text=column, anchor="center")
    tempo_tree.column("index", width=50, anchor="center")
    tempo_tree.column("tick", width=50, anchor="center")
    tempo_tree.column("tickEnd", width=50, anchor="center")
    tempo_tree.column("beatPerMinute", width=90, anchor="center")
    tempo_tree.column("beatPerMeasure", width=95, anchor="center")
    tempo_tree.column("measurePerBeat", width=95, anchor="center")
    tempo_tree.column("measurePerTick", width=90, anchor="center")
    tempo_tree.column("tickPerMeasure", width=90, anchor="center")
    tempo_tree.column("measureStart", width=85, anchor="center")
    tempo_tree.column("measureCount", width=85, anchor="center")

    threading.Thread(
        target=ss_sequencer_tempo_data, args=(tempo_tree, seq, lambda: stop_thread)
    ).start()

    object_tab = Frame(notebook)
    notebook.add(object_tab, text="Objects (Metadata)")

    object_tree = Treeview(object_tab, selectmode="browse")
    object_tree.pack(side="left", fill="both", expand=True)
    object_scroll = Scrollbar(object_tab, orient="vertical", command=object_tree.yview)
    object_scroll.pack(side="right", fill="y")
    object_tree.config(yscrollcommand=object_scroll.set)

    object_tree["columns"] = ("index", "property", "dataLen", "data")
    object_tree["show"] = "headings"
    for column in object_tree["columns"]:
        object_tree.column(column, width=100, stretch=False, anchor="center")
        object_tree.heading(column, text=column, anchor="center")
    object_tree.column("data", width=1440, anchor="w")
    object_tree.heading("data", anchor="w")

    threading.Thread(
        target=ss_sequencer_object_data, args=(object_tree, seq, lambda: stop_thread)
    ).start()

    channel_tab = Frame(notebook)
    notebook.add(channel_tab, text="Channels (Lanes)")

    channel_tree = Treeview(channel_tab, selectmode="browse")
    channel_tree.pack(side="left", fill="both", expand=True)
    channel_scroll = Scrollbar(
        channel_tab, orient="vertical", command=channel_tree.yview
    )
    channel_scroll.pack(side="right", fill="y")
    channel_tree.config(yscrollcommand=channel_scroll.set)

    channel_tree["columns"] = ("index", "eventCount", "property")
    channel_tree["show"] = "headings"
    for column in channel_tree["columns"]:
        channel_tree.column(column, width=580, stretch=False, anchor="center")
        channel_tree.heading(column, text=column, anchor="center")

    threading.Thread(
        target=ss_sequencer_channel_data, args=(channel_tree, seq, lambda: stop_thread)
    ).start()

    event_tab = Frame(notebook)
    notebook.add(event_tab, text="Events (Notes)")

    event_tree = Treeview(event_tab, selectmode="browse")
    event_tree.pack(side="left", fill="both", expand=True)
    event_scroll = Scrollbar(event_tab, orient="vertical", command=event_tree.yview)
    event_scroll.pack(side="right", fill="y")
    event_tree.config(yscrollcommand=event_scroll.set)

    event_tree["columns"] = (
        "tick",
        "duration",
        "channelId",
        "objectId",
        "property",
        "description",
    )
    event_tree["show"] = "headings"
    for column in event_tree["columns"]:
        event_tree.column(column, width=100, stretch=False, anchor="center")
        event_tree.heading(column, text=column, anchor="center")
    event_tree.column("description", width=1240, anchor="w")
    event_tree.heading("description", anchor="w")

    threading.Thread(
        target=ss_sequencer_event_data, args=(event_tree, seq, lambda: stop_thread)
    ).start()

    win.protocol("WM_DELETE_WINDOW", destroy)
    win.minsize(1763, 291)


def main():
    tk_root = tk.Tk()
    tk_root.title("Mode")
    Button(tk_root, text="File", command=lambda: file_mode(tk_root)).pack(
        padx=(15, 5), pady=10, side="left"
    )
    Button(tk_root, text="Folder", command=lambda: folder_mode(tk_root)).pack(
        padx=(5, 15), pady=10, side="right"
    )
    tk_root.protocol("WM_DELETE_WINDOW", tk_root.destroy)
    tk_root.resizable(False, False)
    tk_root.mainloop()


if __name__ == "__main__":
    main()
