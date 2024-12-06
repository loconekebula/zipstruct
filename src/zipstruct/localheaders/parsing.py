from src.zipstruct.utils.common import unpack_little_endian, GeneralPurposeBitMasks
from src.zipstruct.localheaders.lfh import LFH_SIGNATURE, RawLocalFileHeader, LocalFileHeader
from typing import BinaryIO
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

    rlfh = RawLocalFileHeader(
        signature                  = signature,
        version_needed_to_extract  = file.read(2),
        general_purpose_flags      = file.read(2),
        compression_method         = file.read(2),
        file_last_mod_time         = file.read(2),
        file_last_mod_date         = file.read(2),
        crc32                      = file.read(4),
        compressed_size            = file.read(4),
        uncompressed_size          = file.read(4),
        file_name_length           = file.read(2),
        extra_field_length         = file.read(2),
        # file_name
        # extra_field
    )

    # Loading attributes having a variable length
    fn_length = struct.unpack('<H', rlfh.file_name_length)[0]
    ef_length = struct.unpack('<H', rlfh.extra_field_length)[0]

    rlfh.file_name = file.read(fn_length) if fn_length > 0 else b''
    rlfh.extra_field = file.read(ef_length) if ef_length > 0 else b''

    LOGGER.debug(f"Parsed local file header of file '{unpack_little_endian(rlfh.file_name, encoding='utf-8')}'")

    return unpack_from_raw(rlfh)


def unpack_from_raw(rlfh: RawLocalFileHeader):
    ### 4.4.4 general purpose bit flag: (2 bytes)
    gpb = struct.unpack('<H', rlfh.general_purpose_flags)[0]
    utf8 = bool(gpb & GeneralPurposeBitMasks.UTF8_LANGUAGE_ENCODING.value)
    encoding = 'utf-8' if utf8 else 'cp437'
    return LocalFileHeader(
        raw                        = rlfh,
        signature                  = unpack_little_endian(rlfh.signature),
        version_needed_to_extract  = unpack_little_endian(rlfh.version_needed_to_extract),
        general_purpose_flags      = gpb,
        compression_method         = unpack_little_endian(rlfh.compression_method),
        file_last_mod_time         = rlfh.file_last_mod_time,
        file_last_mod_date         = rlfh.file_last_mod_date,
        crc32                      = rlfh.crc32,
        compressed_size            = unpack_little_endian(rlfh.compressed_size),
        uncompressed_size          = unpack_little_endian(rlfh.uncompressed_size),
        file_name_length           = unpack_little_endian(rlfh.file_name_length),
        extra_field_length         = unpack_little_endian(rlfh.extra_field_length),
        file_name                  = unpack_little_endian(rlfh.file_name, encoding=encoding),
        extra_field                = rlfh.extra_field,
    )
