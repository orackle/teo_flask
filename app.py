from flask import Flask, request, jsonify
import os
import uuid  # For generating unique filenames
from whisperspeech.pipeline import Pipeline

app = Flask(__name__)

# Initialize WhisperSpeech pipeline
pipe = Pipeline(s2a_ref='collabora/whisperspeech:s2a-q4-tiny-en+pl.model')

# Configure upload folder
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size

def generate_unique_filename():
    # Generate a unique filename using UUID
    return str(uuid.uuid4())

@app.route('/generate-speech', methods=['POST'])
def generate_speech():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = generate_unique_filename() + '.wav'  # Ensure unique filenames
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text from request
        text = request.form.get('text', '')

        # Generate speech
        result = pipe.generate(text, lang='en', speaker=filepath)
        
        # Save the result to a file
        output_filename = generate_unique_filename() + '.wav'
        output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        result.save(output_filepath)  # assuming `result` has a `save` method
        
        # Return the path to the generated speech
        response = {
            'status': 'success',
            'speech_url': f"/serve-file?filename={output_filename}"
        }
        return jsonify(response)

@app.route('/serve-file')
def serve_file():
    filename = request.args.get('filename')
    if not filename:
        return 'File name not provided', 400
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(filepath)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
