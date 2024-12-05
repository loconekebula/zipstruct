from typing import Optional, List

from pydantic import BaseModel

from src.zipstruct.centraldirs.centraldir import CentralDirectory
from src.zipstruct.descriptors.descriptor import DataDescriptor
from src.zipstruct.eocd.eocd import EndOfCentralDirectory
from src.zipstruct.localheaders.lfh import LocalFileHeader
from src.zipstruct.utils import loaders
from src.zipstruct.utils.state import ZipParsingState



class ZipFileEntry(BaseModel):
    """
    This model aggregates together related metadata of a file stored inside a ZIP archive.
    """

    central_directory: CentralDirectory
    local_file_header: LocalFileHeader
    data_descriptor: Optional[DataDescriptor]
    body_offset: int
    body_compressed_size: int



class ParsedZip(BaseModel):
    entries: List[ZipFileEntry]
    eocd: EndOfCentralDirectory
    parsing_state: ZipParsingState

    class Config:
        arbitrary_types_allowed = True

    @staticmethod
    def load(path: str) -> "ParsedZip":
        state = ZipParsingState(path)

        with open(path, mode="rb") as f:
            eocd = loaders.load_eocd(f, state)
            centraldirs = loaders.load_central_directories(f, eocd.offset_of_start_of_central_directory, state)
            dict_entries = loaders.create_zip_file_entries(f, centraldirs, state)

        zip_entries = []
        for name, value in dict_entries.items():
            zfe = ZipFileEntry(
                central_directory    = value["central_directory"],
                local_file_header    = value["local_file_header"],
                data_descriptor      = value["data_descriptor"],
                body_offset          = value["body_offset"],
                body_compressed_size = value["body_compressed_size"],
            )
            zip_entries.append(zfe)
        return ParsedZip(entries=zip_entries, eocd=eocd, parsing_state=state)

