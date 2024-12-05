import os.path
import pprint

from intervaltree import IntervalTree

import logging
LOGGER = logging.getLogger("zipstruct")


class ZipParsingState:
    def __init__(self, path: str):
        self.path = path
        self.size = os.path.getsize(path)
        self.parsed_intervals = IntervalTree()
        self.unknown_intervals = IntervalTree()

    def register_parsed(self, begin: int, end: int, title: str):
        if self.parsed_intervals.overlap(begin=begin, end=end):
            raise ValueError(f"Interval ({begin}, {end}) is overlapping with some "
                             f"other parsed interval: {self.parsed_intervals[begin:end]}")
        self.parsed_intervals.addi(begin=begin, end=end, data=title)

    def register_unknown(self, begin: int, end: int, data: bytes):
        if self.unknown_intervals.overlap(begin=begin, end=end):
            raise ValueError(f"Interval ({begin}, {end}) is overlapping with some "
                             f"other unknown interval: {self.unknown_intervals[begin:end]}")
        self.unknown_intervals.addi(begin=begin, end=end, data=data)

    def __repr__(self):
        bytes_parsed = sum([interval.end - interval.begin for interval in self.parsed_intervals])
        # bytes_unknown = sum([interval.end - interval.begin for interval in self.unknown_intervals])
        return pprint.pformat({
            "parsed": f"{bytes_parsed}/{self.size}",
            "file_size": self.size,
            "range_parsed": self.parsed_intervals.all_intervals,
            "range_unknown": self.unknown_intervals.all_intervals,
        })
