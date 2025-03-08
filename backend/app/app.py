from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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

if __name__ == '__main__':
    app.run(debug=True)
