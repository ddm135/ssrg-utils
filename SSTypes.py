import binascii
import gzip
import json
from base64 import b64decode, b64encode
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from Cryptodome.Util.Padding import pad, unpad

from SSConstants import (
    SS_CRYPT,
    SS_SEQ_TYPES,
    SS_EVENT_COMMON_PROPERTIES,
    SS_SEQ_LAYOUTS,
)
from SSHelpers import (
    ss_seq_read_int,
    ss_seq_read_double,
    ss_seq_skip_padding,
    ss_seq_read_float,
    ss_event_name,
)


@dataclass(frozen=True)
class SSData:
    path: Path = None
    encrypted: bytes = None
    decrypted: bytes = None
    json: list[dict] = None

    def __init__(self, path: str | Path):
        if isinstance(path, str):
            path = Path(path)
        object.__setattr__(self, "path", path)

        with gzip.open(self.path, "rb") as gzipped:
            try:
                file_content = gzipped.read()
            except gzip.BadGzipFile:
                with path.open("rb") as file:
                    file_content = file.read()

        try:
            file_decrypted = (
                unpad(SS_CRYPT.decrypt(b64decode(file_content)), 16)
                .replace(rb"\/", rb"/")
                .replace(rb"\u", rb"ddm135-u")
            )
            object.__setattr__(self, "encrypted", file_content)
            tmp_json = json.loads(file_decrypted)
            object.__setattr__(
                self,
                "decrypted",
                (
                    json.dumps(tmp_json, indent="\t", ensure_ascii=False)
                    .replace(r"ddm135-u", r"\u")
                    .encode("utf8")
                ),
            )
            object.__setattr__(self, "json", json.loads(self.decrypted))
        except (ValueError, binascii.Error):
            object.__setattr__(self, "decrypted", file_content.replace(b"\r", b""))
            object.__setattr__(self, "json", json.loads(self.decrypted))
            tmp_json = json.loads(self.decrypted.replace(rb"\u", rb"ddm135-u"))
            file_content = (
                json.dumps(tmp_json, separators=(",", ":"), ensure_ascii=False)
                .replace(r"/", r"\/")
                .replace(r"ddm135-u", r"\u")
                .encode("utf8")
            )
            file_encrypted = b64encode(SS_CRYPT.encrypt(pad(file_content, 16)))
            object.__setattr__(self, "encrypted", file_encrypted)


