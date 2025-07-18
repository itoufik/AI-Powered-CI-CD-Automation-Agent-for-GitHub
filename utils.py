from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


def get_gpt_response(full_prompt: str, model="gpt-4") -> str:
    """Gets a response from the GPT-4 model.

    Args:
        full_prompt (str): The prompt to send to the model.
        model (str, optional): The model to use. Defaults to "gpt-4".

    Returns:
        str: The response from the model.
    """
    client = OpenAI(api_key=openai_api_key)

    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": full_prompt}]
    )

    return response.choices[0].message.content
