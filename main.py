from flask import Flask, request, jsonify, send_from_directory
import os, random, string, json

app = Flask(__name__)

config = json.loads(open("./config.json").read())
print(config)

VERSION = "1.0.0"
IMAGE_FOLDER: str = config.get("image_folder")
BASE_PATH: str = config.get("base_path")
PORT: int = config.get("port")

keys: list = config.get("keys")

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

app.config["IMAGE_FOLDER"] = IMAGE_FOLDER

def get_file_name(ext: str, len: int = 16) -> str:
    name = ""
    for _ in range(len):
        name = name + "".join(random.choice(string.ascii_letters))
    return f"{name}.{ext}"

def get_file_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""

@app.route(f"/{BASE_PATH}")
def home():
    return f"Running chaarlottte's simple image host. Version: {VERSION}"

@app.route(f"/{BASE_PATH}/raw/<path:path>", methods=["GET"])
def view_image(path):
    return send_from_directory(IMAGE_FOLDER, path)

@app.route(f"/{BASE_PATH}/upload", methods=["POST"])
def upload_image():

    if request.headers.get("key") is None or request.headers.get("key") not in keys:
        return jsonify({ "message": "Not authorized." }), 401

    if "file" not in request.files:
        return jsonify({ "message": "No image provided." }), 400
    
    image = request.files["file"]
    if image.filename == "":
        return jsonify({ "message": "No selected file." }), 400
    
    if image:
        file_name = get_file_name(ext=get_file_extension(image.filename))
        file_path = os.path.join(app.config.get("IMAGE_FOLDER"), file_name)
        image.save(file_path)
        return jsonify({ 
            "message": "Image saved successfully." ,
            "image_url": f"http://127.0.0.1:5000/img/raw/{file_name}"
        }), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=PORT)