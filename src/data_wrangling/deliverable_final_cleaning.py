import os
import pandas as pd

current_directory = os.getcwd()
data_directory = os.path.join(current_directory, 'data')
input_directory = os.path.join(data_directory, 'deliverable_obligations', 'intermediate')
output_directory = os.path.join(data_directory, 'deliverable_obligations', 'final')

csv_files = [f for f in os.listdir(input_directory) if f.endswith('.csv')]

for file in csv_files:
    input_file_path = os.path.join(input_directory, file)
    df = pd.read_csv(input_file_path)

    # Skip if the DataFrame is empty or has only one column
    if df.empty or len(df.columns) < 2:
        print(f"Skipping file with insufficient columns: {file}")
        output_file_path = os.path.join(output_directory, file)
        df.to_csv(output_file_path, index=False)
        continue

    # Exclude the first column, apply the function that checks if a cell contains 'not applicable', 'credit', or 'tranche' (ignoring case),
    # and drop rows where all cells return True for 'not applicable' or any cell returns True for 'credit' or 'tranche'
    df = df[~df.iloc[:, 1:].applymap(lambda x: str(x).strip().lower() == 'not applicable').all(axis=1)]
    df = df[~df.applymap(lambda x: 'credit' in str(x).strip().lower()).any(axis=1)]
    df = df[~df.iloc[:, 1].apply(lambda x: 'tranche' in str(x).strip().lower())]

    # If there are at least three columns, drop rows where the third column (index 2) contains 'N / A', ignoring case
    if len(df.columns) > 2:
        df = df[~((df.iloc[:, 1].apply(lambda x: str(x).strip().lower() == 'not applicable')) & (df.iloc[:, 2:].isna().all(axis=1)))]
        df = df[~df.iloc[:, 2].apply(lambda x: str(x).strip().lower() == 'n / a')]

    # Handling of loans
    # if the column name contains "isin or other" then the column name becomes isin
    df.rename(columns={col: 'isin' if 'isin or other' in col.lower() else col for col in df.columns}, inplace=True)
    # if the second column has the word LIBOR, rate, FIGI, delete the rows
    if df.shape[1] > 1:  # If there are more than one columns
        df = df[~df.iloc[:, 1].apply(lambda x: any(word in str(x).lower() for word in ['libor', 'rate', 'figi']))]

    # if the column name is isin delete all the rows that have in that column alphanumeric codes smaller or equal to nine
    if 'isin' in df.columns:
        df = df[~df['isin'].apply(lambda x: len(str(x).strip()) <= 9)]

    # Remove all spaces before, after, and between strings for all columns except the first one
    df.iloc[:, 1:] = df.iloc[:, 1:].applymap(lambda x: str(x).strip())
    df.iloc[:, 1:] = df.iloc[:, 1:].replace('\s+', '', regex=True)

    # Check if the second column name is "unique identifier :" and all elements are alphanumeric codes of length 9
    if len(df.columns) > 1 and df.columns[1] == "unique identifier :" and all(df.iloc[:, 1].str.isalnum()) and all(df.iloc[:, 1].str.len() == 9):
        df.rename(columns={"unique identifier :": "cusip"}, inplace=True)


    output_file_path = os.path.join(output_directory, file)
    df.to_csv(output_file_path, index=False)

    print(f"Processed file: {file}")



