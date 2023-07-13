import os
import pandas as pd
import numpy as np

# Path to the directory with the CSV files
current_directory = os.getcwd()
data_directory = os.path.join(current_directory, 'data')
directory = os.path.join(data_directory, 'deliverable_obligations', 'final')
final_database_path = 'data/final_database/auctions_main_updated.csv'

# Load the final_database CSV
final_df = pd.read_csv(final_database_path)

# Get list of all CSV files in the directory
files = [f for f in os.listdir(directory) if f.endswith('.csv')]

# Create a new column in the dataframe for storing the number of rows
final_df['n_bonds'] = np.nan

exceptions = ['20160622_NSINO_CDS-Bucket_deliverable-obligations.csv', 
              '20160622_NSINO_CDS-Bucket-3_deliverable-obligations.csv', 
              '20160622_NSINO_CDS-Bucket-4_deliverable-obligations.csv',
              '20130605_BANKSA_CDS-SNR-or-SUB-Bucket-1_deliverable-obligations.csv',
              '20130605_BANKSA_CDS-SNR-or-SUB-Bucket-2_deliverable-obligations.csv',
              '20130605_BANKSA_CDS-SNR-or-SUB-Bucket-3_deliverable-obligations.csv',
              '20130605_BANKSA_CDS-SNR-or-SUB_deliverable-obligations.csv',
              '20130404_SNSBNK_CDS-SNR-or-SUB_deliverable-obligations.csv',
              '20130404_SNSBNK_CDS-SNR-or-SUB-Bucket-1_deliverable-obligations.csv']


# Iterate over all files
for file in files:
    # Strip '_deliverable-obligations.csv' from the file name to get the identifier
    identifier = file.replace('_deliverable-obligations.csv', '') 
    # Read CSV file
    try:
        df = pd.read_csv(os.path.join(directory, file))
    except pd.errors.EmptyDataError:
        print(f'Empty file: {file}')
        n_bonds = 0
        mask = final_df['identifier'].str.contains(identifier)
        final_df.loc[mask, 'n_bonds'] = n_bonds
        continue

    # Get the number of rows
    n_bonds = len(df)

    if file in exceptions:
        # Exact match for exceptions
        mask = final_df['identifier'] == identifier
    else:
        # Contains match for other files
        mask = final_df['identifier'].str.contains(identifier)

    if not any(mask):
        print(f'No identifier found for {identifier}')
    else:
        # Add num_rows to the last column for matching identifiers
        final_df.loc[mask, 'n_bonds'] = n_bonds

    # Add identifier from final_df to df
    df['identifier'] = final_df.loc[mask, 'identifier'].values[0]

    # Save the updated df back to its original file
    df.to_csv(os.path.join(directory, file), index=False)
# Save the updated final_database
final_df.to_csv(final_database_path, index=False)


# Specify the file path to the dataset
dataset_path = 'data/final_database/auctions_main_updated.csv'

# Read the dataset
data = pd.read_csv(dataset_path)

# Filter the rows where 'n_bonds' is NaN or 0 and the identifier does not contain 'LCDS' or 'Lien'
filtered_data = data[(data['n_bonds'].isna() | (data['n_bonds'] == 0)) ]

# Print the identifiers
# Print the identifiers and 'noi_usd' values
for index, row in filtered_data.iterrows():
    identifier = row['identifier']
    noi_usd = row['noi_usd']
    print(f"Identifier: {identifier}, NOI (USD): {noi_usd}")




