import json
import os


# Generate json file with extracted cell info
def extract_cell_info(file_path, upload_folder):
    with open(file_path, 'r', encoding='utf-8') as file:
        cell_info = json.load(file)

    output_data = {}

    output_data["title"] = cell_info.get('title', 'N/A')
    output_data["node_id"] = cell_info.get('node_id', 'N/A')

    kernel = cell_info.get("kernel", "")
    if kernel == 'ipython':
        output_data["language"] = 'Python'
    elif kernel == 'IRkernel':
        output_data["language"] = 'R'
    else:
        output_data["language"] = 'Unknown'

    outputs = cell_info.get('outputs', [])
    inputs = cell_info.get('inputs', [])
    types = cell_info.get('types', {})
    base_image = cell_info.get('base_image', {})
    confs = cell_info.get('confs', {})
    params = cell_info.get('params', [])
    param_values = cell_info.get('param_values', {})
    cell_dependencies = cell_info.get('dependencies', [])

    output_data["outputs"] = {}
    output_data["inputs"] = {}
    output_data["base_image"] = {}
    output_data["confs"] = {}
    output_data["params"] = {}
    output_data["software_dependencies"] = []

    for output in outputs:
        if output in types:
            output_data["outputs"][output] = types[output]

    for input in inputs:
        if input in types:
            output_data["inputs"][input] = types[input]

    output_data["base_image"]["id1"] = base_image.get("build", "N/A")
    output_data["base_image"]["id2"] = base_image.get("runtime", "N/A")
    output_data["base_image"]["version"] = cell_info.get("image_version", "N/A")

    for conf_key, conf_value in confs.items():
        output_data["confs"][conf_key] = conf_value

    for param in params:
        output_data["params"][param] = {}
        if param in types:
            output_data["params"][param]["type"] = types[param]
        if param in param_values:
            output_data["params"][param]["default"] = param_values[param]

    for cell_dependency in cell_dependencies:
        if cell_dependency.get('module'):
            full_name = f"{cell_dependency['module']}.{cell_dependency['name']}"
        else:
            full_name = cell_dependency['name']
        output_data["software_dependencies"].append(full_name)

    output_file_path = os.path.join(upload_folder, 'out.json')
    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        json.dump(output_data, outfile, indent=2)

    return {"status": "success", "message": f"Extracted cell info from {file_path}"}

# # Example usage
# file_path = './NaaVRE_db.json'
# title_to_match = 'Syntax-Normalizer-chenkaiwei0527-gmail-com'
# info = extract_cell_info(file_path, title_to_match)
# print(json.dumps(info, indent=2))

