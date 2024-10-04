import sqlite3
from pathlib import Path
import argparse
import json

def extract_db_examples(db_path, num_examples=5):
    """
    Connects to the SQLite database at db_path and extracts example values
    for each column in each table.
    
    Parameters:
        db_path (str or Path): The path to the SQLite database file.
        num_examples (int): Number of examples to extract for each column.
        
    Returns:
        dict: A dictionary where keys are table names and values are dictionaries
              of column names with lists of example values.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    db_examples = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info('{table_name}');")
        columns = [col[1] for col in cursor.fetchall()]
        
        db_examples[table_name] = {}
        for column in columns:
            cursor.execute(f"SELECT [{column}] FROM [{table_name}] LIMIT {num_examples};")
 
            examples = [row[0] for row in cursor.fetchall()]
            db_examples[table_name][column] = examples

    conn.close()
    return db_examples

def write_examples_to_file(db_examples, output_file):
    """
    Writes the database examples to a JSON file.
    
    Parameters:
        db_examples (dict): The database examples as returned by extract_db_examples.
        output_file (str or Path): The path to the output JSON file.
    """
    with open(output_file, 'w') as f:
        json.dump(db_examples, f, indent=2, default=str)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract SQLite database examples.')
    parser.add_argument('db_path', help='Path to the SQLite database file')
    parser.add_argument('output_file', help='Path to the output JSON file')
    parser.add_argument('--num_examples', type=int, default=5, help='Number of examples to extract for each column')

    args = parser.parse_args()

    db_file = Path(args.db_path)
    if not db_file.is_file():
        print(f"Error: Database file '{db_file}' does not exist.")
    else:
        db_examples = extract_db_examples(db_file, args.num_examples)
        write_examples_to_file(db_examples, args.output_file)
        print(f"Database examples have been written to {args.output_file}")