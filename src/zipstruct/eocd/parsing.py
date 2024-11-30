import struct
from typing import BinaryIO

from src.zipstruct.eocd.eocd import RawEocd, EOCD_MIN_LENGTH, EOCD_SIGNATURE, INT_EOCD_SIGNATURE
from src.zipstruct.lfh import LOGGER


def search_eocd_signature(f: BinaryIO) -> int:
    """ Find the EOCD signature by searching backward in the file """
    # Seek to end of the file
    f.seek(0, 2)
    file_size = f.tell()

    # Take care of the length-variable comment
    max_comment_length = 2 ** 16
    search_range = min(file_size, 22 + max_comment_length)
    f.seek(-search_range, 2)
    data = f.read(search_range)

    # Find the EOCD signature (0x06054b50) within the search range
    eocd_offset = data.rfind(struct.pack('<I', INT_EOCD_SIGNATURE))
    if eocd_offset == -1:
        raise ValueError("EOCD signature not found. Not a valid ZIP file.")
    return eocd_offset


def parse_eocd(f: BinaryIO, eocd_offset: int) -> RawEocd:
    # Seek to the start of the EOCD and load it in memory
    f.seek(eocd_offset, 0)
    eocd = f.read(-1)

    # Check size
    if len(eocd) < EOCD_MIN_LENGTH:
        raise ValueError(f"Incomplete EOCD record, found {len(eocd)} bytes but minimum is {EOCD_MIN_LENGTH}.")

    if len(eocd) > EOCD_MIN_LENGTH:
        LOGGER.debug(f"EOCD record is {len(eocd)} bytes long (minimum is {EOCD_MIN_LENGTH}). "
                     f"A comment is expected at the end of the file")

    # Check signature
    eocd_signature = struct.unpack('<I', eocd[:4])[0]
    if eocd_signature != INT_EOCD_SIGNATURE:
        raise ValueError("Invalid EOCD signature.")

    # Extract the comment, if any
    comment_length = struct.unpack('<H', eocd[20:22])[0]
    comment = eocd[22:22 + comment_length] if comment_length > 0 else b''

    return RawEocd(
        disk_number=eocd[4:6],
        central_dir_start_disk_number=eocd[6:8],
        total_entries_in_central_dir_on_this_disk=eocd[8:10],
        total_entries_in_central_dir=eocd[10:12],
        size_of_central_dir=eocd[12:16],
        offset_of_start_of_central_directory=eocd[16:20],
        comment_length=eocd[20:22],
        comment=comment
    )


if __name__ == "__main__":
    from pprint import pprint
    path = "/home/kebula/Desktop/projects/ZipHashC2PA/data/inp/original_0.xlsx"
    with open(path, mode="rb") as f:
        offset = search_eocd_signature(f)
        reocd = parse_eocd(f, offset)
        pprint(reocd)
        pprint(reocd.unpack())
