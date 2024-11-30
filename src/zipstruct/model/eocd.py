from typing import Annotated, Type

from annotated_types import Len
from pydantic import BaseModel, conbytes
import struct

from src.zipstruct.model.common import unpack_little_endian

#??????????? Little endian (b'\x06\x05KP'), in file is stored from the least significant byte (hence b'PK\x05\x06')
EOCD_SIGNATURE = b'\x06\x05\x4b\x50'
INT_EOCD_SIGNATURE = 0x06054b50
EOCD_MIN_LENGTH = 22


class RawEocd(BaseModel):
    """
    This model represents the End of Central Directory (EOCD) record, which is the footer of a ZIP file.

    Details can be found in section '4.3.16' of: https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT

    Each attribute is annotated with its expected type in order to simplify parsing
    """

    signature: Annotated[conbytes(min_length=4, max_length=4), int] = EOCD_SIGNATURE
    """ 
    End of Central Directory (EOCD) signature (4 bytes).
    This field has a fixed value of '0x06054b50'.
    """

    disk_number: Annotated[conbytes(min_length=2, max_length=2), int]
    """ 
    The number of the disk containing the EOCD (2 bytes).
    In most cases, this will be 0, as the ZIP file typically spans a single disk 
    """

    central_dir_start_disk_number: Annotated[conbytes(min_length=2, max_length=2), int]
    """ 
    Number of the disk that contains the central directory (2 bytes). If the ZIP file is split across multiple 
    disks (which is rare), this will point to the disk containing the first part of the central directory.
    """

    total_entries_in_central_dir_on_this_disk: Annotated[conbytes(min_length=2, max_length=2), int]
    """
    The total number of entries in the central directory on this disk (2 bytes).
    If the ZIP file is split across multiple disks, this will reflect entries on the current disk.
    """

    total_entries_in_central_dir: Annotated[conbytes(min_length=2, max_length=2), int]
    """
    The total number of entries in the central directory across all disks (2 bytes). This will tell you how 
    many entries are in the whole archive, regardless of how many disks it spans. 
    """

    size_of_central_dir: Annotated[conbytes(min_length=4, max_length=4), int]
    """
    The total size of the central directory in bytes (4 bytes). This value tells you how large the central directory 
    is, which is useful to calculate the location of the central directory when decompressing the ZIP file.
    """

    offset_of_start_of_central_directory: Annotated[conbytes(min_length=4, max_length=4), int]
    """
    The offset (in bytes) from the start of the archive to the beginning of the central directory (4 bytes). 
    This is useful for finding where the central directory starts, especially in multi-disk ZIP archives. 
    """

    comment_length: Annotated[conbytes(min_length=2, max_length=2), int]
    """
    The length of the optional ZIP file comment (2 bytes). A ZIP file may have an optional comment attached to the archive, 
    and this field indicates how long that comment is in bytes.
    """

    comment: Annotated[conbytes(min_length=0, max_length=2**16), str] = None
    """
    The actual comment for the ZIP file, if present. Its length is given by the previous field (comment_length).
    If no comment is present, this field is empty.
    """

    def unpack(self):
        for name, field_info in self.model_fields.items():
            metadata = field_info.metadata
            len_constraint: Len = metadata[1]
            parse_type: Type = metadata[2]
            data = getattr(self, name)
            if len(data) < len_constraint.min_length or len(data) > len_constraint.max_length:
                raise
            print(f"{name} | {parse_type} | {len_constraint}")
            print(unpack_little_endian(data, parse_type))



def read_eocd(file_path: str) -> RawEocd:
    """ Find the EOCD signature by searching backward in the file """
    with open(file_path, 'rb') as f:
        # Seek to the end of the file
        f.seek(0, 2)

        # Start searching from the end of the file (in order to take care of the variable comment)
        max_comment_length = 2 ** 16
        file_size = f.tell()
        search_range = min(file_size, 22 + max_comment_length)
        f.seek(-search_range, 2)
        data = f.read(search_range)

        # Find the EOCD signature (0x06054b50) within the search range
        eocd_offset = data.rfind(struct.pack('<I', 0x06054b50))
        if eocd_offset == -1:
            raise ValueError("EOCD signature not found. Not a valid ZIP file.")

        # Slice out the EOCD record
        eocd = data[eocd_offset:]
        if len(eocd) < EOCD_MIN_LENGTH:
            raise ValueError("Incomplete EOCD record.")

        eocd_signature = struct.unpack('<I', eocd[:4])[0]
        if eocd_signature != 0x06054b50:
            raise ValueError("Invalid EOCD signature.")

        # Extract the comment, if any
        comment_length = struct.unpack('<H', eocd[20:22])[0]
        comment = eocd[22:22 + comment_length] if comment_length > 0 else b''
        assert len(f.read()) == 0

        reocd = RawEocd(
            disk_number=eocd[4:6],
            central_dir_start_disk_number=eocd[6:8],
            total_entries_in_central_dir_on_this_disk=eocd[8:10],
            total_entries_in_central_dir=eocd[10:12],
            size_of_central_dir=eocd[12:16],
            offset_of_start_of_central_directory=eocd[16:20],
            comment_length=eocd[20:22],
            comment=comment
        )
        reocd.unpack()
        return reocd


if __name__ == "__main__":
    print(read_eocd("/home/kebula/Desktop/projects/ZipHashC2PA/data/inp/original_0.xlsx"))
