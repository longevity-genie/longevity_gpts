import os
import sqlite3
import pandas as pd
import typer

app = typer.Typer()


def get_enumerations(db_path):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    results = []
    
    for table_name in tables:
        table_name = table_name[0]  # Extract table name from tuple
        
        # Get column names for each table
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        # Skip the first column and process the rest
        for column in columns[1:]:
            column_name = column[1]  # Column name is the second element in the tuple
            column_type = column[2].lower()  # Column type is the third element

             # Only process text columns (excluding numeric types)
            if ('int' not in column_type and 'float' not in column_type and 'real' not in column_type
                and column_name.lower() not in ['doi','pmid','genotype', 'nucleotide substitution','line']):
         

                # Quote the column name to handle spaces and special characters
                quoted_column_name = f'"{column_name}"'

                # Get total count and distinct count
                cursor.execute(f"SELECT COUNT(*) as total, COUNT(DISTINCT {quoted_column_name}) as distinct_count FROM {table_name};")
                total, distinct_count = cursor.fetchone()

                if total > 0 and distinct_count <= total / 2:

                
                    # Query for distinct values in the column
                    cursor.execute(f"SELECT DISTINCT {quoted_column_name} FROM {table_name};")
                    enumerations = [row[0] for row in cursor.fetchall()]
                    
                    # Append the result to the list
                    results.append({
                        "table_name": table_name,
                        "column_name": column_name,
                        "enumerations": enumerations
                    })
    
    # Close the connection
    conn.close()

    # Write results to file
    write_to_file(results, "enumerations_output.txt")
    
    return results

def write_to_file(data, filename):
    # Check if file exists; if not, create it or overwrite if it does
    if os.path.exists(filename):
        print(f"{filename} exists. It will be overwritten.")
    else:
        print(f"{filename} does not exist. It will be created.")
    
    with open(filename, 'w') as file:
        for entry in data:
            file.write(f"Table: {entry['table_name']}\n")
            file.write(f"Column: {entry['column_name']}\n")
            file.write("Enumerations:\n")
            for value in entry['enumerations']:
                file.write(f"  - {value}\n")
            file.write("\n" + "-"*50 + "\n\n")

@app.command()
def extract(
      db_path: str = typer.Argument(..., help="Path to the SQLite database"),
      output: str = typer.Option("enumerations_output.txt", "--output", "-o", help="Output file name")
):
    """
    Extract enumerations from SQLite database and write to a file.
    """
    enumerations = get_enumerations(db_path)
    
    # Write results to the specified output file
    write_to_file(enumerations, output)
    
    # Convert to a DataFrame for easy viewing if needed
    enumerations_df = pd.DataFrame(enumerations)
    typer.echo(enumerations_df)

if __name__ == "__main__":
    app()