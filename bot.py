import os
import json
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
# not sure why the call to OpenAI does not find it automatically, but this is the workaround
load_dotenv()
key = os.getenv("OPEN_API_KEY")
client = OpenAI(api_key=key)

model = "gpt-4o-mini"
role = "You are a helpful assistant.  Extract the food items and their quantities in grams from the user's message and return them in a JSON format.  The JSON should have a list titled 'food_items' with entries for each with 'name' and 'quantity_in_grams'.  Return just the json."


def extract_food_list(json_data):
    """
    Parses a JSON object and returns a list of food item details.
    
    Args:
        json_data (str or dict): The JSON input containing 'food_items'.
        
    Returns:
        list: A list of formatted strings (or tuples/dicts depending on preference).
    """
    # If the input is a string, parse it into a dictionary
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data
    
    # Extract the list, defaulting to an empty list if the key is missing
    items = data.get("food_items", [])
    
    # Return a list of formatted strings
    return [{"name": item['name'], "grams": item['quantity_in_grams']} for item in items]


def get_weather(location: str):
    print("In tool")
    return f"The weather in {location} is sunny with a high of 25°C and a low of 15°C."

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"}
            },
            "required": ["location"]
        }
    }
}]


messages=[
    {"role": "system", "content": role},
    {"role": "user", "content": "What is the weather in New York City?"}
]

response = client.chat.completions.create(
    model=model,
    tools=tools,
    messages=messages
)

assistant_message = response.choices[0].message

# IMPORTANT: Add assistant message (with tool_calls) to messages
messages.append(assistant_message)



tool_call = response.choices[0].message.tool_calls[0]
if tool_call:
    print(tool_call)
    tool_name = tool_call.function.name
    print(f"Tool called: {tool_name} with arguments: {tool_call.function.arguments}")
    if tool_name == "get_weather":
        # Parse JSON string into dict
        tool_args = json.loads(tool_call.function.arguments)
        location = tool_args.get("location")
        weather_info = get_weather(location)
        print(f"Weather info: {weather_info}")
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": weather_info
        })

        response = client.chat.completions.create(
            model=model,
            messages=messages
        )

print(response.choices[0].message.content)
