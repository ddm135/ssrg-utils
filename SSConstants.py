from Cryptodome.Cipher import AES

SS_CRYPT = AES.new("WnFKN1v_gUcgmUVZnjjjGXGwk557zBSO".encode("utf8"), AES.MODE_ECB)

SS_SEQ_LAYOUTS = {
    0x65: {"name": "Legacy", "padd_size": 0},
    0x66: {"name": "Latest", "padd_size": 4},
}

SS_SEQ_TYPES = {
    0x68: {"name": "Easy", "lanes": range(0, 13, 4)},
    0x6B: {"name": "Normal", "lanes": range(0, 13, 2)},
    0x71: {"name": "Hard", "lanes": range(13)},
}

SS_EVENT_COMMON_PROPERTIES = (0x00, 0x0B, 0x0C, 0x03, 0x15, 0x16)
