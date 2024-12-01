import struct
from pydantic import BaseModel, conbytes
from typing import Annotated


# Little endian (b'\x50\x4B\x01\x02')
CENTRAL_DIR_SIGNATURE = b'\x50\x4B\x01\x02'
INT_CENTRAL_DIR_SIGNATURE = 0x02014b50
MIN_CENTRAL_DIR_LENGTH = 46


class RawCentralDirectory(BaseModel):
    """
    This model represents the Central Directory File Header, a key structure in ZIP archives
    that provides metadata for each file in the archive.

    Details can be found in section '4.3.12' of: https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT

    Each attribute is annotated with its expected type in order to simplify parsing.
    """

    signature: Annotated[conbytes(min_length=4, max_length=4), int] = struct.pack('<I', INT_CENTRAL_DIR_SIGNATURE)
    """ 
    Central Directory File Header signature (4 bytes).
    This field has a fixed value of '0x02014b50'.
    """

    version_made_by: Annotated[conbytes(min_length=2, max_length=2), int]
    """
    The version of the ZIP specification used to create the file (2 bytes). 
    Indicates compatibility with various ZIP features.
    """

    version_needed_to_extract: Annotated[conbytes(min_length=2, max_length=2), int]
    """
    Minimum version of the ZIP specification needed to extract the file (2 bytes).
    """

    general_purpose_flags: Annotated[conbytes(min_length=2, max_length=2), int]
    """
    General-purpose bit flags (2 bytes). Indicates encryption, compression options, etc.
    """

    compression_method: Annotated[conbytes(min_length=2, max_length=2), int]
    """
    Compression method used for the file (2 bytes). Common values:
    - 0: No compression
    - 8: Deflate
    """

    last_mod_file_time: Annotated[conbytes(min_length=2, max_length=2), int]
    """
    Last modification time of the file (2 bytes). Stored in MS-DOS format.
    """

    last_mod_file_date: Annotated[conbytes(min_length=2, max_length=2), int]
    """
    Last modification date of the file (2 bytes). Stored in MS-DOS format.
    """

    crc32: Annotated[conbytes(min_length=4, max_length=4), int]
    """
    CRC-32 checksum of the uncompressed file data (4 bytes).
    """

    compressed_size: Annotated[conbytes(min_length=4, max_length=4), int]
    """
    Size of the compressed file data (4 bytes).
    """

    uncompressed_size: Annotated[conbytes(min_length=4, max_length=4), int]
    """
    Size of the uncompressed file data (4 bytes).
    """

    file_name_length: Annotated[conbytes(min_length=2, max_length=2), int]
    """
    Length of the file name (2 bytes).
    """

    extra_field_length: Annotated[conbytes(min_length=2, max_length=2), int]
    """
    Length of the extra field (2 bytes). Optional metadata for the file.
    """

    file_comment_length: Annotated[conbytes(min_length=2, max_length=2), int]
    """
    Length of the file comment (2 bytes). Optional comments about the file.
    """

    disk_number_start: Annotated[conbytes(min_length=2, max_length=2), int]
    """
    Disk number where the file starts (2 bytes). Relevant for multi-disk ZIP archives.
    """

    internal_file_attributes: Annotated[conbytes(min_length=2, max_length=2), int]
    """
    Internal file attributes (2 bytes). For example, text file or binary.
    """

    external_file_attributes: Annotated[conbytes(min_length=4, max_length=4), int]
    """
    External file attributes (4 bytes). Includes file system-specific permissions.
    """

    relative_offset_of_local_header: Annotated[conbytes(min_length=4, max_length=4), int]
    """
    Offset (in bytes) of the corresponding Local File Header (4 bytes).
    """

    file_name: Annotated[conbytes(min_length=0, max_length=2**16), str] = None
    """
    The name of the file (variable length). The length is specified by file_name_length.
    """

    extra_field: Annotated[conbytes(min_length=0, max_length=2**16), bytes] = None
    """
    Extra metadata for the file (variable length). The length is specified by extra_field_length.
    """

    file_comment: Annotated[conbytes(min_length=0, max_length=2**16), str] = None
    """
    Comment about the file (variable length). The length is specified by file_comment_length.
    """

    def __len__(self):
        size = 0
        for name, _ in self.model_fields.items():
            if name == 'file_name' or name == 'extra_field' or name == 'file_comment':
                continue
            size += len(getattr(self, name))

        if size != MIN_CENTRAL_DIR_LENGTH:
            raise ValueError(f"CentralDirectory record size is {size} (without fields having variable size), "
                             f"the expected amount was {MIN_CENTRAL_DIR_LENGTH}")
        return size + len(self.file_name) + len(self.extra_field) + len(self.file_comment)
