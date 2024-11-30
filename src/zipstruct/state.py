import os.path
from intervaltree import IntervalTree
from src.zipstruct.eocd import parsing as eocd_parser

import logging
LOGGER = logging.getLogger("zipstruct")


class ParsingState:
    def __init__(self, path: str):
        self.path = path
        self.size = os.path.getsize(path)
        self.io = open(path, mode="rb")
        self.tree = IntervalTree()
        self.eocd = None

    def load(self):
        LOGGER.debug("Loading EOCD...")
        self.eocd = self._load_eocd()
        print(self.tree)

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

