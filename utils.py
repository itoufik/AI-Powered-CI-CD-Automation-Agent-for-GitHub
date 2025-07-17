from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

def get_gpt_response(full_prompt:str, model="gpt-4") -> str:
    client = OpenAI(api_key=openai_api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": full_prompt}]
    )

    return response.choices[0].message.content