import json
import os
import shutil
import time

import rocrate.rocrate as ROCrate
from rocrate.model.file import File
from rocrate.model.computationalworkflow import ComputationalWorkflow
from rocrate.model.computerlanguage import ComputerLanguage
from rocrate.model.person import Person
from rocrate.model.contextentity import ContextEntity
from rocrate.model.data_entity import DataEntity
from rocrate.model.softwareapplication import SoftwareApplication
from datetime import date
from rocrate.model.data_entity import DataEntity


# def create_dummy_file(title, content="This is a dummy file."):
#     # Define the file path with the given title
#     file_path = f"{title}.txt"
#
#     # Open the file in write mode and write the content
#     with open(file_path, 'w') as file:
#         file.write(content)
#
#     print(f"File '{file_path}' has been created.")
#     return file_path

def create_fdo(store_path, unique_id, cell_dir):
    start_time = time.perf_counter()
    input_path = os.path.join(store_path, 'out.json')
    print("entered create_fdo")
    try:
        data = {}

        # Load the JSON data from the input file
        with open(input_path, 'r') as f:
            data = json.load(f)

        # Create a new ROCrate
        crate = ROCrate.ROCrate()

        today = date.today()
        node_id = data['node_id']

        # Add metadata
        crate.datePublished = str(today)
        crate.name = node_id

        # crate.write("my_crate")

        # cell_id = create_dummy_file(data['title'], "dummy file")
        cell_id = "#" + data['title']
        cell_name = data['title']
        programming_language = data['language']

        # Main Entity
        current_cell = crate.add(DataEntity(crate, cell_id, properties={
            "@id": cell_id,
            "@type": ["File", "SoftwareSourceCode", "ComputationalWorkflow", "SoftwareApplication"],
            "name": cell_name,
            "programmingLanguage": programming_language
        }))

        # Add inputs
        cell_inputs = None
        total_inputs = len(data['inputs']) + len(data['params']) + len(data['confs'])
        if total_inputs > 1:
            cell_inputs = []
            if len(data['inputs']) > 0:
                for input in data['inputs'].items():
                    type = input[1]
                    id = "#input_" + input[0]
                    name = input[0]
                    i1 = crate.add(DataEntity(crate, id, properties={
                        "@type": ["FormalParameter"],
                        "name": name,
                        "additionalType": type
                    }))
                    cell_inputs.append({"@id": id})
            if len(data['params']) > 0:
                for name, details in data['params'].items():
                    param_type = details['type']
                    default_value = details['default']
                    id = "#" + name
                    i1 = crate.add(DataEntity(crate, id, properties={
                        "@type": ["FormalParameter", "PropertyValueSpecification"],
                        "name": name,
                        "additionalType": param_type,
                        "defaultValue": default_value
                    }))
                    cell_inputs.append({"@id": id})
            if len(data['confs']) > 0:
                for input in data['confs'].items():
                    value = input[1]
                    id = "#" + input[0]
                    name = input[0]
                    i1 = crate.add(DataEntity(crate, id, properties={
                        "@type": ["FormalParameter", "PropertyValueSpecification"],
                        "name": name,
                        "defaultValue": value
                    }))
                    cell_inputs.append({"@id": id})
        elif total_inputs == 1:
            cell_inputs = {}
            if len(data['inputs']) == 1:
                (key_name,), (value,) = data['inputs'].keys(), data['inputs'].values()
                type = value
                id = "#input_" + key_name
                name = key_name
                i1 = crate.add(DataEntity(crate, id, properties={
                    "@type": ["FormalParameter"],
                    "name": name,
                    "additionalType": type
                }))
                cell_inputs = {"@id": id}
            elif len(data['params']) == 1:
                key_name, key_details = next(iter(data['prarams'].items()))

                # Extract type and default value dynamically
                param_type = key_details['type']
                default_value = key_details['default']
                type = param_type
                id = "#" + key_name
                name = key_name
                i1 = crate.add(DataEntity(crate, id, properties={
                    "@type": ["FormalParameter", "PropertyValueSpecification"],
                    "name": name,
                    "additionalType": type,
                    "defaultValue": default_value
                }))
                cell_inputs = {"@id": id}
            elif len(data['confs']) == 1:
                (key_name,), (value,) = data['confs'].keys(), data['confs'].values()
                default = value
                id = "#" + key_name
                name = key_name
                i1 = crate.add(DataEntity(crate, id, properties={
                    "@type": ["FormalParameter", "PropertyValueSpecification"],
                    "name": name,
                    "defaultValue": default
                }))
                cell_inputs = {"@id": id}
        current_cell["ComputationalWorkflow#input"] = cell_inputs

        # Add outputs
        cell_outputs = None
        total_outputs = len(data['outputs'])
        if total_outputs > 1:
            cell_outputs = []
            if len(data['outputs']) > 0:
                for input in data['outputs'].items():
                    type = input[1]
                    id = "#output_" + input[0]
                    name = input[0]
                    i1 = crate.add(DataEntity(crate, id, properties={
                        "@type": ["FormalParameter"],
                        "name": name,
                        "additionalType": type
                    }))
                    cell_outputs.append({"@id": id})
        elif total_outputs == 1:
            cell_outputs = {}
            if len(data['outputs']) == 1:
                (key_name,), (value,) = data['outputs'].keys(), data['outputs'].values()
                type = value
                id = "#output_" + key_name
                name = key_name
                i1 = crate.add(DataEntity(crate, id, properties={
                    "@type": ["FormalParameter"],
                    "name": name,
                    "additionalType": type
                }))
                cell_outputs = {"@id": id}
        current_cell["ComputationalWorkflow#output"] = cell_outputs

        # encode base image
        base_image = data['base_image']
        base_image_id = "#base_image"
        base_image_name = "base_image"
        base_image_location_ids = [base_image['id1'], base_image['id2']]
        image1 = crate.add(DataEntity(crate, base_image_id, properties={
            "@type": ["File", "SoftwareSourceCode"],
            "name": base_image_name,
            "identifier": base_image_location_ids,
            "version": base_image['version']
        }))

        crate.mainEntity = current_cell
        crate.datePublished = str(today)
        crate.description = "This is a FDO for a cell in a Jupyter notebook"
        crate.license = "https://creativecommons.org/licenses/by/4.0/"

        current_cell['softwareRequirements'] = ', '.join(data['software_dependencies'])

        # Add additional files
        if cell_dir is None:
            current_cell['hasPart'] = image1
        else:
            curren_cell_parts = [{"@id": "#base_image"}]
            for root, _, files in os.walk(cell_dir):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    file_id = "./additional/" + filename
                    file_name = filename
                    file = crate.add(DataEntity(crate, file_id, properties={
                        "@type": ["File"],
                        "name": file_name
                    }))
                    curren_cell_parts.append({"@id": file_id})
            current_cell['hasPart'] = curren_cell_parts
        crate.write("my_crate_" + unique_id)

        # Copy additional files to the crate
        if cell_dir is not None:
            crate_path = os.path.join(f"my_crate_{unique_id}", "additional")
            os.makedirs(crate_path, exist_ok=True)
            # Copy files from source to destination
            try:
                for filename in os.listdir(cell_dir):
                    source_file = os.path.join(cell_dir, filename)
                    destination_file = os.path.join(crate_path, filename)
                    if os.path.isfile(source_file):
                        shutil.copy(source_file, destination_file)
            except Exception as e:
                return {"status": "error", "message": str(e)}

        # end_time = time.perf_counter()
        # print(f"Time taken to save files: {(end_time - start_time) * 1000:.2f} ms")
        return {"status": "success", "message": "FDO created successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
