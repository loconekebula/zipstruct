from typing import BinaryIO, Dict

from src.zipstruct.centraldirs.centraldir import CentralDirectory
from src.zipstruct.eocd import parsing as eocd_parser
from src.zipstruct.centraldirs import parsing as cd_parser
from src.zipstruct.localheaders import parsing as lfh_parser
from src.zipstruct.descriptors import parsing as dd_parser
from src.zipstruct.utils.state import ZipParsingState

import logging
LOGGER = logging.getLogger("zipstruct")


def load_eocd(file: BinaryIO, parsing_state: ZipParsingState = None):
    begin = eocd_parser.search_eocd_signature(file)
    LOGGER.debug(f"Found EOCD signature in byte {begin}")

    eocd = eocd_parser.parse_eocd(file, begin)
    end = begin + len(eocd.raw)

    if parsing_state is not None:
        if parsing_state.size != end:
            raise ValueError("EOCD's end offset should match with the file size")
        parsing_state.register_parsed(begin=begin, end=end, title='EOCD')

    LOGGER.debug(f"EOCD successfully loaded from bytes {begin}:{end}")
    return eocd


def load_central_directories(file: BinaryIO, offset: int, parsing_state: ZipParsingState = None):
    LOGGER.debug("Started parsing central directories")
    centraldirs = cd_parser.parse_central_directories(file, offset)
    if parsing_state is None:
        return centraldirs

    begin = offset
    for cd in centraldirs:
        end = begin + len(cd.raw)
        parsing_state.register_parsed(begin=begin, end=end, title=f"CD of '{cd.file_name}'")
        begin = end
    return centraldirs


def create_zip_file_entries(
        file: BinaryIO, centraldirs: list[CentralDirectory], parsing_state: ZipParsingState = None
) -> Dict:
    LOGGER.debug("Started parsing local file headers")

    # Sort by offset to access headers sequentially
    centraldirs.sort(key=lambda cd: cd.relative_offset_of_local_header)

    entries = {}
    for cd in centraldirs:
        # Loading local file header
        lfh_start = cd.relative_offset_of_local_header
        lfh = lfh_parser.parse_local_file_header(file, lfh_start)
        lfh_end = lfh_start + len(lfh.raw)

        if parsing_state is not None:
            parsing_state.register_parsed(begin=lfh_start, end=lfh_end, title=f"LFH of '{lfh.file_name}'")

        # Registering file body offset
        body_end = lfh_end + cd.compressed_size
        parsing_state.register_parsed(begin=lfh_end, end=body_end, title=f"BODY of '{lfh.file_name}'")

        # Loading data descriptor
        dd = None
        if dd_parser.check_data_descriptor_presence(lfh):
            dd = dd_parser.parse_data_descriptor(file, body_end)
            if parsing_state is not None:
                parsing_state.register_parsed(begin=body_end, end=body_end+ len(dd), title=f"DD of '{lfh.file_name}'")

        entries[cd.file_name] = {
            'central_directory'    : cd,
            'local_file_header'    : lfh,
            'data_descriptor'      : dd,
            'body_offset'          : lfh_end,
            'body_compressed_size' : (body_end - lfh_end),
        }
        LOGGER.debug(f"Successfully parsed '{lfh.file_name}' having compressed size: {cd.compressed_size}")
    return entries

