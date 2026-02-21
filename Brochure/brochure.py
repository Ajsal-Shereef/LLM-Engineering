
import os
import json
import requests

from openai import OpenAI
from dotenv import load_dotenv
from scrapper import *
from IPython.display import Markdown, display, update_display
from rich.console import Console
from rich.markdown import Markdown as RichMarkdown
from rich.live import Live

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

openai = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

website_selection_model = "arcee-ai/trinity-large-preview:free"
brochure_model = "arcee-ai/trinity-large-preview:free"

link_system_prompt = """
You are provided with a list of links found on a webpage.
You are able to decide which of the links would be most relevant to include in a brochure about the company,
such as links to an About page, or a Company page, or Careers/Jobs pages.
You should respond in JSON as in this example:

{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}
"""

def get_links_user_prompt(url):
    user_prompt = f"""
Here is the list of links on the website {url} -
Please decide which of these are relevant web links for a brochure about the company, 
respond with the full https URL in JSON format.
Do not include Terms of Service, Privacy, email links.

Links (some might be relative links):

"""
    links = fetch_website_links(url)
    user_prompt += "\n".join(links)
    return user_prompt

def select_relevant_links(url):
    print(f"Selecting relevant links for {url} by calling {website_selection_model}")
    response = openai.chat.completions.create(
        model=website_selection_model,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(url)}
        ],
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    links = json.loads(result)
    print(f"Found {len(links['links'])} relevant links")
    return links

def fetch_page_and_all_relevant_links(url):
    contents = fetch_website_contents(url)
    relevant_links = select_relevant_links(url)
    result = f"## Landing Page:\n\n{contents}\n## Relevant Links:\n"
    for link in relevant_links['links']:
        result += f"\n\n### Link: {link['type']}\n"
        result += fetch_website_contents(link["url"])
    return result

brochure_system_prompt = """
You are an assistant that analyzes the contents of several relevant pages from a company website
and creates a short brochure about the company for prospective customers, investors and recruits.
Respond in markdown without code blocks.
Include details of company culture, customers and careers/jobs if you have the information.
"""

def get_brochure_user_prompt(company_name, url):
    user_prompt = f"""
You are looking at a company called: {company_name}
Here are the contents of its landing page and other relevant pages;
use this information to build a short brochure of the company in markdown without code blocks.\n\n
"""
    user_prompt += fetch_page_and_all_relevant_links(url)
    user_prompt = user_prompt[:5_000] # Truncate if more than 5,000 characters
    return user_prompt

def create_brochure(company_name, url):
    response = openai.chat.completions.create(
        model=brochure_model,
        messages=[
            {"role": "system", "content": brochure_system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
        ],
    )
    result = response.choices[0].message.content
    console = Console()
    console.print(RichMarkdown(result))

# create_brochure("HuggingFace", "https://huggingface.co")

def stream_brochure(company_name, url):
    stream = openai.chat.completions.create(
        model = brochure_model,
        messages = [
            {"role" : "system", "content" : brochure_system_prompt},
            {"role" : "user", "content" : get_brochure_user_prompt(company_name, url)}
        ],
        stream = True
    )
    response = ""
    with Live(RichMarkdown(response), refresh_per_second=10) as live:
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                response += content
                live.update(RichMarkdown(response))

stream_brochure("HuggingFace", "https://huggingface.co")