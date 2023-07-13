import os
import pandas as pd
import wrds

def isin_to_cusip(isin):
    return isin[2:11]

def convert_seconds(time_in_seconds):
    hours = int(time_in_seconds // 3600)
    minutes = int((time_in_seconds % 3600) // 60)
    seconds = int(time_in_seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

'''
def convert_seconds(time_in_seconds):
    days = int(time_in_seconds // 86400)  # Add this line to compute the number of days
    hours = int((time_in_seconds % 86400) // 3600)  # Modify this line to compute hours within a day
    minutes = int((time_in_seconds % 3600) // 60)
    seconds = int(time_in_seconds % 60)
    return f"{days*24+hours:02d}:{minutes:02d}:{seconds:02d}"
'''

# Connect to WRDS
wrds_username = os.environ.get("WRDS_USERNAME")
wrds_password = os.environ.get("WRDS_PASSWORD")
db = wrds.Connection(wrds_username=wrds_username, wrds_password=wrds_password)

# Path to the directory with the CSV files
current_directory = os.getcwd()
data_directory = os.path.join(current_directory, 'data')
directory = os.path.join(data_directory, 'deliverable_obligations', 'final')

# Path to the directory to save the price data
price_data_directory = os.path.join(data_directory, 'deliverable_obligations_prices_144A') 
# Change this directory name to 'deliverable_obligations_prices_trace' or  'deliverable_obligations_prices_enhanced' or  'deliverable_obligations_prices_144A'

unique_identifiers = set()

for filename in os.listdir(directory):
    if filename.endswith('.csv'):
        file_path = os.path.join(directory, filename)
        #year = int(filename[:4])
        #if year > 2012:
        #   continue 

        # Check if the file is empty
        if os.stat(file_path).st_size == 0:
            continue

        # Read the CSV file
        try:
            df = pd.read_csv(file_path)
        except pd.errors.EmptyDataError:
            continue

        # Check if the DataFrame is empty
        if df.empty:
            continue

        # Check if 'cusip' column exists, if not create it
        if 'cusip' not in df.columns:
            df['cusip'] = df['isin'].apply(isin_to_cusip)

        # Iterate over all rows in the DataFrame
        for index, row in df.iterrows():
            # If 'cusip' is empty, convert 'isin' to 'cusip'
            if pd.isnull(row['cusip']):
                df.loc[index, 'cusip'] = isin_to_cusip(row['isin'])

            # Query TRACE Enhanced data for the CUSIP
            query = f"SELECT cusip_id, company_symbol, trd_exctn_dt, trd_exctn_tm, ascii_rptd_vol_tx, rptd_pr FROM trace.trace_btds144a WHERE cusip_id = '{row['cusip']}'" # Change this query to query TRACE data FROM trace.trace
            price_df = db.raw_sql(query) 
            #  entrd_vol_qt, rptd_pr FROM trace.trace_enhanced
            # ascii_rptd_vol_tx, rptd_pr FROM trace.trace
            # ascii_rptd_vol_tx, rptd_pr FROM trace.trace_btds144a
            # Add identifier to the set if the DataFrame is not empty
            if not price_df.empty:
                unique_identifiers.add(row['identifier'])

                # Apply convert_seconds function to trd_exctn_tm column
                # Comment out for TRACE data
                temp = price_df['trd_exctn_tm'].apply(convert_seconds)
                temp = pd.to_datetime(temp, format='%H:%M:%S')

                # Create trd_exctn_dttm column
                price_df['trd_exctn_dt'] = pd.to_datetime(price_df['trd_exctn_dt'], format='%Y-%m-%d')
                # Comment out for TRACE data
                price_df['trd_exctn_dttm'] = price_df['trd_exctn_dt'] + pd.to_timedelta(temp.dt.strftime('%H:%M:%S'))

                # Order rows by trd_exctn_dttm
                # Comment out for TRACE data
                price_df = price_df.sort_values(by='trd_exctn_dttm')

                # Here we drop duplicates across the specified columns
                price_df = price_df.drop_duplicates(subset=['trd_exctn_dttm', 'ascii_rptd_vol_tx', 'rptd_pr'])

                price_file_path = os.path.join(price_data_directory, f"{row['identifier']}_{row['cusip']}.csv")
                price_df.to_csv(price_file_path, index=False)

                # Save the price data to a CSV file
                price_file_path = os.path.join(price_data_directory, f"{row['identifier']}_{row['cusip']}.csv")
                price_df.to_csv(price_file_path, index=False)

print(f"The total number of unique identifiers with non-empty price_df is: {len(unique_identifiers)}")
print(unique_identifiers)
