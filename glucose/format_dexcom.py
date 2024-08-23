import pandas as pd
from pathlib import Path
import typer


def process_csv(
        input_dir: Path = typer.Argument( help="Directory containing the input CSV files."),
        output_file: Path = typer.Argument( help="Path to save the processed CSV file."),
        event_type_filter: str = typer.Option('egv', help="Event type to filter by."),
        drop_duplicates: bool = typer.Option(True, help="Whether to drop duplicate timestamps."),
        time_diff_minutes: int = typer.Option(1, help="Minimum time difference in minutes to keep a row."),
        chunk_size: int = typer.Option(1000, help="Chunk size for the 'id' column increment. Set to 0 or None for a single id."),
) -> pd.DataFrame:

    # Read CSV file into a DataFrame
    filename=input_dir
    df = pd.read_csv(filename, low_memory=False)


    # Filter by Event Type and Event Subtype
    df = df[df['Event Type'].str.lower() == event_type_filter]
    df = df[df['Event Subtype'].isna()]

    # List of columns to keep
    columns_to_keep = [
        'Index',
        'Timestamp (YYYY-MM-DDThh:mm:ss)',
        'Glucose Value (mg/dL)',
    ]

    # Keep only the specified columns
    df = df[columns_to_keep]

    # Rename columns
    column_rename = {
        'Index': 'id',
        'Timestamp (YYYY-MM-DDThh:mm:ss)': 'time',
        'Glucose Value (mg/dL)': 'gl'
    }
    df = df.rename(columns=column_rename)

    
    # Handle id assignment based on chunk_size
    if chunk_size is None or chunk_size == 0:
        df['id'] = 1  # Assign the same id to all rows
    else:
        df['id'] = ((df.index // chunk_size) % (df.index.max() // chunk_size + 1)).astype(int)

    # Convert timestamp to datetime
    df['time'] = pd.to_datetime(df['time'])

    # Calculate time difference and keep rows with at least the specified time difference
    df['time_diff'] = df['time'].diff()
    df = df[df['time_diff'].isna() | (df['time_diff'] >= pd.Timedelta(minutes=time_diff_minutes))]

    # Drop the temporary time_diff column
    df = df.drop(columns=['time_diff'])

    # Ensure glucose values are in float64
    df['gl'] = df['gl'].astype('float64')

    # Optionally drop duplicate rows based on time
    if drop_duplicates:
        df = df.drop_duplicates(subset=['time'], keep='first')

    # Write the modified dataframe to a new CSV file
    df.to_csv(output_file, index=False)

    typer.echo("CSV files have been successfully merged, modified, and saved.")

    return df




def process_multiple_csv(
        input_dir: Path = typer.Argument('./raw_data/livia_unmerged', help="Directory containing the input CSV files."),
        output_file: Path = typer.Argument('./raw_data/livia_unmerged/livia_mini.csv', help="Path to save the processed CSV file."),
        event_type_filter: str = typer.Option('egv', help="Event type to filter by."),
        drop_duplicates: bool = typer.Option(True, help="Whether to drop duplicate timestamps."),
        time_diff_minutes: int = typer.Option(1, help="Minimum time difference in minutes to keep a row."),
        chunk_size: int = typer.Option(1000, help="Chunk size for the 'id' column increment. Set to 0 or None for a single id."),
):
    # Get all the CSV files in the specified directory
    all_files = list(input_dir.glob("*.csv"))

    # List to store the DataFrames
    df_list = []

    # Read each CSV file into a DataFrame and append to the list
    for filename in all_files:
        df = pd.read_csv(filename, low_memory=False)
        df_list.append(df)

    # Concatenate all DataFrames in the list
    combined_df = pd.concat(df_list, ignore_index=True)

    # Filter by Event Type and Event Subtype
    combined_df = combined_df[combined_df['Event Type'].str.lower() == event_type_filter]
    combined_df = combined_df[combined_df['Event Subtype'].isna()]

    # List of columns to keep
    columns_to_keep = [
        'Index',
        'Timestamp (YYYY-MM-DDThh:mm:ss)',
        'Glucose Value (mg/dL)',
    ]

    # Keep only the specified columns
    combined_df = combined_df[columns_to_keep]

    # Rename columns
    column_rename = {
        'Index': 'id',
        'Timestamp (YYYY-MM-DDThh:mm:ss)': 'time',
        'Glucose Value (mg/dL)': 'gl'
    }
    combined_df = combined_df.rename(columns=column_rename)

    # Sort the combined DataFrame by timestamp
    combined_df = combined_df.sort_values('time')

    # Handle id assignment based on chunk_size
    if chunk_size is None or chunk_size == 0:
        combined_df['id'] = 1  # Assign the same id to all rows
    else:
        combined_df['id'] = ((combined_df.index // chunk_size) % (combined_df.index.max() // chunk_size + 1)).astype(int)

    # Convert timestamp to datetime
    combined_df['time'] = pd.to_datetime(combined_df['time'])

    # Calculate time difference and keep rows with at least the specified time difference
    combined_df['time_diff'] = combined_df['time'].diff()
    combined_df = combined_df[combined_df['time_diff'].isna() | (combined_df['time_diff'] >= pd.Timedelta(minutes=time_diff_minutes))]

    # Drop the temporary time_diff column
    combined_df = combined_df.drop(columns=['time_diff'])

    # Ensure glucose values are in float64
    combined_df['gl'] = combined_df['gl'].astype('float64')

    # Optionally drop duplicate rows based on time
    if drop_duplicates:
        combined_df = combined_df.drop_duplicates(subset=['time'], keep='first')

    # Write the modified dataframe to a new CSV file
    combined_df.to_csv(output_file, index=False)

    typer.echo("CSV files have been successfully merged, modified, and saved.")

if __name__ == "__main__":
    typer.run(process_csv)
