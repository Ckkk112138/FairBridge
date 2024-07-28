import json
import os
from datetime import datetime, timezone
from io import BytesIO

from ocflcore import (
    FileSystemStorage,
    OCFLRepository,
    OCFLObject,
    OCFLVersion,
    StorageRoot,
    StreamDigest,
    TopLevelLayout,
)


# Define a function to find a subfolder in a directory
def find_subfolder(directory, name):
    # Iterate over all entries in the directory
    for entry in os.listdir(directory):
        full_path = os.path.join(directory, entry)
        # Check if the entry is a directory
        if os.path.isdir(full_path):
            # If the directory name matches 'node1', print the path
            if entry == name:
                return full_path
            else:
                return False


# Define a function to search for a folder by the head
def search_folder_by_head(obj_path):
    inventory_path = os.path.join(obj_path, 'inventory.json')
    if os.path.exists(inventory_path):
        with open(inventory_path, 'r') as f:
            inventory_data = json.load(f)
            head = inventory_data.get('head')
            subfolder_path = os.path.join(obj_path, head)
            if os.path.isdir(subfolder_path):
                return subfolder_path
    return None


def init_ocfl_repository():
    root = StorageRoot(TopLevelLayout())

    # Setup workspace and root storage:
    storage = FileSystemStorage("FDO_Repos")
    workspace_storage = FileSystemStorage("workspace")
    # Initialize the repository
    repository = OCFLRepository(root, storage, workspace_storage=workspace_storage)
    repository.initialize()
    return repository


# Define a function to add an OCFL object to the repository
def add_ocfl_obj(repository, name, folder_path):
    # Add a new object to the repository
    # Update a new version is not available for now
    v = OCFLVersion(datetime.now(timezone.utc))
    for root, _, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            # Open the file and read its content
            with open(file_path, 'rb') as f:
                file_content = f.read()
                # Create a BytesIO stream from file content
                my_file = StreamDigest(BytesIO(file_content))
                v.files.add(filename, my_file.stream, my_file.digest)
    # Create the object
    o = OCFLObject(name)
    o.versions.append(v)
    repository.add(o)


# Define a function to get latest version of a OCFL object files
def get_ocfl_obj_files(repository_path, name):
    obj_path = find_subfolder(repository_path, name)
    print(obj_path)
    if obj_path:
        subfolder_path = search_folder_by_head(obj_path)
        content_folder = os.path.join(subfolder_path, 'content')
        if os.path.isdir(content_folder):
            files = []
            for root, _, filenames in os.walk(content_folder):
                for filename in filenames:
                    files.append(os.path.relpath(os.path.join(root, filename), obj_path))
            return files
        else:
            return []
    else:
        return []


# Define a function to list all OCFL objects (latest version) in the repository
def list_ocfl_objects(repository_path):
    objects = []
    for entry in os.listdir(repository_path):
        full_path = os.path.join(repository_path, entry)
        if os.path.isdir(full_path):
            subfolder_path = search_folder_by_head(full_path)
            content_folder = os.path.join(subfolder_path, 'content')
            metadata_file = os.path.join(content_folder, 'ro-crate-metadata.json')
            if os.path.isfile(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    value = metadata.get('@graph')[0].get('mainEntity').get('@id')
                    # remove '#' from the name
                    objects.append({'node_id': entry, 'cell_name': value[1:]})
    return objects