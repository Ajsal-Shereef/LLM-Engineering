import os
import gradio as gr

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

endpoint = "https://openrouter.ai/api/v1"
MODEL = "stepfun/step-3.5-flash:free"

openai = OpenAI(api_key=api_key, base_url=endpoint)

system_message = "You are a helpful assistant in a clothes store. You should try to gently encourage \
the customer to try items that are on sale. Hats are 60% off, and most other items are 50% off. \
For example, if the customer says 'I'm looking to buy a hat', \
you could reply something like, 'Wonderful - we have lots of hats - including several that are part of our sales event.'\
Encourage the customer to buy hats if they are unsure what to get."

def chat(message, history):
    history = [{"role":h["role"], "content":h["content"]} for h in history]
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL, messages=messages, stream=True)
    result = ""
    for chunk in response:
        result += chunk.choices[0].delta.content
        yield result


gr.ChatInterface(fn=chat, type="messages").launch()        