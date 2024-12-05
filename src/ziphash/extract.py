import struct
from src.zipstruct.eocd.eocd import EndOfCentralDirectory


def extract_from_eocd(eocd: EndOfCentralDirectory, has_manifest = False):
    # model_dump() will not be used in order to specify explicitly the dump order
    reocd = eocd.raw
    aggregate = (
        reocd.signature
        + reocd.comment_length
        + reocd.comment
    )

    if not has_manifest:
        return (
            aggregate
            + reocd.total_entries_in_central_dir
            # + self.disk_number
            # + self.central_dir_start_disk_number
            # + self.total_entries_in_central_dir_on_this_disk
            # + self.size_of_central_dir
            # + self.offset_of_start_of_central_directory
        )

    # Consider manifest as an additional entry
    tot_unpacked = struct.unpack("<H", reocd.total_entries_in_central_dir)[0]
    tot_unpacked -= 1
    tot_packed = struct.pack("<H", tot_unpacked)

    return (
        aggregate
        + tot_packed
    )
