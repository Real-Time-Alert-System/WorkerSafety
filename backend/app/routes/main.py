# routes/main.py
from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from utils import allowed_file
from flask import current_app

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # In a real application, you would call your PPE detection model here
        # For demo purposes, we're returning dummy results
        results = {
            'safe': True,
            'detections': {
                'helmet': True,
                'vest': True,
                'gloves': False,
                'goggles': True
            }
        }
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath.replace('\\', '/'),
            'results': results
        })
    
    return jsonify({'error': 'File type not allowed'})
