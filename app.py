from flask import Flask, jsonify, request
import PyPDF2
import spacy
from flask_cors import CORS
from collections import Counter
from io import BytesIO

nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Welcome to the Flask app!"

def extract_keywords(text):
    doc = nlp(text)
    keywords = [token.text for token in doc if token.pos_ in ["NOUN", "PROPN"]]
    common_keywords = Counter(keywords).most_common(10)
    return common_keywords

@app.route('/analyze-resume', methods=['POST'])
def analyze_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ''
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()
            keywords = extract_keywords(text)
            return jsonify({
                "content": text,
                "keywords": keywords
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Unsupported file format"}), 400

if __name__ == '__main__':
    app.run(debug=True)
