from __future__ import annotations

import gzip
import struct
from collections.abc import Callable, Generator
from pathlib import Path
from tkinter import filedialog, Toplevel
from tkinter.ttk import Treeview
from typing import BinaryIO, TYPE_CHECKING

from tksheet import Sheet

from SSConstants import SS_SEQ_LAYOUTS

if TYPE_CHECKING:
    from SSTypes import SSData, SSSeq


def ss_data_write_gzipped(data: SSData) -> None:
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


def ss_data_write_encrypted(data: SSData) -> None:
    path = filedialog.asksaveasfilename(
        initialfile=f"{data.path.name.split(".")[0]}",
        filetypes=[("SSRG Unpacked Data Files", "")],
    )
    if not path:
        return
    path = Path(path)

    with path.open("wb") as f:
        f.write(data.encrypted)


def ss_data_write_decrypted(data: SSData) -> None:
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


def ss_seq_read_int(seq: BinaryIO) -> int:
    return struct.unpack("<I", seq.read(4))[0]


def ss_seq_read_float(seq: BinaryIO) -> float:
    return struct.unpack("<f", seq.read(4))[0]


def ss_seq_read_double(seq: BinaryIO) -> float:
    return struct.unpack("<d", seq.read(8))[0]


def ss_seq_skip_padding(seq: BinaryIO, layout: int) -> None:
    seq.seek(SS_SEQ_LAYOUTS[layout]["padd_size"], 1)


def ss_event_name(code: int):
    match code:
        case 0x00:
            return "Tap"
        case 0x0B:
            return "Group 1 Slider Start"
        case 0x15:
            return "Group 2 Slider Start"
        case c if c in range(0x00_00_00_16, 0x7F_FF_FF_FF):
            return "Group 2 Slider Continue"
        case _:
            return "Group 1 Slider Continue"


def ss_sequencer_folder_data(
    sheet: Sheet,
    root: Toplevel,
    seqs: Generator[Path, None, None],
    stop: Callable,
):
    from SSTypes import SSSeq

    for seq in seqs:
        try:
            seq = SSSeq(seq)
            sheet.data += [
                [
                    seq.path.name,
                    seq.SEQData_Object[0]["data"].replace("\0", ""),
                    seq.event_transients["noteCount"],
                    seq.event_transients["noteCountRaw"],
                    seq.event_transients["invalidCount"],
                ]
            ]

            if stop():
                break
        except Exception:
            pass

    if not stop():
        sheet.set_all_cell_sizes_to_text()
        root.minsize(sum(sheet.get_column_widths()) + 20, 291)


def ss_sequencer_tempo_data(tree: Treeview, seq: SSSeq, stop: Callable):
    for idx, tmp in enumerate(seq.SEQData_Tempo):
        tree.insert(
            "",
            "end",
            values=(
                idx,
                tmp["tick"],
                tmp["tickEnd"],
                tmp["sec"],
                tmp["secEnd"],
                tmp["beatPerMinute"],
                tmp["beatPerMeasure"],
                tmp["measurePerBeat"],
                tmp["measurePerTick"],
                tmp["tickPerMeasure"],
                tmp["beatPerSec"],
                tmp["secPerBeat"],
                tmp["tickPerSec"],
                tmp["secPerTick"],
                tmp["measurePerSec"],
                tmp["secPerMeasure"],
                tmp["measureStart"],
                tmp["measureCount"],
            ),
        )

        if stop():
            break


def ss_sequencer_object_data(tree: Treeview, seq: SSSeq, stop: Callable):
    for idx, obj in enumerate(seq.SEQData_Object):
        tree.insert(
            "", "end", values=(idx, obj["property"], obj["dataLen"], obj["data"])
        )

        if stop():
            break


def ss_sequencer_channel_data(tree: Treeview, seq: SSSeq, stop: Callable):
    for idx, channel in enumerate(seq.SEQData_Channel):
        tree.insert("", "end", values=(idx, channel["eventCount"], channel["property"]))

        if stop():
            break


def ss_sequencer_event_data(tree: Treeview, seq: SSSeq, stop: Callable):
    for event in seq.SEQData_Event:
        tree.insert(
            "",
            "end",
            values=(
                event["tick"],
                event["duration"],
                event["channelId"],
                event["objectId"],
                f"{event["property"]} (0x{event["property"]:X})",
                event["description"],
            ),
        )

        if stop():
            break
