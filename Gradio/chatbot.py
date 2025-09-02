import ollama
import gradio as gr

OLLAMA_API = "http://localhost:11434/api/chat"
MODEL = "llama3.2"

system_message = "You are a helpful assistant in a clothes store. You should try to gently encourage \
the customer to try items that are on sale. Hats are 60% off, and most other items are 50% off. \
For example, if the customer says 'I'm looking to buy a hat', \
you could reply something like, 'Wonderful - we have lots of hats - including several that are part of our sales event.'\
Encourage the customer to buy hats if they are unsure what to get."

def chat(message, history):
    message = [{"role" : "system", "content" : system_message}] + history + [{"role" : "user", "content" : message}]
    response = ollama.chat(model = MODEL, messages = message, stream = True)
    result = ""
    for chunk in response:
        if "message" in chunk and "content" in chunk["message"]:
            result += chunk["message"]["content"]
            yield result

gr.ChatInterface(fn=chat, type="messages").launch()        