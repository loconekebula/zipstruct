from src.zipstruct.utils.common import compare_models
from pydantic import BaseModel, conbytes, conint
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
    """

    signature: conbytes(min_length=4, max_length=4) = CENTRAL_DIR_SIGNATURE
    """ 
    Central Directory File Header signature (4 bytes).
    This field has a fixed value of b'\x50\x4B\x01\x02'.
    """

    version_made_by: conbytes(min_length=2, max_length=2)
    """
    The version of the ZIP specification used to create the file (2 bytes). 
    Indicates compatibility with various ZIP features.
    """

    version_needed_to_extract: conbytes(min_length=2, max_length=2)
    """
    Minimum version of the ZIP specification needed to extract the file (2 bytes).
    """

    general_purpose_flags: conbytes(min_length=2, max_length=2)
    """
    General-purpose bit flags (2 bytes). Indicates encryption, compression options, etc.
    """

    compression_method: conbytes(min_length=2, max_length=2)
    """
    Compression method used for the file (2 bytes). Common values:
    - 0: No compression
    - 8: Deflate
    """

    last_mod_file_time: conbytes(min_length=2, max_length=2)
    """
    Last modification time of the file (2 bytes). Stored in MS-DOS format.
    """

    last_mod_file_date: conbytes(min_length=2, max_length=2)
    """
    Last modification date of the file (2 bytes). Stored in MS-DOS format.
    """

    crc32: conbytes(min_length=4, max_length=4)
    """
    CRC-32 checksum of the uncompressed file data (4 bytes).
    """

    compressed_size: conbytes(min_length=4, max_length=4)
    """
    Size of the compressed file data (4 bytes).
    """

    uncompressed_size: conbytes(min_length=4, max_length=4)
    """
    Size of the uncompressed file data (4 bytes).
    """

    file_name_length: conbytes(min_length=2, max_length=2)
    """
    Length of the file name (2 bytes).
    """

    extra_field_length: conbytes(min_length=2, max_length=2)
    """
    Length of the extra field (2 bytes). Optional metadata for the file.
    """

    file_comment_length: conbytes(min_length=2, max_length=2)
    """
    Length of the file comment (2 bytes). Optional comments about the file.
    """

    disk_number_start: conbytes(min_length=2, max_length=2)
    """
    Disk number where the file starts (2 bytes). Relevant for multi-disk ZIP archives.
    """

    internal_file_attributes: conbytes(min_length=2, max_length=2)
    """
    Internal file attributes (2 bytes). For example, text file or binary.
    """

    external_file_attributes: conbytes(min_length=4, max_length=4)
    """
    External file attributes (4 bytes). Includes file system-specific permissions.
    """

    relative_offset_of_local_header: conbytes(min_length=4, max_length=4)
    """
    Offset (in bytes) of the corresponding Local File Header (4 bytes).
    """

    file_name: conbytes(min_length=0, max_length=2**16) = None
    """
    The name of the file (variable length). The length is specified by file_name_length.
    """

    extra_field: conbytes(min_length=0, max_length=2**16) = None
    """
    Extra metadata for the file (variable length). The length is specified by extra_field_length.
    """

    file_comment: conbytes(min_length=0, max_length=2**16) = None
    """
    Comment about the file (variable length). The length is specified by file_comment_length.
    """


    def __len__(self):
        size = 0
        for _, value in self.model_dump(exclude={'file_name', 'extra_field', 'file_comment'}).items():
            size += len(value)

        if size != MIN_CENTRAL_DIR_LENGTH:
            raise ValueError(f"CentralDirectory record size is {size} (without fields having variable size), "
                             f"the expected amount was {MIN_CENTRAL_DIR_LENGTH}")
        return size + len(self.file_name) + len(self.extra_field) + len(self.file_comment)




class CentralDirectory(BaseModel):
    """
    This model represents the Central Directory File Header, a key structure in ZIP archives
    that provides metadata for each file in the archive.

    Details can be found in section '4.3.12' of: https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT

    Original raw bytes are stored inside the 'raw' field in little-endian order.
    """

    raw: RawCentralDirectory
    """
    Useful if you need all the fields of this class in the original raw binary (little-endian) format
    """

    signature: int = INT_CENTRAL_DIR_SIGNATURE
    """ 
    Central Directory File Header signature (4 bytes).
    This field has a fixed value of '0x02014b50'.
    """

    version_made_by: conint(ge=0, lt=2**16)
    """
    The version of the ZIP specification used to create the file (2 bytes). 
    Indicates compatibility with various ZIP features.
    """

    version_needed_to_extract: conint(ge=0, lt=2**16)
    """
    Minimum version of the ZIP specification needed to extract the file (2 bytes).
    """

    general_purpose_flags: conint(ge=0, lt=2**16)
    """
    General-purpose bit flags (2 bytes). Indicates encryption, compression options, etc.
    """

    compression_method: conint(ge=0, lt=2**16)
    """
    Compression method used for the file (2 bytes). Common values:
    - 0: No compression
    - 8: Deflate
    """

    last_mod_file_time: conbytes(min_length=2, max_length=2)
    """
    This is not parsed and will be equal to the raw version.
    Last modification time of the file (2 bytes). Stored in MS-DOS format.
    """

    last_mod_file_date: conbytes(min_length=2, max_length=2)
    """
    This is not parsed and will be equal to the raw version.
    Last modification date of the file (2 bytes). Stored in MS-DOS format.
    """

    crc32: conbytes(min_length=4, max_length=4)
    """
    This is not parsed and will be equal to the raw version.
    CRC-32 checksum of the uncompressed file data (4 bytes).
    """

    compressed_size: conint(ge=0, lt=4**16)
    """
    Size of the compressed file data (4 bytes).
    """

    uncompressed_size: conint(ge=0, lt=4**16)
    """
    Size of the uncompressed file data (4 bytes).
    """

    file_name_length: conint(ge=0, lt=2**16)
    """
    Length of the file name (2 bytes).
    """

    extra_field_length: conint(ge=0, lt=2**16)
    """
    Length of the extra field (2 bytes). Optional metadata for the file.
    """

    file_comment_length: conint(ge=0, lt=2**16)
    """
    Length of the file comment (2 bytes). Optional comments about the file.
    """

    disk_number_start: conint(ge=0, lt=2**16)
    """
    Disk number where the file starts (2 bytes). Relevant for multi-disk ZIP archives.
    """

    internal_file_attributes: conbytes(min_length=2, max_length=2)
    """
    This is not parsed and will be equal to the raw version.
    Internal file attributes (2 bytes). For example, text file or binary.
    """

    external_file_attributes: conbytes(min_length=4, max_length=4)
    """
    This is not parsed and will be equal to the raw version.
    External file attributes (4 bytes). Includes file system-specific permissions.
    """

    relative_offset_of_local_header: conint(ge=0, lt=2**32)
    """
    Offset (in bytes) of the corresponding Local File Header (4 bytes).
    """

    file_name: str = None
    """
    The name of the file (variable length). The length is specified by file_name_length.
    This will tried to be parsed in 'utf-8' or 'cp437', if an error occurs during parsing it will be None
    """

    extra_field: Annotated[conbytes(min_length=0, max_length=2**16), bytes] = None
    """
    This is not parsed and will be equal to the raw version.
    Extra metadata for the file (variable length). The length is specified by extra_field_length.
    """

    file_comment: str = None
    """
    Comment about the file (variable length). The length is specified by file_comment_length.
    This will tried to be parsed in 'utf-8' or 'cp437', if an error occurs during parsing it will be None
    """

    _offset_start: int = None
    """
    This is a custom field, it is not compliant with the standard.
    """

    def __len__(self):
        return len(self.raw)


    def compare(self, new: 'CentralDirectory', filename=''):
        prefix = f'{filename}.CD' if filename else ''
        return compare_models(a=self, b=new, exclude={'raw'}, prefix=prefix)
