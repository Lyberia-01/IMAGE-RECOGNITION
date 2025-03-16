import os
import base64
from io import BytesIO
from dotenv import load_dotenv

import google.generativeai as genai
from flask import Flask, jsonify, request
from PIL import Image

load_dotenv()

API_KEY = os.environ.get("API_KEY")

genai.configure(api_key=API_KEY)

app = Flask(__name__)

@app.route("/api/process_image", methods=["POST"])
def process_image():
    if request.method == "POST":
        try:
            data = request.get_json()
            base64_image = data.get("image")
            prompt = data.get("prompt", "Describe this image.")

            image_bytes = base64.b64decode(base64_image)
            image = Image.open(BytesIO(image_bytes))

             # Convert RGBA to RGB if ever needed
            if image.mode == "RGBA":
                image = image.convert("RGB")

            image_path = "temp_image.jpg"
            image.save(image_path)

            with open(image_path, "rb") as image_file:
                image_data = image_file.read()

            contents = [
                {
                    "parts": [
                        {"mime_type": "image/jpeg", "data": base64.b64encode(image_data).decode('utf-8')},
                        {"text": prompt},
                    ]
                }
            ]

            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            response = model.generate_content(contents)

            os.remove(image_path)

            return jsonify({"result": response.text})

        except Exception as e:
            return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(port=int(os.environ.get('PORT', 80)))