import zipfile
import hashlib
import shutil
import os


def calculate_hash(file_path, hash_algorithm='sha256'):
    """Calculates the hash of a file."""
    hash_func = hashlib.new(hash_algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def add_dummy_file(zip_path, dummy_file_name="dummy.txt"):
    """Adds a dummy file to the ZIP archive."""
    with zipfile.ZipFile(zip_path, 'a') as zipf:
        # Create and add a dummy file
        zipf.writestr(dummy_file_name, "This is a dummy file.")


def remove_file_from_zip(zip_path, file_to_remove):
    """Removes a file from the ZIP archive."""
    # Create a temporary ZIP file
    temp_zip_path = zip_path + ".temp"

    with zipfile.ZipFile(zip_path, 'r') as zipf, zipfile.ZipFile(temp_zip_path, 'w') as temp_zip:
        # Copy all files except the one to be removed
        for item in zipf.infolist():
            if item.filename != file_to_remove:
                temp_zip.writestr(item, zipf.read(item.filename))

    # Replace original ZIP with the modified one
    os.replace(temp_zip_path, zip_path)

def main():
    original_file = "/home/kebula/Desktop/projects/ZipHashC2PA/data/sample-1-sheet.xlsx"
    modified_file = "/home/kebula/Desktop/projects/ZipHashC2PA/temp/sample_modified.xlsx"

    # Step 1: Copy original file to work with a fresh copy
    shutil.copy(original_file, modified_file)

    # Step 2: Calculate hash of the original file
    original_hash = calculate_hash(original_file)
    print(f"Original Hash: {original_hash}")

    # Step 3: Add dummy file to the modified ZIP
    add_dummy_file(modified_file, "dummy.txt")

    # Step 4: Calculate hash after adding dummy file
    hash_after_add = calculate_hash(modified_file)
    print(f"Hash After Adding: {hash_after_add}")

    # Step 5: Remove the dummy file
    remove_file_from_zip(modified_file, "dummy.txt")

    # Step 6: Calculate hash after removing dummy file
    hash_after_remove = calculate_hash(modified_file)
    print(f"Hash After Removing: {hash_after_remove}")

    # Check if hash matches original
    if original_hash == hash_after_remove:
        print("The file is identical to the original.")
    else:
        print("The file is NOT identical to the original.")

if __name__ == "__main__":
    main()
