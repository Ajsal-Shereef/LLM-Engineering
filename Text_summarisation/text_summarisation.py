#Import required libraries
import requests

from bs4 import BeautifulSoup
from IPython.display import Markdown, display

headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

# Constants

OLLAMA_API = "http://localhost:11434/api/chat"
HEADERS = {"Content-Type": "application/json"}
MODEL = "llama3.2"

#Webscrapping class
class WebScrap():
    def __init__(self, url):
        """
        Perform simple webscraping to extract data from a given website
        """
        self.url = url
        response = requests.get(self.url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title "
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip = True)
        
system_prompt = "You are an assistant that analyzes the contents of a website \
and provides a short summary, ignoring text that might be navigation related. \
Respond in markdown."

def get_user_prompt(website_content):
    """
    This function returns the user prompts given the website info
    """
    user_prompt = f"You are looking at a website titled {website_content.title}"
    user_prompt += "\nThe contents of this website is as follows; \
please provide a short summary of this website in markdown. \
If it includes news or announcements, then summarize these too.\n\n"
    user_prompt += website_content.text
    return user_prompt
        
def get_messages(website_content):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": get_user_prompt(website_content)}
    ]
    

def summarise(url):
    website_content = WebScrap(url)
    payload = {
        "model": MODEL,
        "messages": get_messages(website_content),
        "stream": False
    }
    response = requests.post(OLLAMA_API, json=payload, headers = HEADERS)
    print(response.json()['message']['content'])
    
summarise("https://cnn.com")
    


        