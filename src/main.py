import hashlib
import os.path

from src.ziphash.extract import extract_from_eocd, extract_from_central_directory, extract_from_lfh, extract_from_dd, \
    compute_zip_hash
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

    original_hexdigest, state = compute_zip_hash(original_pz, has_manifest=False)
    print(state)
    appended_hexdigest, state = compute_zip_hash(appended_pz, has_manifest=True)
    print(state)

    print(f"Original: {original_hexdigest}")
    print(f"Modified: {appended_hexdigest}")

