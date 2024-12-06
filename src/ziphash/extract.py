import struct
from src.zipstruct.centraldirs.centraldir import CentralDirectory
from src.zipstruct.descriptors.descriptor import DataDescriptor
from src.zipstruct.eocd.eocd import EndOfCentralDirectory
from src.zipstruct.localheaders.lfh import LocalFileHeader


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
