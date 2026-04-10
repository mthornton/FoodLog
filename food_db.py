import sqlite3
import csv
import os
from datetime import datetime

db_path = "./Data/Food.sqlite"


def build_where_clause(search_string):
    # Split string into individual words
    words = search_string.split()

    # Build conditions
    conditions = []
    for word in words:
        # Escape single quotes to avoid SQL errors
        safe_word = word.replace("'", "''")
        conditions.append(f"description LIKE '%{safe_word}%'")

    # Join conditions with OR
    where_clause = " OR ".join(conditions)

    return where_clause

    

def ids_for_description(description):
    print(f"Searching for description: {description}")

    where_clause = build_where_clause(description)
    query = f"select fdc_id, description from food_nutrient_summary where {where_clause}"
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            # return [row[0] for row in cursor.fetchall()]
            return cursor.fetchall()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []



def nutrition_for_food_list(fdc_id, weight_in_grams=100):
    print(f"Fetching nutrition info for FDC ID: {fdc_id}, Weight: {weight_in_grams}g")

    percent = weight_in_grams / 100.0

    # Use parameterized queries (?) to prevent SQL injection
    query = f"""
        SELECT 
            fdc_id, 
            description, 
            protein * ? AS protein, 
            carbohydrates * ? AS carbohydrates, 
            calories * ? AS calories, 
            fiber * ? AS fiber 
        FROM food_nutrient_summary 
        WHERE fdc_id = ?
    """

    try:
        with sqlite3.connect(db_path) as conn:
            # Set the row_factory to sqlite3.Row for dictionary-like access
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Pass parameters as a tuple
            cursor.execute(query, (percent, percent, percent, percent, fdc_id))
            rows = cursor.fetchall()

            if not rows:
                print("No data found for the specified criteria.")
                return []

            # Refactor: Convert rows to a list of dictionaries
            # This also handles adding the 'logged_at' key easily
            result = []
            for row in rows:
                row_dict = dict(row)
                row_dict['logged_at'] = None  # Or use a timestamp like datetime.now()
                result.append(row_dict)

            return result

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return []



def id_for_description(client, description, options):
    model = "gpt-4o-mini"
    role = "You are a health and wellness consultant.  You provide personalized advice on nutrition, exercise, and overall well-being."

    messages=[
        {"role": "system", "content": role},
        {"role": "user", "content": f"I am looking for fdc_id of the food item that best match the description: '{description}'.  Here are some options with the fdc_id and description: {options}. Which one is the best match?  Reply with only a single fdc_id and only include the fdc_id in the response."}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    return response.choices[0].message.content.strip()



#if __name__ == "__main__":
    # list = nutrition_for_food_list('./Data/Food.sqlite', 2646170, 400)
    # list = ids_for_description('breaded chicken breast')
    # print(list)