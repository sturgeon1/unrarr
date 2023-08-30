import os
import re
import rarfile

# Set your log path here
LOG_PATH = "/unrarr/unrarr.log"
# List search directories here
SEARCH_DIRS = [
    "/data/movies",
    "/data/radarr",
    "/data/tv",
    "/data/sonarr",
]


# Set output directory based on search directory. Edit this for your filesystem
def set_output_dir(rar_file):
    if "/data/radarr" in rar_file or "/data/movies" in rar_file:
        output_dir = "/data/unrarr/movies"
    elif "/data/torrents/sonarr" in rar_file or "/data/torrents/tv" in rar_file:
        output_dir = "/data/torrents/unrarr/tv"
    return output_dir


# Load log file contents into set
def load_log():
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "a") as _:
            pass
        return set()
    with open(LOG_PATH, "r") as f:
        unrar_files = set(line.strip() for line in f.readlines())
    print("Loaded log file")
    return unrar_files


# Add processed directory to log file
def add_log(directory):
    with open(LOG_PATH, "a") as f:
        f.write(f"{directory}\n")


# Use regex (gross) to check if file is multipart rar
def check_multipart(file_name):
    pattern = re.compile(r"\.part\d{2}\.rar$")
    return pattern.search(file_name) is not None


# Walk through search directories, find rar files
def get_rars():
    rar_list = []
    for dir in SEARCH_DIRS:
        for folder_path, _, file_names in os.walk(dir):
            for file_name in file_names:
                if file_name.endswith(".rar") and (
                    not check_multipart(file_name) or file_name.endswith("part01.rar")
                ):
                    rar_list.append(os.path.join(folder_path, file_name))
    return rar_list


# Get the directory name directly under the search directory, so rar files
# in child directories are extracted to the same directory as parent files
def get_ext_dir(rar_file, search_dirs):
    base_dir = next((dir for dir in search_dirs if rar_file.startswith(dir)), None)
    rel_path = os.path.relpath(rar_file, base_dir)
    parts = rel_path.split(os.sep)
    return parts[0]


# Generate full output directory, extract rar file, and add log entry
def unrarr(rar_file, unrar_files):
    if rar_file in unrar_files:
        return
    output_dir = set_output_dir(rar_file)
    ext_dir = get_ext_dir(rar_file, SEARCH_DIRS)
    full_output = os.path.join(output_dir, ext_dir)
    print(f"Extracting {rar_file}...")
    with rarfile.RarFile(rar_file, "r") as rf:
        rf.extractall(full_output)
    unrar_files.add(rar_file)
    add_log(rar_file)


if __name__ == "__main__":
    unrar_dirs = load_log()
    rar_list = get_rars()
    for rar in rar_list:
        unrarr(rar, unrar_dirs)
