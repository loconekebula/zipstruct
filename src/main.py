import hashlib
import os.path

from src.ziphash.extract import extract_from_eocd, extract_from_central_directory, extract_from_lfh, extract_from_dd
from src.zipstruct.utils.zipentry import ParsedZip
import zipfile
import shutil

import logging
LOGGER = logging.getLogger("zipstruct")


def append_to_zip():
    path = "/home/kebula/Desktop/projects/ZipHashC2PA/data/inp/original_0.xlsx"
    outp = "/home/kebula/Desktop/projects/ZipHashC2PA/data/tmp/appended.zip"

    if os.path.exists(outp):
        os.remove(outp)
    shutil.copyfile(path, outp)

    with zipfile.ZipFile(outp, "a") as zf:
        # zf.writestr('manifest.c2pa', data='secure_manifest')
        second_file = "/home/kebula/Desktop/signed.c2pa"
        print(f"Adding a file having sizes: {os.path.getsize(second_file)}")
        zf.write(second_file, '__keb_manifest.c2pa')


if __name__ == "__main__":
    # append_to_zip()
    # exit()

    LOGGER.setLevel(logging.INFO)
    path = "/home/kebula/Desktop/projects/ZipHashC2PA/data/inp/original_0.xlsx"
    original_pz = ParsedZip.load(path)

    path = "/home/kebula/Desktop/projects/ZipHashC2PA/data/tmp/appended.zip"
    appended_pz = ParsedZip.load(path)

    # original_pz.compare(appended_pz)
    # appended_pz.compare(original_pz)
    # LOGGER.info(original_pz.parsing_state)
    # LOGGER.info(appended_pz.parsing_state)

    hash_func = hashlib.new('sha256')
    hash_func.update(extract_from_eocd(original_pz.eocd))
    for entry in original_pz.entries:
        hash_func.update(extract_from_central_directory(entry.central_directory))
        hash_func.update(extract_from_lfh(entry.local_file_header))
        if entry.data_descriptor is not None:
            hash_func.update(extract_from_dd(entry.data_descriptor))
    print(hash_func.hexdigest())

    hash_func = hashlib.new('sha256')
    hash_func.update(extract_from_eocd(appended_pz.eocd, has_manifest=True))
    for entry in appended_pz.entries:
        if entry.central_directory.file_name == "__keb_manifest.c2pa":
            continue
        hash_func.update(extract_from_central_directory(entry.central_directory))
        hash_func.update(extract_from_lfh(entry.local_file_header))
        if entry.data_descriptor is not None:
            hash_func.update(extract_from_dd(entry.data_descriptor))
    print(hash_func.hexdigest())

