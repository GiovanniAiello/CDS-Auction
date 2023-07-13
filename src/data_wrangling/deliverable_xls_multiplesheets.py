import os
import pandas as pd
import re
import numpy as np

# Define the directory containing the XLS files
current_directory = os.getcwd()
data_directory = os.path.join(current_directory, 'data')

# Define the directory containing the XLS files
xls_directory = os.path.join(data_directory, 'deliverable_obligations', 'raw')

# Define the directory to store the output CSV files
output_directory = os.path.join(data_directory, 'deliverable_obligations', 'intermediate')

# List of patterns to search for
patterns = [r'\bisin\b', r'\bcusip\b']

# Loop through each year from 2006 to 2023
for year in range(2006, 2024):
    year_folder_path = os.path.join(xls_directory, str(year))
    
    if os.path.isdir(year_folder_path):

        # Loop through each XLS file in the folder
        for filename in os.listdir(year_folder_path):
            if filename.endswith('.xls') or filename.endswith('.xlsx') or filename.endswith('.XLS'):
                
                # Skip the specified file
                if filename == "20120202_NRAMC_CDS_deliverable-obligations.xls":
                    continue

                # File path
                file_path = os.path.join(year_folder_path, filename)

                # Load the Excel file
                xls = pd.ExcelFile(file_path)

                # Check if any sheet name contains one of the keywords
                for sheet_name in xls.sheet_names:
                    if any(keyword in sheet_name for keyword in ["Sen", "Senior", "Sub", "Subordinate"]):
                        print(f"Processing file: {filename}, Sheet: {sheet_name}")
                        # Read the data for the current sheet
                        data = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
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

                            # Replace ", " with "\n" to unify the separators
                            output_data['isin'] = output_data['isin'].str.replace(',', '\n')

                            # Replace " and " with "\n" to unify the separators
                            output_data['isin'] = output_data['isin'].str.replace(' and ', '\n')

                            # Replace " / " with "\n" to unify the separators
                            output_data['isin'] = output_data['isin'].str.replace(' / ', '\n')

                            # Replace " and " with "\n" to unify the separators
                            output_data['isin'] = output_data['isin'].str.replace(';', '\n')

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
                            output_data = output_data[((output_data['isin'].str.len() >= 5) & (output_data['isin'].str.len() <= 30)) | 
                                                      ((output_data['cusip'].str.len() >= 5) & (output_data['cusip'].str.len() <= 30))]

                        elif 'isin' in output_data.columns:  # If only 'isin' exists
                            output_data = output_data[(output_data['isin'].str.len() >= 5) & (output_data['isin'].str.len() <= 30)]

                        elif 'cusip' in output_data.columns:  # If only 'cusip' exists
                            output_data = output_data

                        # List of words to filter out
                        filter_words = ['notes', 'loan', 'security', 'cusip', 'numbers', 'Auction Settlement', 'doubt']

                        # Apply the filter
                        if 'isin' in output_data.columns:
                            for word in filter_words:
                                output_data = output_data[~output_data['isin'].str.contains(word, case=False, na=False)]
                        if 'cusip' in output_data.columns:
                            for word in filter_words:
                                output_data = output_data[~output_data['cusip'].str.contains(word, case=False, na=False)]
                        
                       
                        keyword = next((keyword for keyword in ["Sen", "Senior", "Sub", "Subordinate"] if keyword.lower() in sheet_name.lower()), None)
                        if keyword:
                            new_filename = f"{os.path.splitext(filename)[0].replace('_deliverable-obligations', '-')}{keyword}_deliverable-obligations.csv"
                        else:
                            new_filename = f"{os.path.splitext(filename)[0].replace('_deliverable-obligations', '-')}{sheet_name.lower()}_deliverable-obligations.csv"
                         # Define the output file path
                        output_file_path = os.path.join(output_directory, new_filename)

                        # Save the DataFrame to a CSV file
                        output_data.to_csv(output_file_path, index=False)



# List of files to process
file_list = ['20110728_BKIR_CDS-Sen_deliverable-obligations.csv', '20110728_BKIR_CDS-Sub_deliverable-obligations.csv']

for filename in file_list:
    # Define the full file path
    file_path = os.path.join(output_directory, filename)
    
    # Load the DataFrame from the CSV file
    output_data = pd.read_csv(file_path)
    
    # Add a new column 'Regulation' with NaN values
    output_data['Regulation'] = np.nan

    # Loop over each row in the DataFrame for 'Rule 144A'
    for i, row in output_data.iterrows():
        # If the 'isin' value contains the string 'Rule 144A'
        if 'Rule 144A' in row['isin']:
            # Split the 'isin' value into components
            components = row['isin'].split('(Rule 144A)')
            # The first component is always the isin
            isin = components[0].strip()
            # The second component is the regulation
            regulation = 'Rule 144A' if len(components) > 1 else np.nan
            # Update the 'isin' and 'Regulation' values
            output_data.loc[i, 'isin'] = isin
            output_data.loc[i, 'Regulation'] = regulation

    # Loop over each row in the DataFrame for 'Reg S'
    for i, row in output_data.iterrows():
        # If the 'isin' value contains the string 'Reg S'
        if 'Reg S' in row['isin']:
            # Split the 'isin' value into components
            components = row['isin'].split('(Reg S)')
            # The first component is always the isin
            isin = components[0].strip()
            # The second component is the regulation
            regulation = 'Reg S' if len(components) > 1 else np.nan
            # Update the 'isin' and 'Regulation' values
            output_data.loc[i, 'isin'] = isin
            output_data.loc[i, 'Regulation'] = regulation

    # Remove the 'Regulation' column if it only contains NaN values
    if output_data['Regulation'].isna().all():
        output_data.drop('Regulation', axis=1, inplace=True)

    # Save the modified DataFrame back to the same CSV file
    output_data.to_csv(file_path, index=False)

