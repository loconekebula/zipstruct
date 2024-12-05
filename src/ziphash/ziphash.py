import hashlib

from src.zipstruct.utils.zipentry import ParsedZip


def calculate_hash(file_path, hash_algorithm='sha256'):
    """Calculates the hash of a file."""
    hash_func = hashlib.new(hash_algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def compute_zip_hash(pz: ParsedZip, hash_algorithm='sha256'):
    """Calculates the hash of a zip file """
    hash_func = hashlib.new(hash_algorithm)
    exclude = {
        'size_of_central_dir',
        'offset_of_start_of_central_directory',
        'total_entries_in_central_dir_on_this_disk',
        'total_entries_in_central_dir'
    }

    eocd_dict = pz.eocd.raw.model_dump(exclude=exclude)
    for k, v in eocd_dict.items():
        hash_func.update(v)
    return hash_func.hexdigest()
