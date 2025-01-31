import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, Toplevel
from tkinter.ttk import Button, Label

from SSHelpers import (
    ss_data_write_decrypted,
    ss_data_write_encrypted,
    ss_data_write_gzipped,
)
from SSTypes import SSData


def opened(root: tk.Tk):
    path = filedialog.askopenfilename(title="Select data file")
    if not path:
        return
    path = Path(path)

    try:
        data = SSData(path)
    except Exception as e:
        messagebox.showerror(
            title="Error", message=f"Not a valid SSRG data file: {path}"
        )
        return

    root.withdraw()
    win = Toplevel(root)
    win.title("Save As")
    Label(
        win,
        text="Which form would you like to save the data file as?",
        padding=10,
        background="white",
        anchor="center",
    ).pack(fill="x")
    Button(
        win,
        text="Close",
        command=root.destroy,
    ).pack(padx=(5, 15), pady=10, side="right")
    Button(
        win,
        text="Decrypted JSON",
        command=lambda: ss_data_write_decrypted(data),
    ).pack(padx=5, pady=10, side="right")
    Button(
        win,
        text="Encrypted JSON",
        command=lambda: ss_data_write_encrypted(data),
    ).pack(padx=5, pady=10, side="right")
    Button(
        win,
        text="GZipped Encrypted JSON",
        command=lambda: ss_data_write_gzipped(data),
    ).pack(padx=(15, 5), pady=10, side="right")
    win.protocol("WM_DELETE_WINDOW", root.destroy)
    win.resizable(False, False)


def main():
    tk_root = tk.Tk()
    tk_root.title("Open")
    Button(tk_root, text="Open", command=lambda: opened(tk_root)).pack(
        padx=15, pady=10, side="top"
    )
    tk_root.protocol("WM_DELETE_WINDOW", tk_root.destroy)
    tk_root.resizable(False, False)
    tk_root.mainloop()


if __name__ == "__main__":
    main()
