import struct
from enum import Enum
from typing import Type


def unpack_little_endian(data: bytes, new_type: Type):
    if new_type == str:
        return data.decode('utf-8')
    if new_type is None or len(data) == 0:
        return None

    length = len(data)
    if length == 1:
        code = 'B'
    elif length == 2:
        code = 'H'
    elif length == 4:
        code = 'I'
    else:
        raise
    fmt = f'<{code}'
    return struct.unpack(fmt, data)[0]


class GeneralPurposeBitMasks(Enum):
    # General purpose bit flags
    # Zip Appnote: 4.4.4 general purpose bit flag: (2 bytes)
    ENCRYPTED = 1 << 0
    # Bits 1 and 2 have different meanings depending on the compression used.
    # COMPRESS_OPTION_1 = 1 << 1
    # COMPRESS_OPTION_2 = 1 << 2
    # USE_DATA_DESCRIPTOR: If set, crc-32, compressed size and uncompressed
    # size are zero in the local header and the real values are written in the data
    # descriptor immediately following the compressed data.
    USE_DATA_DESCRIPTOR = 1 << 3
    # Bit 4: Reserved for use with compression method 8, for enhanced deflating.
    # RESERVED_BIT_4 = 1 << 4
    COMPRESSED_PATCH = 1 << 5
    STRONG_ENCRYPTION = 1 << 6
    # UNUSED_BIT_7 = 1 << 7
    # UNUSED_BIT_8 = 1 << 8
    # UNUSED_BIT_9 = 1 << 9
    # UNUSED_BIT_10 = 1 << 10
    UTF_FILENAME = 1 << 11
    # Bit 12: Reserved by PKWARE for enhanced compression.
    # RESERVED_BIT_12 = 1 << 12
    # ENCRYPTED_CENTRAL_DIR = 1 << 13
    # Bit 14, 15: Reserved by PKWARE
    # RESERVED_BIT_14 = 1 << 14
    # RESERVED_BIT_15 = 1 << 15

