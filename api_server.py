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
    # ... existing code ...

@app.route('/api/parse-text', methods=['POST'])
def parse_text():
    # ... existing code ...

# Serve the React app for any other routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Add a function to launch the web UI
def launch_web_ui(port=5000):
    """Launch the web UI in the default browser"""
    import webbrowser
    import threading
    
    def open_browser():
        webbrowser.open(f'http://localhost:{port}')
    
    # Start the browser after a short delay
    threading.Timer(1.5, open_browser).start()
    
    # Run the Flask app
    app.run(debug=True, port=port)

if __name__ == '__main__':
    app.run(debug=True)