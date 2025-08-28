#imports
import requests
import ollama

from rich.console import Console
from rich.markdown import Markdown

#ollama API
OLLAMA_API = "http://localhost:11434/api/chat"

# Create a console object
console = Console()

#prompts
question = """
Please explain what this code does and why:
yield from {book.get("author") for book in books if book.get("author")}
"""
system_prompt = "You are an assistant to understand python code and provide explanations line by line"
user_prompt = "Explain the below code line by line with comments" + question

message = [{"role" : "system", "content" : system_prompt},
           {"role" : "user", "content" : user_prompt}]

response = ollama.chat(model="llama3.2", messages = message)
reply = response["message"]["content"]
# Use the rich console to print the Markdown object
console.print(Markdown(reply))