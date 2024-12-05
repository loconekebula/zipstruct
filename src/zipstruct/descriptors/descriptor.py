from typing import Optional

from pydantic import BaseModel, conbytes, conint

DATA_DESCRIPTOR_SIGNATURE = b'\x50\x4b\x07\x08'
INT_DATA_DESCRIPTOR_SIGNATURE = 0x08074b50
DATA_DESCRIPTOR_MIN_LENGTH = 12
DATA_DESCRIPTOR_MAX_LENGTH = 16


class RawDataDescriptor(BaseModel):
    """
    This model represents the 'DataDescriptor' record, which is an optional footer of a ZIP file.

    Details can be found in section '4.3.9' of: https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT
    """

    signature: Optional[conbytes(min_length=4, max_length=4)] = DATA_DESCRIPTOR_SIGNATURE
    """ 
    The optional signature field (4 bytes). If present, it is fixed to b'\x50\x4b\x07\x08'.
    """

    crc32: conbytes(min_length=4, max_length=4)
    """
    CRC-32 of the uncompressed data (4 bytes). This value must match the CRC-32 calculated for the data.
    """

    compressed_size: conbytes(min_length=4, max_length=4)
    """
    The size of the compressed data (4 bytes). This field provides the compressed size of the file.
    """

    uncompressed_size: conbytes(min_length=4, max_length=4)
    """
    The size of the uncompressed data (4 bytes). This field provides the original size of the file.
    """

    def __len__(self):
        size = 0 if self.signature is None else len(self.signature)
        for _, value in self.model_dump(exclude={'signature'}).items():
            size += len(value)

        if DATA_DESCRIPTOR_MAX_LENGTH < size < DATA_DESCRIPTOR_MIN_LENGTH:
            raise ValueError(f"'DataDescriptor' record size is {size}, expected size in "
                             f"range [{DATA_DESCRIPTOR_MIN_LENGTH}, {DATA_DESCRIPTOR_MAX_LENGTH}]")
        return size



class DataDescriptor(BaseModel):
    """
    This model represents the 'DataDescriptor' record, which is an optional footer of a ZIP file.

    Details can be found in section '4.3.9' of: https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT

    Original raw bytes are stored inside the 'raw' field in little-endian order.
    """

    raw: RawDataDescriptor
    """
    Useful if you need all the fields of this class in the original raw binary (little-endian) format
    """

    signature: Optional[conint(ge=INT_DATA_DESCRIPTOR_SIGNATURE, le=INT_DATA_DESCRIPTOR_SIGNATURE)] = INT_DATA_DESCRIPTOR_SIGNATURE
    """ 
    The optional signature field (4 bytes). If present, it is fixed to '0x08074b50'.
    """

    crc32: conbytes(min_length=4, max_length=4)
    """
    This is not parsed and will be equal to the raw version.
    CRC-32 of the uncompressed data (4 bytes). This value must match the CRC-32 calculated for the data.
    """

    compressed_size: conint(ge=0, lt=2**32)
    """
    The size of the compressed data (4 bytes). This field provides the compressed size of the file.
    """

    uncompressed_size: conint(ge=0, lt=2**32)
    """
    The size of the uncompressed data (4 bytes). This field provides the original size of the file.
    """

    def __len__(self):
        return len(self.raw)

