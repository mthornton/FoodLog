import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from food_db import nutrition_for_food_list, ids_for_description

# Load environment variables from .env file
load_dotenv()
key = os.getenv("OPEN_API_KEY")
client = OpenAI(api_key=key)

model = "gpt-4o-mini"
role = "You are a health and wellness consultant.  You provide personalized advice on nutrition, exercise, and overall well-being."


def id_for_description(db_path, description, options):
    model = "gpt-4o-mini"
    role = "You are a health and wellness consultant.  You provide personalized advice on nutrition, exercise, and overall well-being."

    messages=[
        {"role": "system", "content": role},
        {"role": "user", "content": f"I am looking for fdc_id of the food item that best match the description: '{description}'.  Here are some options with the fdc_id and description: {options}. Which one is the best match?  Reply with only a single fdc_id."}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    return response.choices[0].message.content.strip()


list = ids_for_description('./Data/Food.sqlite', 'breaded chicken breast')
fdc_id = id_for_description('./Data/Food.sqlite', 'chicken', list)
print(f"Selected FDC ID: {fdc_id}")
print(nutrition_for_food_list('./Data/Food.sqlite', fdc_id, 300))


'''tools = [
    {
        "type": "function",
        "function": {
            "name": "id_for_description",
            "description": "Get the FDC ID and description for a given food description",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "The description of the food item to search for"}
                },
                "required": ["description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "nutrition_for_food_list",
            "description": "Get a list of nutrition information for a given list of food items",
            "parameters": {
                "type": "object",
                "properties": {
                    "fdc_ids": {"type": "array", "items": {"type": "integer"}, "description": "List of FDC IDs for the food items"},
                    "servings": {"type": "array", "items": {"type": "number"}, "description": "List of serving sizes for each food item"}
                },
                "required": ["fdc_ids", "servings"]
            }
        }
    }    
]


messages=[
    {"role": "system", "content": role},
    {"role": "user", "content": "I ate 300g of chicken breast.  What is the nutritional information for that?"}
]


response = client.chat.completions.create(
    model=model,
    tools=tools,
    messages=messages
)


# IMPORTANT: Add assistant message (with tool_calls) to messages
assistant_message = response.choices[0].message
messages.append(assistant_message)



tool_call = response.choices[0].message.tool_calls[0]
if tool_call:
    print(tool_call)
    tool_name = tool_call.function.name
    print(f"Tool called: {tool_name} with arguments: {tool_call.function.arguments}")
    if tool_name == "id_for_description":
        # Parse JSON string into dict
        tool_args = json.loads(tool_call.function.arguments)
        description = tool_args.get("description")
        food_info = id_for_description('./Data/Food.sqlite', description)
        print(f"Food info: {food_info}")
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": food_info
        })

        response = client.chat.completions.create(
            model=model,
            messages=messages
        )

#list = nutrition_for_food_list('./Data/Food.sqlite', 2646170, 400)
#print(list)
print("BOT says:")
print(response.choices[0].message.content)
'''