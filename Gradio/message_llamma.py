import ollama
import gradio as gr

#ollama API
OLLAMA_API = "http://localhost:11434/api/chat"
MODEL = "llama3.2"

system_message = "You are a helpful assistant"

def shout(text):
    return text.upper()

def message_llama(prompt):
    message = [{"role" : "system", "content": system_message},
               {"role" : "user" , "content": prompt}]
    response = ollama.chat(model = MODEL, messages = message, stream=True)
    result = ""
    for chunk in response:
        if "message" in chunk and "content" in chunk["message"]:
            result += chunk["message"]["content"]
            yield result
    
gr.Interface(fn=message_llama, inputs='textbox', outputs="textbox").launch()