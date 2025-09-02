import ollama
import requests
import gradio as gr
from bs4 import BeautifulSoup

#ollama API
OLLAMA_API = "http://localhost:11434/api/chat"
MODEL = "llama3.2"

system_message = "You are an assistant that analyzes the contents of a company website landing page \
and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown."

class Website:
    def __init__(self, url):
        self.url = url
        response = requests.get(url)
        self.body = response.content
        soup = BeautifulSoup(self.body, "html.parser")
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator= "\n", strip = True)
        
    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"

def message_llama(prompt):
    message = [{"role" : "system", "content": system_message},
               {"role" : "user" , "content": prompt}]
    response = ollama.chat(model = MODEL, messages = message, stream=True)
    result = ""
    for chunk in response:
        if "message" in chunk and "content" in chunk["message"]:
            result += chunk["message"]["content"]
            yield result

def stream_brochure(company_name, url, tone):
    user_prompt = f"Please generate the company brochure for {company_name}. Here is tha landing page \
        and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown and use {tone} tone"
    user_prompt += Website(url).get_contents()
    response = message_llama(user_prompt)
    yield from response
    
gr.Interface(fn=stream_brochure, 
             inputs=[gr.Textbox(label="Company name"),
                     gr.Textbox(label="Landing page URL including http:// or https://"),
                     gr.Dropdown(["Humaric", "Professional", "Ugly", "Romantic", "Emojify"], label="Select tone")], 
             outputs=[gr.Markdown(label="Brochure:")]).launch()
    

