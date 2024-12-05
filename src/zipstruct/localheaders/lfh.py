import sys
from typing import Optional, BinaryIO
from pydantic import BaseModel, conbytes, conint

import logging
LOGGER = logging.getLogger("zipstruct")
LOGGER.addHandler(logging.StreamHandler(sys.stderr))
LOGGER.setLevel(logging.DEBUG)


LFH_SIGNATURE = b'\x50\x4b\x03\x04'
INT_LFH_SIGNATURE = 0x04034b50
MIN_LOCAL_FILE_HEADER = 30


class RawLocalFileHeader(BaseModel):
    """
    This model represents the Local File Header, which describes a file stored in a ZIP archive.

    Details can be found in section '4.3.7' of: https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT
    """

    signature: bytes = LFH_SIGNATURE
    """
    Local File Header signature (4 bytes).
    This field has a fixed value of b'\x50\x4b\x03\x04'.
    """

    version_needed_to_extract: conbytes(min_length=2, max_length=2)
    """
    The minimum version of the ZIP specification needed to extract this file (2 bytes).
    Indicates compatibility requirements for extracting the file.
    """

    general_purpose_flags: conbytes(min_length=2, max_length=2)
    """
    Bit flags indicating properties of the file (2 bytes).
    These may include encryption, data compression method specifics, and more.
    """

    compression_method: conbytes(min_length=2, max_length=2)
    """
    The compression method used to store the file (2 bytes).
    Common values include '0' (no compression) and '8' (deflate).
    """

    file_last_mod_time: conbytes(min_length=2, max_length=2)
    """
    The last modification time of the file, stored in MS-DOS format (2 bytes).
    """

    file_last_mod_date: conbytes(min_length=2, max_length=2)
    """
    The last modification date of the file, stored in MS-DOS format (2 bytes).
    """

    crc32: conbytes(min_length=4, max_length=4)
    """
    The CRC-32 checksum of the file data (4 bytes).
    This value is used to verify the integrity of the file contents.
    """

    compressed_size: conbytes(min_length=4, max_length=4)
    """
    The size of the compressed file data in bytes (4 bytes).
    If the file is stored without compression, this equals the uncompressed size.
    """

    uncompressed_size: conbytes(min_length=4, max_length=4)
    """
    The size of the uncompressed file data in bytes (4 bytes).
    """

    file_name_length: conbytes(min_length=2, max_length=2)
    """
    The length of the file name in bytes (2 bytes).
    Indicates the size of the 'file_name' field.
    """

    extra_field_length: conbytes(min_length=2, max_length=2)
    """
    The length of the optional extra field in bytes (2 bytes).
    Indicates the size of the 'extra_field' field, which may contain additional metadata.
    """

    file_name: Optional[bytes] = None
    """
    The name of the file, as specified in the ZIP archive.
    Its length is given by the 'file_name_length' field.
    """

    extra_field: Optional[bytes] = None
    """
    The extra field for the file, if present. Its length is given by the 'extra_field_length' field.
    The content of this field may contain additional metadata about the file.
    """


    def __len__(self):
        size = 0
        for _, value in self.model_dump(exclude={'file_name', 'extra_field'}).items():
            size += len(value)

        if size != MIN_LOCAL_FILE_HEADER:
            raise ValueError(f"LocalFileHeader record size is {size} (without fields having variable size), "
                             f"the expected amount was {MIN_LOCAL_FILE_HEADER}")
        return size + len(self.file_name) + len(self.extra_field)



class LocalFileHeader(BaseModel):
    """
    This model represents the Local File Header, which describes a file stored in a ZIP archive.

    Details can be found in section '4.3.7' of: https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT

    Original raw bytes are stored inside the 'raw' field in little-endian order.
    """

    raw: RawLocalFileHeader
    """
    Useful if you need all the fields of this class in the original raw binary (little-endian) format
    """

    signature: int = INT_LFH_SIGNATURE
    """
    Local File Header signature (4 bytes).
    This field has a fixed value of '0x04034b50'.
    """

    version_needed_to_extract: conint(ge=0, lt=2**16)
    """
    The minimum version of the ZIP specification needed to extract this file (2 bytes).
    Indicates compatibility requirements for extracting the file.
    """

    general_purpose_flags: conint(ge=0, lt=2 ** 16)
    """
    Bit flags indicating properties of the file (2 bytes).
    These may include encryption, data compression method specifics, and more.
    """

    compression_method: conint(ge=0, lt=2**16)
    """
    The compression method used to store the file (2 bytes).
    Common values include '0' (no compression) and '8' (deflate).
    """

    file_last_mod_time: conbytes(min_length=2, max_length=2)
    """
    This is not parsed and will be equal to the raw version.
    The last modification time of the file, stored in MS-DOS format (2 bytes).
    """

    file_last_mod_date: conbytes(min_length=2, max_length=2)
    """
    This is not parsed and will be equal to the raw version.
    The last modification date of the file, stored in MS-DOS format (2 bytes).
    """

    crc32: conbytes(min_length=4, max_length=4)
    """
    This is not parsed and will be equal to the raw version.
    The CRC-32 checksum of the file data (4 bytes). This value is used to verify the integrity of the file contents.
    """

    compressed_size: conint(ge=0, lt=2**32)
    """
    The size of the compressed file data in bytes (4 bytes).
    If the file is stored without compression, this equals the uncompressed size.
    """

    uncompressed_size: conint(ge=0, lt=2**32)
    """
    The size of the uncompressed file data in bytes (4 bytes).
    """

    file_name_length: conint(ge=0, lt=2**16)
    """
    The length of the file name in bytes (2 bytes).
    Indicates the size of the 'file_name' field.
    """

    extra_field_length: conint(ge=0, lt=2**16)
    """
    The length of the optional extra field in bytes (2 bytes).
    Indicates the size of the 'extra_field' field, which may contain additional metadata.
    """

    file_name: str = None
    """
    The name of the file, as specified in the ZIP archive.
    Its length is given by the 'file_name_length' field.
    """

    extra_field: Optional[bytes] = None
    """
    The extra field for the file, if present. Its length is given by the 'extra_field_length' field.
    The content of this field may contain additional metadata about the file.
    """


    def __len__(self):
        return len(self.raw)

