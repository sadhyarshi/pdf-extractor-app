from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import fitz  # PyMuPDF
from googletrans import Translator

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def extract_text_with_font_and_coordinates(page):
    text_with_font_and_coordinates = []
    blocks = page.get_text("dict")["blocks"]

    for b in blocks:
        for l in b.get("lines", []):
            for s in l.get("spans", []):
                font_flags = s.get("flags", 0)
                font_style = ""
                if font_flags & 1 << 0:
                    font_style += "bold "
                if font_flags & 1 << 1:
                    font_style += "italic "
                if font_flags & 1 << 2:
                    font_style += "underline "
                if font_flags & 1 << 3:
                    font_style += "strikethrough "
                if font_flags & 1 << 4:
                    font_style += "superscript "
                if font_flags & 1 << 5:
                    font_style += "subscript "

                font_family = s.get("font", "Unknown")
                if "bold" in font_family.lower() or "black" in font_family.lower() or "heavy" in font_family.lower():
                    font_style += "bold "
                if "italic" in font_family.lower():
                    font_style += "italic "

                text_with_font_and_coordinates.append({
                    "text": s.get("text", ""),
                    "font_size": s.get("size", 0),
                    "font_family": font_family,
                    "font_color": s.get("color", (0, 0, 0)),
                    "font_style": font_style.strip(),
                    "left": s.get("bbox", (0, 0, 0, 0))[0],
                    "top": s.get("bbox", (0, 0, 0, 0))[1],
                    "width": s.get("bbox", (0, 0, 0, 0))[2] - s.get("bbox", (0, 0, 0, 0))[0],
                    "height": s.get("bbox", (0, 0, 0, 0))[3] - s.get("bbox", (0, 0, 0, 0))[1]
                })

    return text_with_font_and_coordinates

#def translate_text(text, target_language):
   # translator = Translator()
   # translated_text = translator.translate(text, dest=target_language).text
   # return translated_text

def rgb_to_hex(rgb):
    r, g, b = rgb
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

def convert_color_to_hex(rgb_color):
    if isinstance(rgb_color, int):
        r = (rgb_color >> 16) & 0xFF
        g = (rgb_color >> 8) & 0xFF
        b = rgb_color & 0xFF
        rgb_color = (r, g, b)
    font_color_hex = rgb_to_hex(rgb_color)
    return font_color_hex

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file provided'}), 400
   # target_language = request.form.get('language', 'en')  # Default to English

    translated_data = {}
    pdf_file = file.stream.read()  # Read file stream
    doc = fitz.open(stream=pdf_file, filetype='pdf')

    for page_number in range(len(doc)):
        page = doc[page_number]
        page_width = page.rect.width
        page_height = page.rect.height

        page_data = {
            "height": page_height,
            "width": page_width,
            "data": []
        }
        
        translated_data[str(page_number)] = page_data
        text_with_font_and_coordinates = extract_text_with_font_and_coordinates(page)

        for item in text_with_font_and_coordinates:
            original_text = item["text"]
           # translated_text = translate_text(original_text, target_language)
            end_left = item["left"] + item["width"]
            end_top = item["top"] + item["height"]
            font_color_hex = convert_color_to_hex(item["font_color"])

            page_data["data"].append({
                "original_text": original_text,
                #"translated_text": translated_text,
                "font_size": item["font_size"],
                "font_family": item["font_family"],
                "font_color": item["font_color"],
                "font_color_hex": font_color_hex,
                "font_style": item["font_style"],
                "left": item["left"],
                "top": item["top"],
                "end_left": end_left,
                "end_top": end_top
            })

    return jsonify(translated_data)

if __name__ == "__main__":
    app.run(debug=True)
