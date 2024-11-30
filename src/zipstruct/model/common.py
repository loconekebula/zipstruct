import struct
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

