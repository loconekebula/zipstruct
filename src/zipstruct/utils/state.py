import os.path
import pprint

from intervaltree import IntervalTree, Interval

import logging
LOGGER = logging.getLogger("zipstruct")


class ZipParsingState:
    def __init__(self, path: str):
        self.path = path
        self.size = os.path.getsize(path)
        self.parsed_intervals = IntervalTree()
        # Start with everything as unknown
        self.unknown_intervals = IntervalTree(intervals=[Interval(begin=0, end=self.size)])

    def register_parsed(self, begin: int, end: int, title: str):
        if self.parsed_intervals.overlap(begin=begin, end=end):
            raise ValueError(f"Interval ({begin}, {end}) is overlapping with some "
                             f"other parsed interval: {self.parsed_intervals[begin:end]}")
        self.parsed_intervals.addi(begin=begin, end=end, data=title)
        self.unknown_intervals.chop(begin=begin, end=end)

    def __repr__(self):
        bytes_parsed = sum([interval.end - interval.begin for interval in self.parsed_intervals])
        return pprint.pformat({
            "file_size": self.size,
            "parsed_amount": f"{bytes_parsed}/{self.size}",
            "parsed_rate": f"{(bytes_parsed / self.size * 100):.2f}%",
            "ranges_parsed": self.parsed_intervals.all_intervals,
            "ranges_unknown": self.unknown_intervals.all_intervals,
        })
