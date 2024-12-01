from zipstruct.state import ParsingState
# import zipfile

if __name__ == "__main__":
    path = "/home/kebula/Desktop/projects/ZipHashC2PA/data/inp/original_0.xlsx"
    ps = ParsingState(path)
    with open(path, 'rb') as f:
        ps.load()
