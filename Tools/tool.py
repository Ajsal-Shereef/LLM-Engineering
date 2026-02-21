
import os
import json
import gradio as gr

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
endpoint = "https://openrouter.ai/api/v1"
model = "stepfun/step-3.5-flash:free"

openai = OpenAI(api_key=api_key, base_url=endpoint)

system_message = """
You are a helpful assistant for an Airline called FlightAI.
Give short, courteous answers, no more than 1 sentence.
Always be accurate. If you don't know the answer, say so.
"""

ticket_prices = {"london": "$799", "paris": "$899", "tokyo": "$1400", "berlin": "$499"}

def get_ticket_price(destination_city):
    print(f"Tool called for city {destination_city}")
    price = ticket_prices.get(destination_city.lower(), "Unknown ticket price")
    return f"The price of a ticket to {destination_city} is {price}"

price_function = {
    "name" : "get_ticket_price",
    "description" : "Get the price of the return ticket to the destination city",
    "parameters" : {
        "type" : "object",
        "properties" : {
            "destination_city" : {
                "type" : "string",
                "description" : "The destination city"
            },
        },
        "required" : ["destination_city"],
        "additionalProperties" : False
    },
}
tools = [{"type": "function", "function": price_function}]

def handle_tool_calls(message):
    tool_call = message.tool_calls[0]
    if tool_call.function.name == "get_ticket_price":
        arguments = json.loads(tool_call.function.arguments)
        city = arguments.get('destination_city')
        price_details = get_ticket_price(city)
        response = {
            "role" : "tool",
            "content" : price_details,
            "tool_call_id" : tool_call.id,
        }
    return response

def chat(message, history):
    history = [{"role":h["role"], "content":h["content"]} for h in history]
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=model, messages=messages, tools=tools, stream=False)
    while response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        tool_response = handle_tool_calls(message)
        messages.append(message)
        messages.append(tool_response)
        response = openai.chat.completions.create(model=model, messages=messages, tools=tools, stream=False)

    return response.choices[0].message.content

gr.ChatInterface(fn=chat, type="messages").launch()

