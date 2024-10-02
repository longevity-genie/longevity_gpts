import sqlite3
from pathlib import Path
import argparse

def extract_db_structure(db_path):
    """
    Connects to the SQLite database at db_path and extracts the structure
    (table names and column definitions) of all tables in the database.
    
    Parameters:
        db_path (str or Path): The path to the SQLite database file.
        
    Returns:
        dict: A dictionary where keys are table names and values are lists of
              dictionaries containing column information.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to get all table names in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Loop through the tables and get their schema
    db_structure = {}
    for table in tables:
        table_name = table[0]  # Extract the table name from the tuple
        # Get the table schema using PRAGMA table_info
        cursor.execute(f"PRAGMA table_info('{table_name}');")
        columns = cursor.fetchall()
        # Each column is a tuple: (cid, name, type, notnull, dflt_value, pk)
        column_info = []
        for column in columns:
            col_dict = {
                'cid': column[0],
                'name': column[1],
                'type': column[2],
                'notnull': bool(column[3]),
                'dflt_value': column[4],
                'pk': bool(column[5])
            }
            column_info.append(col_dict)
        db_structure[table_name] = column_info

    # Close the connection
    conn.close()

    return db_structure

def print_db_structure(db_structure):
    """
    Prints the database structure in a readable format.
    
    Parameters:
        db_structure (dict): The database structure as returned by extract_db_structure.
    """
    for table_name, columns in db_structure.items():
        print(f"Table: {table_name}")
        print("Columns:")
        for col in columns:
            pk = 'PRIMARY KEY' if col['pk'] else ''
            notnull = 'NOT NULL' if col['notnull'] else ''
            default = f"DEFAULT {col['dflt_value']}" if col['dflt_value'] else ''
            constraints = ' '.join(filter(None, [pk, notnull, default]))
            print(f"  - {col['name']} ({col['type']}) {constraints}")
        print("\n")  # Add an empty line after each table for readability

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract SQLite database structure.')
    parser.add_argument('db_path', help='Path to the SQLite database file')

    args = parser.parse_args()

    # Check if the database file exists
    db_file = Path(args.db_path)
    if not db_file.is_file():
        print(f"Error: Database file '{db_file}' does not exist.")
    else:
        # Extract the database structure
        db_structure = extract_db_structure(db_file)

        # Print the database structure
        print_db_structure(db_structure)
