import os.path

from src.zipstruct.localheaders.lfh import LOGGER
from src.zipstruct.common import unpack_little_endian
from zipstruct.state import ParsingState
import zipfile
import shutil

if __name__ == "__main__":
    path = "/home/kebula/Desktop/projects/ZipHashC2PA/data/inp/original_0.xlsx"
    """
    outp = "/home/kebula/Desktop/projects/ZipHashC2PA/data/tmp/appended.zip"

    if os.path.exists(outp):
        os.remove(outp)
    shutil.copyfile(path, outp)

    with zipfile.ZipFile(outp, "a") as zf:
        zf.writestr('manifest.c2pa', data='secure_manifest')
        #zipf.write(source_path, destination)
    """
    ps = ParsingState(path)
    with open(path, 'rb') as f:
        print(f.read(4))
        f.seek(54 + 204, 0)
        print(f.read(4))
        print(f.read(4))
        print(f.read(4))
        print(f.read(4))
        print(f.read(4))
        print(f.read(4))
        """
        f.seek(328, 0)
        value = f.read(16)
        unpacked = unpack_little_endian(value, new_type=int)
        print(f"{unpacked:10d} | {hex(unpacked)} | {value}")

        f.seek(844, 0)
        value = f.read(16)
        unpacked = unpack_little_endian(value, new_type=int)
        print(f"{unpacked:10d} | {hex(unpacked)} | {value}")

        f.seek(1089, 0)
        value = f.read(16)
        unpacked = unpack_little_endian(value, new_type=int)
        print(f"{unpacked:10d} | {hex(unpacked)} | {value}")
        # print("0x08074b50")
        """
        ps.load(f)
    LOGGER.debug(ps)

    import struct
    for lfh in ps.lfhs:
        gpb = struct.unpack('<H', lfh.general_purpose_bit_flag)[0]
        LOGGER.debug(f"General purpose bits '{bin(gpb)}' - {unpack_little_endian(lfh.file_name, new_type=str)}")
