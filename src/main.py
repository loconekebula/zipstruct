import os.path

from src.zipstruct.localheaders.lfh import LOGGER
from src.zipstruct.utils.zipentry import ParsedZip
import zipfile
import shutil


def append_to_zip():
    path = "/home/kebula/Desktop/projects/ZipHashC2PA/data/inp/original_0.xlsx"
    outp = "/home/kebula/Desktop/projects/ZipHashC2PA/data/tmp/appended.zip"

    if os.path.exists(outp):
        os.remove(outp)
    shutil.copyfile(path, outp)

    with zipfile.ZipFile(outp, "a") as zf:
        zf.writestr('manifest.c2pa', data='secure_manifest')
        #zipf.write(source_path, destination)


if __name__ == "__main__":
    path = "/home/kebula/Desktop/projects/ZipHashC2PA/data/inp/original_0.xlsx"
    pz = ParsedZip.load(path)
    LOGGER.debug(pz.parsing_state)
