
import os
import pandas as pd
import re

# Define the directory containing the PDF files
current_directory = os.getcwd()
data_directory = os.path.join(current_directory, 'data')

# Define the directory containing the XLS files and CSV
raw_data_directory = os.path.join(data_directory, 'deliverable_obligations', 'raw')

# Define the directory to store the output CSV files
output_directory = os.path.join(data_directory, 'deliverable_obligations', 'intermediate')

# List of files to skip
files_to_skip = [
    "20090730_brabin_deliverable-obligations.xls",
    "20101209_ANGBKL_CDS_deliverable-obligations.xls",
    "20110728_BKIR_CDS_deliverable-obligations.XLS",
    "20110729_IPBS_CDS_deliverable-obligations.XLS",
    "20110202_ANGBKL2_CDS_deliverable-obligations.xls",
    "20110630_AIB_CDS_deliverable-obligations.XLS",
    "20111005_IPBS2_CDS_deliverable-obligations.XLS",
    "20081006_famefrmc_deliverable-obligations.xls",
    "20081106_kaupth_deliverable-obligations.xls",
    "20081105_glitni_deliverable-obligations.xls",
    "20081104_landsb_deliverable-obligations.xls",
]


# List of patterns to search for
patterns = [r'\bisin\b', r'\bcusip\b']

# Loop through each year from 2006 to 2023
for year in range(2006, 2024):
    year_folder_path = os.path.join(raw_data_directory, str(year))
    
    if os.path.isdir(year_folder_path):
        print(f"Processing directory: {year_folder_path}")

        # Loop through each XLS or CSV file in the folder
        for filename in os.listdir(year_folder_path):
            if filename in files_to_skip:
                print(f"Skipping file: {filename}")
                continue
            if filename.endswith('.xls') or filename.endswith('.xlsx') or filename.endswith('.XLS') or filename.endswith('.csv'):
                print(f"Processing file: {filename}")
                
                # File path
                file_path = os.path.join(year_folder_path, filename)

                # Read the XLS or CSV file without specifying a header
                if filename.endswith('.xls') or filename.endswith('.xlsx') or filename.endswith('.XLS'):
                    data = pd.read_excel(file_path, header=None)
                else:
                    data = pd.read_csv(file_path, header=None)

                # Loop over the rows
                for i, row in data.iterrows():
                    row = row.astype(str).str.lower()

                    # If any pattern is in row.values
                    if any(re.search(pattern, val) for val in row.values for pattern in patterns):
                        # Rename columns and drop previous rows
                        data.columns = data.iloc[i]
                        data = data.iloc[i + 1:]
                        print(f"Found header row at index {i}")
                        break

                # Convert column names to lowercase for case-insensitive matching
                data.columns = data.columns.str.lower()

                # Find the 'isin' and 'cusip' columns, if they exist
                isin_col = next((str(col) for col in data.columns if re.search(r'\bisin\b', str(col), re.I)), None)
                cusip_col = next((str(col) for col in data.columns if re.search(r'\bcusip\b', str(col), re.I)), None)

                # If neither 'isin' or 'cusip' is found, continue with the next file
                if isin_col is None and cusip_col is None:
                    print(f"No 'isin' or 'cusip' in file: {filename}. Skipping file.")
                    continue

                # Add the 'File Name' column
                data.insert(0, 'File Name', filename)

                # If both 'isin' and 'cusip' are found
                if isin_col and cusip_col:
                    print(f"Both 'isin' and 'cusip' found in file: {filename}")
                    output_data = data[['File Name', isin_col, cusip_col]].copy()  # Create a copy to avoid SettingWithCopyWarning
                    output_data.columns = ['final_name', 'isin', 'cusip']
                elif isin_col:  # If only 'isin' is found
                    print(f"Only 'isin' found in file: {filename}")
                    output_data = data[['File Name', isin_col]].copy()
                    output_data.columns = ['final_name', 'isin']
                elif cusip_col:  # If only 'cusip' is found
                    print(f"Only 'cusip' found in file: {filename}")
                    output_data = data[['File Name', cusip_col]].copy()
                    output_data.columns = ['final_name', 'cusip']

                # If 'isin' exists, split rows containing multiple ISINs
                if 'isin' in output_data.columns:
                    print(f"Processing 'isin' values in file: {filename}")

                    # Ensure that the 'isin' column is of type string
                    output_data['isin'] = output_data['isin'].astype(str)
                    
                    # Define a regex pattern for "(see footnotes ...)"
                    pattern = r'\(see footnotes.*?\)'

                    # Loop through all the columns that can potentially contain the 'see footnotes' text
                    for col in ['isin']:
                        if col in output_data.columns:
                            output_data[col] = output_data[col].str.replace(pattern, '', regex=True)


                    # Replace ", " with "\n" to unify the separators
                    output_data['isin'] = output_data['isin'].str.replace(',', '\n')

                    # Replace " and " with "\n" to unify the separators
                    output_data['isin'] = output_data['isin'].str.replace(' and ', '\n')

                    # Replace "   " with "\n" to unify the separators
                    output_data['isin'] = output_data['isin'].str.replace('   ', '\n')
                    # Replace " / " with "\n" to unify the separators
                    output_data['isin'] = output_data['isin'].str.replace(' / ', '\n')
                    # Split the ISINs and explode into separate rows
                    output_data['isin'] = output_data['isin'].str.split('\n')
                    output_data = output_data.explode('isin')

                # Strip leading and trailing spaces from the columns
                output_data = output_data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

                # If 'isin' and 'cusip' columns exist, drop rows where both 'isin' and 'cusip' are empty
                if 'isin' in output_data.columns and 'cusip' in output_data.columns:
                    output_data = output_data.dropna(subset=['isin', 'cusip'], how='all')
                elif 'isin' in output_data.columns:  # If only 'isin' exists, drop rows where 'isin' is empty
                    output_data = output_data.dropna(subset=['isin'])
                elif 'cusip' in output_data.columns:  # If only 'cusip' exists, drop rows where 'cusip' is empty
                    output_data = output_data.dropna(subset=['cusip'])

                # Filter out the rows where 'isin' or 'cusip' is empty, less than 5 characters or more than 30 characters
                if 'isin' in output_data.columns and 'cusip' in output_data.columns:
                    output_data = output_data[((output_data['isin'].str.len() >= 5) ) | 
                                              ((output_data['cusip'].str.len() >= 5) )]

                elif 'isin' in output_data.columns:  # If only 'isin' exists
                    output_data = output_data[(output_data['isin'].str.len() >= 5)]

                elif 'cusip' in output_data.columns:  # If only 'cusip' exists
                    output_data = output_data

                # List of words to filter out
                filter_words = ['loan', 'security', 'cusip', 'numbers', 'NOTES:', 'Credit', 'Lehman Brothers', 'Accreted', 'Weinstein']

                # Apply the filter
                if 'isin' in output_data.columns:
                    for word in filter_words:
                        output_data = output_data[~output_data['isin'].str.contains(word, case=False, na=False)]
                if 'cusip' in output_data.columns:
                    for word in filter_words:
                        output_data = output_data[~output_data['cusip'].str.contains(word, case=False, na=False)]
                # Define the output file path
                output_file_path = os.path.join(output_directory, f"{os.path.splitext(filename)[0]}.csv")

                print(f"Saving file: {output_file_path}")

                # Save the DataFrame to a CSV file
                output_data.to_csv(output_file_path, index=False)
