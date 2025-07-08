import os

def create_file(directory, filename, content=""):
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w') as f:
        f.write(content)
    return file_path
