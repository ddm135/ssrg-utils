import gzip
from pathlib import Path
from tkinter import filedialog

from SSTypes import SSData


def ss_write_gzipped(data: SSData):
    path = filedialog.asksaveasfilename(
        initialfile=f"{data.path.name.split(".")[0]}.bin",
        filetypes=[("SSRG Packed Data Files", ".bin")],
        defaultextension=".bin",
    )
    if not path:
        return
    path = Path(path)

    with path.open("wb") as f:
        gz = gzip.GzipFile("", "wb", 6, f, 0.0)
        gz.write(data.encrypted)
        gz.close()


def ss_write_encrypted(data: SSData):
    path = filedialog.asksaveasfilename(
        initialfile=f"{data.path.name.split(".")[0]}",
        filetypes=[("SSRG Unpacked Data Files", "")],
    )
    if not path:
        return
    path = Path(path)

    with path.open("wb") as f:
        f.write(data.encrypted)


def ss_write_decrypted(data: SSData):
    path = filedialog.asksaveasfilename(
        initialfile=f"{data.path.name.split(".")[0]}.json",
        filetypes=[("JSON Files", ".json")],
        defaultextension=".json",
    )
    if not path:
        return
    path = Path(path)

    with path.open("wb") as f:
        f.write(data.decrypted)
