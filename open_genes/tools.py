import sqlite3
from pathlib import Path


def db_query(sql:str):
    """ This function execute query on open-genes sqlite table. It returns query results. """
    dbpath = Path(Path(__file__).parent, "data", "open_genes.sqlite")
    conn = sqlite3.connect(dbpath, isolation_level='DEFERRED')
    cursor = conn.cursor()
    
    # Print the SQL query
    print(f"Executing SQL query: {sql}")
    
    cursor.execute(sql)
    try:
        rows = cursor.fetchall()
        if rows is None or len(rows) == 0:
            conn.close()
            return ""
        names = [description[0] for description in cursor.description]
        text = "; ".join(names) + "\n"
        for row in rows:
            row = [str(i) for i in row]
            text += "; ".join(row) + "\n"
    finally:
        conn.close()

    return text
