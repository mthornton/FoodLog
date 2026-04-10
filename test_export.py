import sqlite3
import csv
import os
from datetime import datetime

def export_food_data(db_path, output_file):
    # The SQL query as provided
    
    weight_in_grams = 300
    percent = weight_in_grams / 100.0

    query = f"""
        select f.fdc_id, f.description, fn.nutrient_id, n.name, fn.amount * {percent} as amount , n.unit_name
        from food f inner join food_nutrients fn on f.fdc_id = fn.fdc_id
        inner join nutrients n on fn.nutrient_id = n.id
        where f.fdc_id = 2646170 and fn.nutrient_id in (1003, 1005, 2047, 1079);
    """

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

        # 2. Check if we need to write headers (only if file doesn't exist/is empty)
        file_exists = os.path.isfile(output_file) and os.path.getsize(output_file) > 0

        # 3. Append data to food_log.csv
        with open(output_file, mode='a', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            
            if not file_exists:
                writer.writerow(headers)
            
            # Current timestamp in YYYY-MM-DD HH:MM:SS format
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 4. Transform and Load: Add timestamp to each record and write
            for row in data_list:
                # Convert tuple to list to allow appending the timestamp
                record = list(row)
                record.append(current_time)
                writer.writerow(record)
            
        print(f"Success! Data appended to {output_file} at {current_time}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Ensure this matches your local database filename
    export_food_data('./Data/Food.sqlite', 'food_log.csv')