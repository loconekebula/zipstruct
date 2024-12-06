import hashlib
import struct

from intervaltree import Interval

from src.zipstruct.centraldirs.centraldir import CentralDirectory
from src.zipstruct.descriptors.descriptor import DataDescriptor
from src.zipstruct.eocd.eocd import EndOfCentralDirectory
from src.zipstruct.localheaders.lfh import LocalFileHeader
from src.zipstruct.utils.state import ReadState, LOGGER
from src.zipstruct.utils.zipentry import ParsedZip


# NOTE: model_dump() will not be used in order to specify explicitly the dump order


def extract_from_eocd(eocd: EndOfCentralDirectory, has_manifest = False):
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


def extract_from_central_directory(cd: CentralDirectory):
    # model_dump() will not be used in order to specify explicitly the dump order
    rcd = cd.raw
    aggregate = (
            rcd.signature
            + rcd.version_made_by
            + rcd.version_needed_to_extract
            + rcd.general_purpose_flags
            + rcd.compression_method
            + rcd.last_mod_file_time
            + rcd.last_mod_file_date
            + rcd.crc32
            + rcd.compressed_size
            + rcd.uncompressed_size
            + rcd.file_name_length
            + rcd.extra_field_length
            + rcd.file_comment_length
            # + rcd.disk_number_start
            + rcd.internal_file_attributes
            + rcd.external_file_attributes
            + rcd.relative_offset_of_local_header
            + rcd.file_name
            + rcd.extra_field
            + rcd.file_comment
    )
    return aggregate


def extract_from_lfh(lfh: LocalFileHeader):
    rlfh = lfh.raw
    aggregate = (
        rlfh.signature
        + rlfh.version_needed_to_extract
        + rlfh.general_purpose_flags
        + rlfh.compression_method
        + rlfh.file_last_mod_time
        + rlfh.file_last_mod_date
        + rlfh.crc32
        + rlfh.compressed_size
        + rlfh.uncompressed_size
        + rlfh.file_name_length
        + rlfh.extra_field_length
        + rlfh.file_name
        + rlfh.extra_field
    )
    return aggregate


def extract_from_dd(dd: DataDescriptor):
    rdd = dd.raw
    signature = rdd.signature if rdd.signature is not None else b''
    aggregate = (
        signature
        + rdd.crc32
        + rdd.compressed_size
        + rdd.uncompressed_size
    )
    return aggregate


def add_to_state(data, interval: Interval, state: ReadState):
    state.registeri(
        begin=interval.begin,
        end=interval.begin + len(data),
        title=interval.data
    )


def compute_zip_hash(pz: ParsedZip, has_manifest=False):
    hash_state = ReadState(pz.parsing_state.size)

    hash_func = hashlib.new('sha256')

    # Add EOCD first
    eocd_aggregate = extract_from_eocd(pz.eocd, has_manifest=has_manifest)
    add_to_state(data=eocd_aggregate, interval=pz.eocd.interval, state=hash_state)
    hash_func.update(eocd_aggregate)

    for entry in pz.entries:
        if entry.central_directory.file_name == "__keb_manifest.c2pa":
            # Ignore manifest if present
            LOGGER.warning("Manifest found, it will be ignored")
            continue

        # Add CD, LFH, and DD
        cd_aggregate = extract_from_central_directory(entry.central_directory)
        add_to_state(data=cd_aggregate, interval=entry.central_directory.interval, state=hash_state)
        hash_func.update(cd_aggregate)

        lfh_aggregate = extract_from_lfh(entry.local_file_header)
        add_to_state(data=lfh_aggregate, interval=entry.local_file_header.interval, state=hash_state)
        hash_func.update(lfh_aggregate)
        if entry.data_descriptor is not None:
            dd_aggregate = extract_from_dd(entry.data_descriptor)
            add_to_state(data=dd_aggregate, interval=entry.data_descriptor.interval, state=hash_state)
            hash_func.update(dd_aggregate)

    # Add file body
    with open(file=pz.path, mode="rb") as f:
        for entry in pz.entries:
            if entry.central_directory.file_name == "__keb_manifest.c2pa":
                # Ignore manifest if present
                LOGGER.warning("Manifest found, it will be ignored")
                continue
            f.seek(entry.body_offset)
            chunk = f.read(entry.body_compressed_size)
            hash_state.registeri(
                begin=entry.body_offset,
                end=entry.body_offset + len(chunk),
                title=f"BODY of {entry.central_directory.file_name}"
            )
            hash_func.update(chunk)

    return hash_func.hexdigest(), hash_state

