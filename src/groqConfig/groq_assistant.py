import os
import base64
import json
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

# 1. Obtenemos la ruta exacta de la carpeta groqConfig
CURRENT_DIR = Path(__file__).parent

# 2. Le decimos que el contexto está en esa misma carpeta
DEFAULT_CONTEXT_PATH = CURRENT_DIR / "groq_context.txt"

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY is not set")

client = Groq(
    api_key=groq_api_key,
)

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
def load_context(context_path):
    with open(context_path, "r", encoding="utf-8") as f:
        return f.read()

# 3. Le pasamos DEFAULT_CONTEXT_PATH como valor por defecto
def analyze_plant(image_path, specimen_data: dict, context_path=DEFAULT_CONTEXT_PATH):
        
        base64_image = encode_image(image_path)
        context = load_context(context_path)

        specimen_info = json.dumps(specimen_data, ensure_ascii=False)

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": context,
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": specimen_info
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
        )

        response_text = chat_completion.choices[0].message.content
        return json.loads(response_text)

