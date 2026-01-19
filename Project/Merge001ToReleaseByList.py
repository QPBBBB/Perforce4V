def read_paths_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def execute():
    # Read PathToReleaseFrom001.txt And Process Each Path
    file_path = r'D:\AssetMergeTool\PathToReleaseFrom001.txt'
    paths = read_paths_from_file(file_path)
    print(paths)

if __name__ == '__main__':
    execute()