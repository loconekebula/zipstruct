from src.zipstruct.common import unpack_little_endian
from src.zipstruct.localheaders.lfh import LFH_SIGNATURE, RawLocalFileHeader
from src.zipstruct.centraldirs.centraldir import RawCentralDirectory
from typing import BinaryIO, List
import struct

import logging
LOGGER = logging.getLogger("zipstruct")


def parse_local_file_header(file: BinaryIO, offset: int):
    LOGGER.debug(f"Parsing local file header at offset: {offset}")
    file.seek(offset, 0)
    signature = file.read(4)
    if signature != LFH_SIGNATURE:
        raise Exception(f"Not a valid zipfile, the local file header does not have a valid "
                        f"signature (read: {signature}, expected: {LFH_SIGNATURE})")

    lfh = RawLocalFileHeader(
        signature=signature,
        version_needed_to_extract=file.read(2),
        general_purpose_bit_flag=file.read(2),
        compression_method=file.read(2),
        file_last_mod_time=file.read(2),
        file_last_mod_date=file.read(2),
        crc32=file.read(4),
        compressed_size=file.read(4),
        uncompressed_size=file.read(4),
        file_name_length=file.read(2),
        extra_field_length=file.read(2),
        # file_name: Optional[bytes] = None
        # extra_field: Optional[bytes] = None
    )

    # Loading attributes having a variable length
    fn_length = struct.unpack('<H', lfh.file_name_length)[0]
    ef_length = struct.unpack('<H', lfh.extra_field_length)[0]

    lfh.file_name = file.read(fn_length) if fn_length > 0 else b''
    lfh.extra_field = file.read(ef_length) if ef_length > 0 else b''

    LOGGER.debug(f"Parsed local file header of file '{unpack_little_endian(lfh.file_name, new_type=str)}'")

    ### 4.4.4 general purpose bit flag: (2 bytes)
    # gpb = struct.unpack('<H', lfh.general_purpose_bit_flag)[0]
    # LOGGER.debug(f'General purpose bits: {gpb:16b}')
    return lfh
