from typing import Optional, List

from pydantic import BaseModel

from src.zipstruct.centraldirs.centraldir import CentralDirectory
from src.zipstruct.descriptors.descriptor import DataDescriptor
from src.zipstruct.eocd.eocd import EndOfCentralDirectory
from src.zipstruct.localheaders.lfh import LocalFileHeader
from src.zipstruct.utils import loaders
from src.zipstruct.utils.state import ZipParsingState

import logging
LOGGER = logging.getLogger("zipstruct")


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


    def compare(self, new: 'ParsedZip'):
        self.eocd.compare(new.eocd)
        if len(self.entries) != len(new.entries):
            LOGGER.warning(
                f"Mismatch between number of files inside the zips ({len(self.entries)} != {len(new.entries)})"
            )

        for entry in self.entries:
            name = entry.central_directory.file_name
            iterator = iter(x for x in new.entries if x.central_directory.file_name == name)
            correspondent = next(iterator, None)
            if not correspondent:
                LOGGER.warning(f"File '{name}' has not been found in the new zip")
                continue

            entry.central_directory.compare(correspondent.central_directory)
            entry.local_file_header.compare(correspondent.local_file_header)
            if entry.data_descriptor:
                entry.data_descriptor.compare(correspondent.data_descriptor, filename=name)
            if entry.body_offset != correspondent.body_offset:
                print(f"diff 'body_offset': {entry.body_offset} != {correspondent.body_offset}")
            if entry.body_compressed_size != correspondent.body_compressed_size:
                print(f"diff 'body_compressed_size': {entry.body_compressed_size} != {correspondent.body_compressed_size}")

