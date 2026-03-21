import os
import base64
import json
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

SRC_DIR = Path(__file__).parent.parent
image_path = SRC_DIR / "images" / "plant.jpg"
context_path = SRC_DIR / "config" / "groq_context.txt"

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY is not set")

# funcion para decodificar una imagen a texto usando un modelo de lenguaje
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
# cargar contexto de mi agente AI

def load_context(context_path):
    with open(context_path, "r", encoding="utf-8") as f:
        return f.read()

#img to base64 string
base64_image = encode_image(image_path)

# cargar contexto
context = load_context(context_path)

client = Groq(
    api_key=groq_api_key,
)

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
plant_data = json.loads(response_text)
print(plant_data)