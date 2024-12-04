import os.path
import pprint

from intervaltree import IntervalTree
from typing import BinaryIO

from src.zipstruct.centraldirs.centraldir import CentralDirectory
from src.zipstruct.eocd import parsing as eocd_parser
from src.zipstruct.centraldirs import parsing as cd_parser
from src.zipstruct.eocd.eocd import RawEocd, EndOfCentralDirectory
from src.zipstruct.localheaders.lfh import RawLocalFileHeader
from src.zipstruct.localheaders import parsing as lfh_parser

import logging
LOGGER = logging.getLogger("zipstruct")


class ParsingState:
    eocd: EndOfCentralDirectory

    def __init__(self, path: str):
        self.path = path
        self.size = os.path.getsize(path)
        self.tree = IntervalTree()
        self.cds: list[CentralDirectory] = []
        self.lfhs : list[RawLocalFileHeader] = []

    def load(self, file: BinaryIO):
        LOGGER.debug("Loading EOCD...")
        self.eocd = self._load_eocd(file)
        cd_start = self.eocd.offset_of_start_of_central_directory
        self.cds = self._load_central_directories(file, cd_start)
        self.lfhs = self._load_local_file_headers(file, self.cds)
        return self

    def _load_eocd(self, file: BinaryIO):
        eocd_offset = eocd_parser.search_eocd_signature(file)
        LOGGER.debug(f"Found EOCD signature in byte {eocd_offset}")
        eocd = eocd_parser.parse_eocd(file, eocd_offset)
        end = eocd_offset + len(eocd.raw)
        if self.size != end:
            raise ValueError("EOCD end should match the file end")
        self.tree.addi(eocd_offset, end)
        LOGGER.debug(f"EOCD successfully loaded from bytes {eocd_offset}:{end}")
        return eocd

    def _load_central_directories(self, file: BinaryIO, offset: int):
        cds = cd_parser.parse_central_directories(file, offset)
        total = sum([len(cd.raw) for cd in cds])
        self.tree.addi(offset, offset + total)
        return cds

    def _load_local_file_headers(self, file: BinaryIO, cds: list[CentralDirectory]):
        LOGGER.debug("Started parsing local file headers")
        # Sort by offset
        cds.sort(key=lambda cd: cd.relative_offset_of_local_header)
        lfhs = []
        for cd in cds:
            offset = cd.relative_offset_of_local_header
            lfh = lfh_parser.parse_local_file_header(file, offset)
            self.tree.addi(offset, offset + len(lfh))
            LOGGER.debug(f"File '{lfh.file_name}' has compressed size: {cd.compressed_size}"
                         f" and uncompressed size: {cd.uncompressed_size}")
            lfhs.append(lfh)
        return lfhs

    def __repr__(self):
        namelist = [cd.file_name for cd in self.cds] if self.cds is not None else None
        bytes_parsed = sum([interval.end - interval.begin for interval in self.tree])
        return pprint.pformat({
            "parsed_amount": f"{bytes_parsed}/{self.size}",
            "file_size": self.size,
            "bytes_parsed": bytes_parsed,
            "range_parsed": self.tree.all_intervals,
            "eocd_size": len(self.eocd) if self.eocd else None,
            "central_directories": namelist,
            "number_of_files": len(namelist)
        })
