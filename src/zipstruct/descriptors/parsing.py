import logging
from typing import BinaryIO

from src.zipstruct.common import GeneralPurposeBitMasks, unpack_little_endian
from src.zipstruct.descriptors.descriptor import RawDataDescriptor, DATA_DESCRIPTOR_SIGNATURE, DataDescriptor
from src.zipstruct.localheaders.lfh import LocalFileHeader

LOGGER = logging.getLogger("zipstruct")


def check_data_descriptor_presence(lfh: LocalFileHeader):
    return bool(lfh.general_purpose_flags & GeneralPurposeBitMasks.USE_DATA_DESCRIPTOR.value)


def parse_data_descriptor(file: BinaryIO, offset: int):
    LOGGER.debug(f"Parsing data descriptor at offset: {offset}")
    file.seek(offset, 0)
    signature = file.read(4)

    if signature != DATA_DESCRIPTOR_SIGNATURE:
        crc32 = signature
        signature = None
    else:
        crc32 = file.read(4)

    rdd = RawDataDescriptor(
        signature         = signature,
        crc32             = crc32,
        compressed_size   = file.read(4),
        uncompressed_size = file.read(4),
    )

    return unpack_from_raw(rdd)


def unpack_from_raw(rdd: RawDataDescriptor):
    return DataDescriptor(
        raw               = rdd,
        signature         = unpack_little_endian(rdd.signature) if rdd.signature is not None else None,
        crc32             = rdd.crc32,
        compressed_size   = unpack_little_endian(rdd.compressed_size),
        uncompressed_size = unpack_little_endian(rdd.uncompressed_size),
    )
