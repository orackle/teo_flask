from flask import Flask, request, jsonify
import os
import torch
from whisperspeech.pipeline import Pipeline
from urllib.parse import quote as url_quote

app = Flask(__name__)

# Initialize WhisperSpeech pipeline
pipe = Pipeline(s2a_ref='collabora/whisperspeech:s2a-q4-tiny-en+pl.model')

# Configure upload folder
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size

@app.route('/generate-speech', methods=['POST'])
def generate_speech():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text from request
        text = request.form.get('text', '')

        # Generate speech
        result = pipe.generate(text, lang='en', speaker=filepath)
        
        # Save the result to a file
        output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'output.wav')
        result.save(output_filepath)  # assuming `result` has a `save` method
        
        # Return the path to the generated speech
        response = {
            'status': 'success',
            'speech_url': output_filepath  # You might need to serve this file properly
        }
        return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
