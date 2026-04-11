import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from food_db import nutrition_for_food_list, ids_for_description, id_for_description

# Load environment variables from .env file
load_dotenv()
key = os.getenv("OPEN_API_KEY")
client = OpenAI(api_key=key)

model = "gpt-4o-mini"
role = "You are a health and wellness consultant.  You provide personalized advice on nutrition, exercise, and overall well-being.  If the user gives you a report on what they ate, estiamte the wieght in grams and computer the nutritional information."

meal = [
    {'item':'bread', 'weight':50},
    {'item':'ham', 'weight':100},
    {'item':'milk', 'weight':150}
]

tools = [
    {
        "type": "function",
        "function": {
            "name": "nutrition_info_for_meal",
            "description": "Returns a list of dictionaries of nutrition information for a supplied set of food.",
            "parameters": {
                "type": "object",
                "properties": {
                    "meal": {
                        "type": "array",
                        "description": "A list of food items in the meal.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "item": {
                                    "type": "string",
                                    "description": "The name of the food (e.g., 'chicken breast')"
                                },
                                "weight": {
                                    "type": "number",
                                    "description": "The weight of the food in grams"
                                }
                            },
                            "required": ["item", "weight"]
                        }
                    }
                },
                "required": ["meal"]
            }
        }
    }
]


def nutrition_info_for_meal(meal):
    meal_nut_info = []

    for item in meal:
        list = ids_for_description(item['item'])
        fdc_id = id_for_description(client, item['item'], list)
        nut_info = nutrition_for_food_list(fdc_id, item['weight'])
        meal_nut_info.append(nut_info)
        print(nut_info)

    write_daily_food_log(meal_nut_info)

    return meal_nut_info


def write_daily_food_log(daily_food_log_entry):
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"daily_food_log_{today}.log"
    file_path = os.path.join(os.getcwd(), filename)

    with open(file_path, "a", encoding="utf-8") as file:
        if os.path.getsize(file_path) > 0:
            file.write("\n")

        file.write(daily_food_log_entry)

    return {
        "status": "success",
        "file_path": file_path,
        "title": f"Daily Food Log {today}"
    }


prompt = ""

while prompt != "quit":
    prompt = input("you: ")

    if prompt != "quit":

        messages=[
            {"role": "system", "content": role},
            {"role": "user", "content": prompt}
        ]


        response = client.chat.completions.create(
            model=model,
            tools=tools,
            messages=messages
        )


        assistant_message = response.choices[0].message
        messages.append({
            "role": "assistant",
            "content": assistant_message.content or "",
            "tool_calls": [tool_call.model_dump() for tool_call in (assistant_message.tool_calls or [])]
        })

        tool_calls = assistant_message.tool_calls or []
        if tool_calls:
            for tool_call in tool_calls:
                print(tool_call)
                tool_name = tool_call.function.name
                print(f"Tool called: {tool_name} with arguments: {tool_call.function.arguments}")

                if tool_name == "nutrition_info_for_meal":
                    tool_args = json.loads(tool_call.function.arguments)
                    requested_meal = tool_args.get("meal", [])
                    food_info = nutrition_info_for_meal(requested_meal)
                    tool_content = json.dumps(food_info)
                    print(f"Food info: {food_info}")
                else:
                    tool_content = json.dumps({
                        "error": f"Unsupported tool: {tool_name}"
                    })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_content
                })

            response = client.chat.completions.create(
                model=model,
                tools=tools,
                messages=messages
            )

        print("BOT says:")
        print(response.choices[0].message.content)