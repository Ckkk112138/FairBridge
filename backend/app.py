import uuid
import webbrowser

from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import os
import json
from cell_parser import extract_cell_info
from FDO_encoder import create_fdo
import threading
import ocfl_utils

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


def make_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


data_ready = {}
DB_FOLDER = 'db'
make_folder(DB_FOLDER)
repo = ocfl_utils.init_ocfl_repository()


@app.before_request
def before_request():
    headers = {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
               'Access-Control-Allow-Headers': 'Content-Type'}
    if request.method == 'OPTIONS' or request.method == 'options':
        return jsonify(headers), 200

# Define a function to process the file
def process_file(file_path, unique_id, cell_dir):
    # Generate a unique ID for the file
    # Directory to store the JSON files
    UPLOAD_FOLDER = DB_FOLDER + '/uploads' + "_" + unique_id
    make_folder(UPLOAD_FOLDER)
    # Call the extract_cell_info function to extrac key info of a cell
    result = extract_cell_info(file_path, UPLOAD_FOLDER)
    # Call the create_fdo function to create an FDO
    result2 = create_fdo(UPLOAD_FOLDER, unique_id, cell_dir)
    global data_ready
    if result2.get('status') == 'success':
        data_ready[unique_id] = True
    else:
        data_ready[unique_id] = False
    return unique_id


# Define a route to store the new RO-Crate Metadata File and store it in the OCFL repository
@app.route('/store-fdo', methods=['POST'])
def store_json():
    if not request.is_json:
        return jsonify({"error": "Invalid input, expecting JSON format"}), 400

    content = request.get_json()

    # Extract unique_id from the content
    unique_id = request.args.get('unique_id')
    if not unique_id:
        return jsonify({"error": "No unique_id provided"}), 400

    base_dir = 'my_crate_' + unique_id
    file_name = 'ro-crate-metadata.json'
    data_file_path = os.path.join(base_dir, file_name)
    # Save the JSON content to the specified file
    with open(data_file_path, 'w') as f:
        json.dump(content, f, indent=4)
    node_id = content.get('@graph')[0].get('name')
    ocfl_utils.add_ocfl_obj(repo, node_id, base_dir)
    del data_ready[unique_id]
    return jsonify({"message": "File saved successfully"}), 200


# Define a route to check if the data is ready
@app.route('/is-data-ready/<unique_id>')
def is_data_ready(unique_id):
    return jsonify({"ready": data_ready.get(unique_id, False)})


# Define a route to get the generated RO-Crate Metadata File (initial version)
@app.route('/get-processed-data/<unique_id>')
def get_processed_data(unique_id):
    base_dir = 'my_crate_' + unique_id
    file_name = 'ro-crate-metadata.json'
    data_file_path = os.path.join(base_dir, file_name)
    print(data_file_path)
    if data_ready:
        if os.path.exists(data_file_path):
            with open(data_file_path, 'r') as f:
                processed_data = json.load(f)
            return jsonify(processed_data)
        else:
            return jsonify({"error": "Data file not found"}), 404
    else:
        return jsonify({"error": "Data not ready"}), 404


# Define a route to upload a new cell
@app.route('/upload', methods=['POST'])
def upload_file():
    global data_ready
    if 'cell' not in request.form:
        return jsonify(error='No cell data provided.'), 400

    cell_data = request.form['cell']
    try:
        cell_info = json.loads(cell_data)
    except json.JSONDecodeError:
        return jsonify(error='Invalid JSON format for cell data.'), 400

    unique_id = str(uuid.uuid4())
    filename = f"cell_{unique_id}.json"
    file_path = os.path.join(DB_FOLDER, filename)

    # Ensure the DB_FOLDER exists
    if not os.path.exists(DB_FOLDER):
        make_folder(DB_FOLDER)

    # Save the JSON content to the specified file
    with open(file_path, 'w') as f:
        json.dump(cell_info, f)

    # Check if there are any files
    if len(request.files) > 0:
        cell_dir = os.path.join(DB_FOLDER, unique_id)
        os.makedirs(cell_dir, exist_ok=True)
        # Save files
        for key in request.files:
            # Iterate over each file under the same key
            files = request.files.getlist(key)
            for file in files:
                file.save(os.path.join(cell_dir, file.filename))
    else:
        cell_dir = None

    data_ready[unique_id] = False
    thread = threading.Thread(target=process_file, args=(file_path, unique_id, cell_dir))
    thread.start()

    # redirect to the frontend with the unique_id
    vue_app_url = f"http://localhost:5173/{unique_id}"
    webbrowser.open(vue_app_url, new=2)
    return jsonify({"redirect_url": vue_app_url}), 200


# Define a route to get the path of all files of an OCFL object using node_id
@app.route('/get-ocfl-object-files/<node_id>')
def get_ocfl_object_files(node_id):
    print(node_id)
    files = ocfl_utils.get_ocfl_obj_files("./FDO_Repos", node_id)
    if len(files) > 0:
        return jsonify({"files": files}), 200
    else:
        return jsonify({"error": f"No files found for node_id {node_id}"}), 404


# Define a route to get all OCFL objects in the repository
@app.route('/get-ocfl-objects')
def get_ocfl_objects():
    objects = ocfl_utils.list_ocfl_objects("./FDO_Repos")
    if len(objects) > 0:
        return jsonify({"objects": objects}), 200
    else:
        return jsonify({"error": "No OCFL objects found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
