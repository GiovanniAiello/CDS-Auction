import os
import pandas as pd
import numpy as np

# Path to the directory with the CSV files
current_directory = os.getcwd()
data_directory = os.path.join(current_directory, 'data')
directory = os.path.join(data_directory, 'deliverable_obligations', 'intermediate')
final_database_path = 'data/final_database/auctions_main_updated.csv'

# Load the final_database CSV
final_df = pd.read_csv(final_database_path)

# Get list of all CSV files in the directory
files = [f for f in os.listdir(directory) if f.endswith('.csv')]

# Create a new column in the dataframe for storing the number of rows
final_df['num_rows'] = np.nan

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
    df = pd.read_csv(os.path.join(directory, file))

    # Get the number of rows
    num_rows = len(df)

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
        final_df.loc[mask, 'num_rows'] = num_rows

# Save the updated final_database
final_df.to_csv(final_database_path, index=False)

