import tkinter as tk
from tkinter import filedialog, Toplevel
from tkinter.ttk import Button, Label

from SSHelpers import ss_write_decrypted, ss_write_encrypted, ss_write_gzipped
from SSTypes import SSData


def main():
    tk_root = tk.Tk()
    tk_root.withdraw()

    path = filedialog.askopenfilename(title="Select data file")
    if not path:
        return

    data = SSData(path)

    win = Toplevel()
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
        command=tk_root.destroy,
    ).pack(padx=(5, 15), pady=10, side="right")
    Button(
        win,
        text="Decrypted JSON",
        command=lambda: ss_write_decrypted(data),
    ).pack(padx=5, pady=10, side="right")
    Button(
        win,
        text="Encrypted JSON",
        command=lambda: ss_write_encrypted(data),
    ).pack(padx=5, pady=10, side="right")
    Button(
        win,
        text="GZipped Encrypted JSON",
        command=lambda: ss_write_gzipped(data),
    ).pack(padx=(15, 5), pady=10, side="right")
    win.protocol("WM_DELETE_WINDOW", tk_root.destroy)
    win.resizable(width=False, height=False)
    tk_root.mainloop()


if __name__ == "__main__":
    main()
