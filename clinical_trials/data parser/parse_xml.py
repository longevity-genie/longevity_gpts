import sqlite3
import os
import xml.etree.ElementTree as ET
from pathlib import Path
import click


def create_database(db_name):
    """
    Create a SQLite database with the specified name and a table for storing XML data.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS studies (
        id INTEGER PRIMARY KEY,
        study_id TEXT,
        title TEXT,
        start_date TEXT,
        status TEXT,
        study_type TEXT,
        condition TEXT,
        phase TEXT,
        country TEXT,
        sponsor TEXT,
        sponsor_class TEXT,
        summary TEXT,
        gender TEXT,
        minimum_age REAL,
        maximum_age REAL,
        enrollment INTEGER,
        path TEXT
    )
    ''')

    conn.commit()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interventions (
            id INTEGER PRIMARY KEY,
            intervention_type TEXT,
            intervention_name TEXT,
            studies_id INTEGER,
            FOREIGN KEY("studies_id") REFERENCES "studies"("id")
        )
        ''')
    conn.commit()
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS studies_id_index ON interventions (studies_id)
    ''')
    conn.commit()
    return conn


def insert_data_into_database(conn, data):
    """
    Insert data into the SQLite database.
    """
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO studies (
        study_id,
        title,
        start_date,
        status,
        study_type,
        condition,
        phase,
        country,
        sponsor,
        sponsor_class,
        summary,
        gender,
        minimum_age,
        maximum_age,
        enrollment,
        path
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)

    # conn.commit()
    return cursor.lastrowid


def insert_into_interventions(conn, type:str, name:str, id:int):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO interventions (
            intervention_type,
            intervention_name,
            studies_id
        ) VALUES (?, ?, ?)
        ''', (type, name, id))

    # conn.commit()


def time_to_float(date_text:str):
    if (date_text is None) or (date_text == "N/A") or (date_text.strip() == ''):
        return None
    value, period = date_text.split(" ")
    value = int(value)
    # Define the number of days in a year to account for leap years
    days_in_year = 365.25
    # Conversion rates from each time unit to years
    conversion_rates = {
        'Year': 1,
        'Years': 1,
        'Months': 1 / 12,
        'Month': 1 / 12,
        'Weeks': 7 / days_in_year,
        'Week': 7 / days_in_year,
        'Days': 1 / days_in_year,
        'Day': 1 / days_in_year,
        'Hours': 1 / (24 * days_in_year),
        'Hour': 1 / (24 * days_in_year),
        'Minutes': 1 / (24 * 60 * days_in_year),
        'Minute': 1 / (24 * 60 * days_in_year),
    }
    # Ensure the period is correctly specified
    if period not in conversion_rates:
        raise ValueError(f"Invalid period '{period}'. Must be one of: {list(conversion_rates.keys())}.")
    # Convert the given value and period to years
    years = value * conversion_rates[period]
    return years


def convert_date_format(date_str):
    from datetime import datetime
    # Parse the input string to a datetime object assuming the first day of the month
    try:
        date_obj = datetime.strptime(date_str, '%B %Y')
    except:
        date_obj = datetime.strptime(date_str, '%B %d, %Y')

    # Convert the datetime object back to a string in the desired format "YYYY-MM-DD"
    new_date_str = date_obj.strftime('%Y-%m-%d')

    return new_date_str


def parse_xml_and_insert(file_path, conn):
    """
    Parse the XML file and insert the data into the database.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extracting relevant information
    study_id = root.find('.//nct_id').text if root.find('.//nct_id') is not None else ''
    title = root.find('.//brief_title').text if root.find('.//brief_title') is not None else ''
    start_date = convert_date_format(root.find('.//start_date').text) if root.find('.//start_date') is not None else ''
    status = root.find('.//overall_status').text if root.find('.//overall_status') is not None else ''
    study_type = root.find('.//study_type').text if root.find('.//study_type') is not None else ''
    condition = root.find('.//condition').text if root.find('.//condition') is not None else ''
    phase = root.find('.//phase').text if root.find('.//phase') is not None else ''

    # new fields
    country = root.find('.//location_countries/country').text if root.find('.//location_countries/country') is not None else ''
    sponsor = root.find('.//lead_sponsor/agency').text if root.find('.//lead_sponsor/agency') is not None else ''
    sponsor_class = root.find('.//lead_sponsor/agency_class').text if root.find('.//lead_sponsor/agency_class') is not None else ''
    summary = root.find('.//brief_summary/textblock').text if root.find('.//brief_summary/textblock') is not None else ''
    gender = root.find('.//eligibility/gender').text if root.find('.//eligibility/gender') is not None else ''
    minimum_age = root.find('.//eligibility/minimum_age').text if root.find('.//eligibility/minimum_age') is not None else ''
    minimum_age = time_to_float(minimum_age)
    maximum_age = root.find('.//eligibility/maximum_age').text if root.find('.//eligibility/maximum_age') is not None else ''
    maximum_age = time_to_float(maximum_age)
    enrollment = root.find('.//enrollment').text if root.find('.//enrollment') is not None else ''

    data = (study_id, title, start_date, status, study_type, condition, phase, country,
            sponsor, sponsor_class, summary, gender, minimum_age, maximum_age, enrollment, file_path)

    # Insert data into database
    id = insert_data_into_database(conn, data)
    interventions = root.findall('.//intervention')
    for element in interventions:
        intervention_type = element.find('.//intervention_type').text if element is not None else ''
        intervention_name = element.find('.//intervention_name').text if element is not None else ''
        insert_into_interventions(conn, intervention_type, intervention_name, id)


def process_all_xml_files_in_folder(folder_path, conn, size = 0):
    counter:int = 0
    for subdir, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(subdir, file)
                try:
                    parse_xml_and_insert(file_path, conn)
                    counter += 1
                    if counter % 1000 == 0:
                        print(f"processed: {counter}/{size}")
                        conn.commit()
                    # print(f"Processed file: {file_path}")
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
    conn.commit()


def estimate_files(folder_path):
    sum:int = 0
    for subdir, _, files in os.walk(folder_path):
        sum += len(files)

    return sum

@click.command()
@click.option('--data_path', default="xml",  help='path to the folder with folders with xml files')
@click.option('--database_name', default="studies_db.sqlite", help='database name')
def parse(data_path:str, database_name:str):
    conn = create_database(database_name)
    path = Path(data_path)
    size = estimate_files(path)
    process_all_xml_files_in_folder(path, conn, size)
    conn.close()

if __name__ == '__main__':
    parse()