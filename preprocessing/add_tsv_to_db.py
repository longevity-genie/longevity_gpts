import polars as pl
import sqlite3
import typer
import os

def polars_dtype_to_sqlite(dtype: pl.DataType) -> str:
    """
    Map Polars data types to SQLite data types.
    
    Parameters:
        dtype (pl.DataType): Polars data type.
    
    Returns:
        str: Corresponding SQLite data type.
    """
    if dtype in [pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64]:
        return 'INTEGER'
    elif dtype in [pl.Float32, pl.Float64]:
        return 'REAL'
    elif dtype == pl.Boolean:
        return 'INTEGER'
    elif dtype == pl.Utf8:
        return 'TEXT'
    elif dtype in [pl.Date, pl.Datetime, pl.Time]:
        return 'TEXT'
    else:
        return 'BLOB'

def main(
    tsv_file: str = typer.Argument(..., help="Path to the input TSV file"),
    sqlite_db_file: str = typer.Argument(..., help="Path to the SQLite database file (will be created if it doesn't exist)"),
    table_name: str = typer.Argument(..., help="Name of the new table to create"),
):
    """
    Read a TSV file and import its data into a new table in a SQLite database.
    If the database file does not exist, it will be created.

    Parameters:
        tsv_file (str): Path to the input TSV file.
        sqlite_db_file (str): Path to the SQLite database file.
        table_name (str): Name of the new table to create.
    """
    # Read TSV file into a Polars DataFrame
    df = pl.read_csv(tsv_file, separator='\t')
    
    # Get the schema of the DataFrame
    schema = df.schema
    
    # Map Polars data types to SQLite data types and construct column definitions
    columns = []
    for col_name, dtype in schema.items():
        sqlite_type = polars_dtype_to_sqlite(dtype)
        columns.append(f'"{col_name}" {sqlite_type}')
    
    # Create SQL statement for creating a new table
    columns_sql = ', '.join(columns)
    create_table_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_sql});'
    
    # Ensure the directory for the SQLite database exists
    db_dir = os.path.dirname(sqlite_db_file)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"Created directory for database at '{db_dir}'.")

    # Connect to the SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect(sqlite_db_file)
    cursor = conn.cursor()
    
    # Create the new table
    cursor.execute(create_table_sql)
    conn.commit()
    
    # Prepare the INSERT statement
    column_names = df.columns
    quoted_column_names = [f'"{col}"' for col in column_names]
    columns_sql = ', '.join(quoted_column_names)
    placeholders = ', '.join(['?'] * len(column_names))
    insert_sql = f'INSERT INTO "{table_name}" ({columns_sql}) VALUES ({placeholders})'
    
    # Convert DataFrame to list of tuples for insertion
    data = df.to_numpy().tolist()
    
    # Insert the data into the table
    cursor.executemany(insert_sql, data)
    conn.commit()
    
    # Close the database connection
    conn.close()
    print(f"Data from '{tsv_file}' has been imported into table '{table_name}' in '{sqlite_db_file}'.")

if __name__ == "__main__":
    typer.run(main)
