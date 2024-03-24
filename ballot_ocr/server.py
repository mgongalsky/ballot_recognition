from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename

from ballot_ocr.recognize_ballot import recognize_ballot

app = Flask(__name__)

# Directory to save uploaded files
UPLOAD_FOLDER = 'uploads'
# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        json_response = recognize_ballot(file_path)
        return jsonify(json_response)
    else:
        return jsonify({"error": "File type not allowed"}), 400

if __name__ == '__main__':
    app.run(debug=True)