import pprint

from intervaltree import IntervalTree, Interval

import logging
LOGGER = logging.getLogger("zipstruct")


class ReadState:
    def __init__(self, full_size: int):
        # Start with everything as unknown
        self.size = full_size
        self.unknown_intervals = IntervalTree(intervals=[Interval(begin=0, end=self.size)])
        self.parsed_intervals = IntervalTree()

    def register(self, begin: int, end: int, title: str):
        if self.parsed_intervals.overlap(begin=begin, end=end):
            raise ValueError(f"Interval ({begin}, {end}) is overlapping with some "
                             f"other parsed interval: {self.parsed_intervals[begin:end]}")
        self.parsed_intervals.addi(begin=begin, end=end, data=title)
        self.unknown_intervals.chop(begin=begin, end=end)

    def raise_for_not_existing(self, begin: int, end: int):
        result = self.parsed_intervals.envelop(begin=begin, end=end)
        size = len(result)
        if size > 1:
            raise ValueError(f"Interval ({begin}, {end}) envelops multiple existing "
                             f"intervals: {self.parsed_intervals[begin:end]}")
        if size == 0:
            raise ValueError(f"Interval ({begin}, {end}) does not exists")
        return

    def __str__(self):
        bytes_read = sum([interval.end - interval.begin for interval in self.parsed_intervals])
        return pprint.pformat({
            "full_size": self.size,
            "read_amount": f"{bytes_read}/{self.size}",
            "read_rate": f"{(bytes_read / self.size * 100):.2f}%",
        })

    def __repr__(self):
        bytes_read = sum([interval.end - interval.begin for interval in self.parsed_intervals])
        return pprint.pformat({
            "full_size": self.size,
            "read_amount": f"{bytes_read}/{self.size}",
            "read_rate": f"{(bytes_read / self.size * 100):.2f}%",
            "ranges_read": self.parsed_intervals.all_intervals,
            "ranges_unknown": self.unknown_intervals.all_intervals,
        })
