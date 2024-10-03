import binascii
import gzip
import json
from base64 import b64decode, b64encode
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad


@dataclass
class SSData:
    path: Path = None
    encrypted: bytes = None
    decrypted: bytes = None
    json: list[dict] = None

    def __init__(self, path: str | Path):
        if isinstance(path, str):
            path = Path(path)
        self.path = path

        crypt = AES.new("WnFKN1v_gUcgmUVZnjjjGXGwk557zBSO".encode("utf8"), AES.MODE_ECB)
        with gzip.open(self.path, "rb") as gzipped:
            try:
                file_content = gzipped.read()
            except gzip.BadGzipFile:
                with path.open("rb") as file:
                    file_content = file.read()

        try:
            file_decrypted = (
                unpad(crypt.decrypt(b64decode(file_content)), 16)
                .replace(rb"\/", rb"/")
                .replace(rb"\u", rb"ddm135-u")
            )
            self.encrypted = file_content
            tmp_json = json.loads(file_decrypted)
            self.decrypted = (
                json.dumps(tmp_json, indent="\t", ensure_ascii=False)
                .replace(r"ddm135-u", r"\u")
                .encode("utf8")
            )
            self.json = json.loads(self.decrypted)
        except (ValueError, binascii.Error):
            self.decrypted = file_content.replace(b"\r", b"")
            self.json = json.loads(self.decrypted)
            tmp_json = json.loads(self.decrypted.replace(rb"\u", rb"ddm135-u"))
            file_content = (
                json.dumps(tmp_json, separators=(",", ":"), ensure_ascii=False)
                .replace(r"/", r"\/")
                .replace(r"ddm135-u", r"\u")
                .encode("utf8")
            )
            file_encrypted = b64encode(crypt.encrypt(pad(file_content, 16)))
            self.encrypted = file_encrypted


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
