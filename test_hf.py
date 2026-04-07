import os
from openai import OpenAI

model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
client = OpenAI(
    base_url=f"https://api-inference.huggingface.co/models/{model_id}/v1",
    api_key=os.environ.get("HF_TOKEN", "sk-placeholder")
)

try:
    response = client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": "Hi"}],
        max_tokens=10
    )
    print("Success model url:", response.choices[0].message.content)
except Exception as e:
    print(f"Error model url: {e}")
