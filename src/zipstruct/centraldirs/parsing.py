import struct
from typing import BinaryIO
from src.zipstruct.centraldirs.centraldir import (
    RawCentralDirectory, INT_CENTRAL_DIR_SIGNATURE, MIN_CENTRAL_DIR_LENGTH, CENTRAL_DIR_SIGNATURE
)
import logging
LOGGER = logging.getLogger("zipstruct")


def parse_central_directories(f: BinaryIO, start_offset: int):
    f.seek(start_offset, 0)

    signature = f.read(4)
    cds = []
    offset = start_offset
    LOGGER.debug(f"Started parsing central directories from byte: {offset}")
    while signature == CENTRAL_DIR_SIGNATURE:
        cd = parse_central_directory(f, offset)
        cds.append(cd)
        signature = f.read(4)
        offset += len(cd)
    LOGGER.debug(f"Stopped to parse central directories at byte {offset}, no central directory "
                 f"signature was found (bytes read: {signature})")
    total = sum([len(cd) for cd in cds])
    expected = offset - start_offset
    if total != expected:
        raise ValueError(f"'__len__' function of {RawCentralDirectory.__name__} may be bugged, expected len "
                         f"({expected}) is different from the total amount of byte parsed: {expected}")
    return cds


def parse_central_directory(f: BinaryIO, offset: int) -> RawCentralDirectory:
    # Seek to the start of the CentralDirectory and load it in memory
    f.seek(offset, 0)
    cd = f.read(MIN_CENTRAL_DIR_LENGTH)

    # Check size
    if len(cd) < MIN_CENTRAL_DIR_LENGTH:
        raise ValueError(f"Incomplete CentralDirectory record, found {len(cd)} bytes "
                         f"but minimum is {MIN_CENTRAL_DIR_LENGTH}.")

    # Check signature
    signature = struct.unpack('<I', cd[:4])[0]
    if signature != INT_CENTRAL_DIR_SIGNATURE:
        raise ValueError("Invalid 'Central Directory' signature")

    # Extract the comment, if any
    name_length = struct.unpack('<H', cd[28:30])[0]
    extra_length = struct.unpack('<H', cd[30:32])[0]
    comment_length = struct.unpack('<H', cd[32:34])[0]
    name = f.read(name_length)
    extra = f.read(extra_length)
    comment = f.read(comment_length)

    rcd = RawCentralDirectory(
        signature                       = cd[0:4],
        version_made_by                 = cd[4:6],
        version_needed_to_extract       = cd[6:8],
        general_purpose_flags           = cd[8:10],
        compression_method              = cd[10:12],
        last_mod_file_time              = cd[12:14],
        last_mod_file_date              = cd[14:16],
        crc32                           = cd[16:20],
        compressed_size                 = cd[20:24],
        uncompressed_size               = cd[24:28],
        file_name_length                = cd[28:30],
        extra_field_length              = cd[30:32],
        file_comment_length             = cd[32:34],
        disk_number_start               = cd[34:36],
        internal_file_attributes        = cd[36:38],
        external_file_attributes        = cd[38:42],
        relative_offset_of_local_header = cd[42:46],
        file_name                       = name,
        extra_field                     = extra,
        file_comment                    = comment,
    )

    current = len(rcd)
    expected = MIN_CENTRAL_DIR_LENGTH + len(name) + len(extra) + len(comment)
    if current != expected:
        raise ValueError(f"Incomplete CentralDirectory record, mismatch between "
                         f"expected ({expected}) and current ({current}) amount")

    LOGGER.debug(f"Parsed central directory of file '{name.decode('utf-8')}' from bytes {offset}:{offset+len(rcd)}")
    return rcd
