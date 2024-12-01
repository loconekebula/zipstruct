import os.path
import struct
import pprint

from intervaltree import IntervalTree
from src.zipstruct.eocd import parsing as eocd_parser
from src.zipstruct.centraldirs import parsing as cd_parser

import logging
LOGGER = logging.getLogger("zipstruct")


class ParsingState:
    def __init__(self, path: str):
        self.path = path
        self.size = os.path.getsize(path)
        self.io = open(path, mode="rb")
        self.tree = IntervalTree()
        self.eocd = None
        self.cds = None

    def load(self):
        LOGGER.debug("Loading EOCD...")
        self.eocd = self._load_eocd()
        cd_start = struct.unpack("<I", self.eocd.offset_of_start_of_central_directory)[0]
        self.cds = self._load_central_directories(cd_start)
        print(self)


    def _load_eocd(self):
        eocd_offset = eocd_parser.search_eocd_signature(self.io)
        LOGGER.debug(f"Found EOCD signature in byte {eocd_offset}")
        reocd = eocd_parser.parse_eocd(self.io, eocd_offset)
        end = eocd_offset + len(reocd)
        if self.size != end:
            raise ValueError("EOCD end should match the file end")
        self.tree.addi(eocd_offset, end)
        LOGGER.debug(f"EOCD successfully loaded from bytes {eocd_offset}:{end}")
        return reocd

    def _load_central_directories(self, offset):
        cds = cd_parser.parse_central_directories(self.io, offset)
        total = sum([len(cd) for cd in cds])
        self.tree.addi(offset, offset + total)
        return cds

    def __repr__(self):
        namelist = [cd.file_name.decode("utf-8") for cd in self.cds] if self.cds is not None else None
        bytes_parsed = sum([interval.end - interval.begin for interval in self.tree])
        return pprint.pformat({
            "progress": f"{bytes_parsed}/{self.size}",
            "file_size": self.size,
            "bytes_parsed": bytes_parsed,
            "range_parsed": self.tree,
            "eocd_size": len(self.eocd) if self.eocd else None,
            "central_directories": namelist,
        })
