import sqlite3
import csv
import os
from datetime import datetime


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

    
def ids_for_description(db_path, description):
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


def nutrition_for_food_list(db_path, fdc_id, weight_in_grams=100):
    print(f"Fetching nutrition info for FDC ID: {fdc_id}, Weight: {weight_in_grams}g")

    percent = weight_in_grams / 100.0

    query = f"select fdc_id, description, protein * {percent} as protein, carbohydrates * {percent} as carbohydrates, calories * {percent} as calories, fiber * {percent} as fiber from food_nutrient_summary where fdc_id = {fdc_id}"

    try:
        # 1. Extract data from SQLite
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            data_list = cursor.fetchall()
            
            # Prepare headers and add 'logged_at' column
            headers = [column[0] for column in cursor.description]
            headers.append('logged_at')

        if not data_list:
            print("No data found for the specified criteria.")
            return

        return data_list
            

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # list = nutrition_for_food_list('./Data/Food.sqlite', 2646170, 400)
    list = ids_for_description('./Data/Food.sqlite', 'breaded chicken breast')
    # print(list)