@dataclass(frozen=True)
class SSSeq:
    path: Path = None
    SEQData_Info: dict = field(default_factory=dict)
    SEQData_Tempo: list[dict] = field(default_factory=list)
    SEQData_Object: list[dict] = field(default_factory=list)
    SEQData_Channel: list[dict] = field(default_factory=list)
    SEQData_Event: list[dict] = field(default_factory=list)
    event_transients: dict = field(default_factory=dict)

    def __init__(self, path: str | Path):
        if isinstance(path, str):
            path = Path(path)
        object.__setattr__(self, "path", path)
        object.__setattr__(self, "SEQData_Info", {})
        object.__setattr__(self, "SEQData_Tempo", [])
        object.__setattr__(self, "SEQData_Object", [])
        object.__setattr__(self, "SEQData_Channel", [])
        object.__setattr__(self, "SEQData_Event", [])
        object.__setattr__(self, "event_transients", {})

        with path.open("rb") as seq:
            self.SEQData_Info["layout"] = ss_seq_read_int(seq)

            if self.SEQData_Info["layout"] not in SS_SEQ_LAYOUTS:
                raise Exception(f"Not a valid SSRG beatmap file: {path}")

            self.SEQData_Info["tickLength"] = ss_seq_read_int(seq)
            self.SEQData_Info["secLength"] = ss_seq_read_double(seq)
            self.SEQData_Info["tickPerBeat"] = ss_seq_read_int(seq)
            ss_seq_skip_padding(seq, self.SEQData_Info["layout"])
            self.SEQData_Info["beatPerTick"] = ss_seq_read_double(seq)
            self.SEQData_Info["tempoCount"] = ss_seq_read_int(seq)
            self.SEQData_Info["objectCount"] = ss_seq_read_int(seq)
            self.SEQData_Info["channelCount"] = ss_seq_read_int(seq)
            self.SEQData_Info["eventCount"] = ss_seq_read_int(seq)
            self.SEQData_Info["measureCount"] = ss_seq_read_int(seq)
            self.SEQData_Info["beatCount"] = ss_seq_read_int(seq)
            self.SEQData_Info["type"] = ss_seq_read_int(seq)
            ss_seq_skip_padding(seq, self.SEQData_Info["layout"])

            for i in range(self.SEQData_Info["tempoCount"]):
                tempo = {}
                tempo["tick"] = ss_seq_read_int(seq)
                tempo["tickEnd"] = ss_seq_read_int(seq)
                tempo["sec"] = ss_seq_read_float(seq)
                tempo["secEnd"] = ss_seq_read_float(seq)
                tempo["beatPerMinute"] = ss_seq_read_double(seq)
                tempo["beatPerMeasure"] = ss_seq_read_int(seq)
                ss_seq_skip_padding(seq, self.SEQData_Info["layout"])  # padd_0
                tempo["measurePerBeat"] = ss_seq_read_double(seq)
                tempo["measurePerTick"] = ss_seq_read_double(seq)
                tempo["tickPerMeasure"] = ss_seq_read_int(seq)
                ss_seq_skip_padding(seq, self.SEQData_Info["layout"])  # padd_1
                tempo["beatPerSec"] = ss_seq_read_double(seq)
                tempo["secPerBeat"] = ss_seq_read_double(seq)
                tempo["tickPerSec"] = ss_seq_read_double(seq)
                tempo["secPerTick"] = ss_seq_read_double(seq)
                tempo["measurePerSec"] = ss_seq_read_double(seq)
                tempo["secPerMeasure"] = ss_seq_read_double(seq)
                tempo["measureStart"] = ss_seq_read_int(seq)
                tempo["measureCount"] = ss_seq_read_int(seq)
                self.SEQData_Tempo.append(tempo)

            last = {"dataLen": ss_seq_read_int(seq)}
            if last["dataLen"]:
                last["data"] = seq.read(last["dataLen"]).decode("utf8")
            for i in range(self.SEQData_Info["objectCount"] - 1):
                obj = {
                    "property": ss_seq_read_int(seq),
                    "dataLen": ss_seq_read_int(seq),
                }
                if obj["dataLen"]:
                    obj["data"] = seq.read(obj["dataLen"]).decode("utf8")
                    self.SEQData_Object.append(obj)
            last["property"] = ss_seq_read_int(seq)
            if last["dataLen"]:
                last = {"property": last.pop("property"), **last}
                self.SEQData_Object.append(last)

            for i in range(self.SEQData_Info["channelCount"]):
                channel = {
                    "eventCount": ss_seq_read_int(seq),
                    "property": ss_seq_read_int(seq),
                }
                self.SEQData_Channel.append(channel)

            self.event_transients["startEvent"] = False
            self.event_transients["endEvent"] = False
            self.event_transients["noteCountRaw"] = 0
            self.event_transients["noteCount"] = 0
            self.event_transients["invalidCount"] = 0

            for i in range(self.SEQData_Info["eventCount"]):
                event = {
                    "tick": ss_seq_read_int(seq),
                    "duration": ss_seq_read_int(seq),
                    "channelId": ss_seq_read_int(seq),
                    "objectId": ss_seq_read_int(seq),
                    "property": ss_seq_read_int(seq),
                }

                if i == 0:
                    if (
                        event["duration"] == 0
                        and event["channelId"] == 31
                        and event["objectId"] == 1
                        # and __event['property'] == 0
                    ):
                        event["description"] = "Start"
                        self.event_transients["startEvent"] = True
                    else:
                        event["description"] = "Invalid"
                        self.event_transients["invalidCount"] += 1
                elif i == self.SEQData_Info["eventCount"] - 1:
                    if (
                        event["duration"] == 0
                        and event["channelId"] == 13
                        and event["objectId"] == 0
                        and event["property"] == 0
                    ):
                        event["description"] = "End"
                        self.event_transients["endEvent"] = True
                    else:
                        event["description"] = "Invalid"
                        self.event_transients["invalidCount"] += 1
                else:
                    if (
                        event["tick"] in range(self.SEQData_Info["tickLength"])
                        and event["duration"] == 0
                        and event["channelId"]
                        in SS_SEQ_TYPES[self.SEQData_Info["type"]]["lanes"]
                        # and event['objectId'] in (0, 2, 5, 8, 15, 16, 30, 34)
                    ):
                        event["description"] = ss_event_name(event["property"])
                        self.event_transients["noteCountRaw"] += 1

                        if event["property"] in SS_EVENT_COMMON_PROPERTIES:
                            self.event_transients["noteCount"] += 1
                    else:
                        event["description"] = "Invalid"
                        self.event_transients["invalidCount"] += 1
                ss_seq_skip_padding(seq, self.SEQData_Info["layout"])
                self.SEQData_Event.append(event)


@dataclass
class SSSong:
    code: int = None
    artist_kr: str = None
    artist_jp: str = None
    artist_en: str = None
    name_kr: str = None
    name_jp: str = None
    name_en: str = None
    duration: int = None
    easy: int = None
    normal: int = None
    hard: int = None
    date: datetime = None
