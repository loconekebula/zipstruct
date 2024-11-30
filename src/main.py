from src.zipstruct.model.eocd import read_eocd

if __name__ == "__main__":
    path = "/home/kebula/Desktop/projects/ZipHashC2PA/data/inp/original_0.xlsx"
    with open(path, 'rb') as f:
        read_eocd(f)
