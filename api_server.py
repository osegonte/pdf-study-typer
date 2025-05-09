# api_server.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from parser.study_item import StudyItem, StudyItemCollection
from parser.content_parser import PDFStudyExtractor
from parser.text_parser import TextParser

app = Flask(__name__, static_folder='frontend/dist')
CORS(app)  # Enable Cross-Origin Resource Sharing

@app.route('/api/parse-pdf', methods=['POST'])
def parse_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    # Save the uploaded file temporarily
    temp_path = 'temp/' + file.filename
    os.makedirs('temp', exist_ok=True)
    file.save(temp_path)
    
    # Process the PDF
    try:
        extractor = PDFStudyExtractor(temp_path)
        extractor.process()
        items = extractor.get_study_items()
        
        # Convert items to serializable format
        serialized_items = [item.to_dict() for item in items]
        
        # Remove temporary file
        os.remove(temp_path)
        
        return jsonify({
            'items': serialized_items,
            'count': len(serialized_items)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/parse-text', methods=['POST'])
def parse_text():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
        
    # Process the text
    try:
        parser = TextParser(data['text'])
        parser.parse()
        items = parser.get_study_items()
        
        # Convert items to serializable format
        serialized_items = [item.to_dict() for item in items]
        
        return jsonify({
            'items': serialized_items,
            'count': len(serialized_items)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve the React app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)