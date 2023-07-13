import os
import pandas as pd
import re


# Define the directory containing the PDF files
current_directory = os.getcwd()
data_directory = os.path.join(current_directory, 'data')

# Define the directory containing the XLS files and CSV
raw_data_directory = os.path.join(data_directory, 'deliverable_obligations', 'processed_pdf_nanonets')

# Define the directory to store the output CSV files
output_directory = os.path.join(data_directory, 'deliverable_obligations', 'intermediate')

# List of patterns to search for
patterns = [r'\bcusip\b', r'\bisin\b', r'\bunique identifier\b']

# Loop through each CSV file in the folder
for filename in os.listdir(raw_data_directory):
    if filename.endswith('.csv'):
        # File path
        file_path = os.path.join(raw_data_directory, filename)
        print(f"Processing file: {file_path}")  # Print statement for debugging

        # Read the CSV file without specifying a header
        data = pd.read_csv(file_path, header=None)

        # Add the 'file_name' column with the filename (without path and extension)
        data.insert(0, 'file_name', os.path.splitext(filename)[0])
        
        # Convert first column to 'file_name'
        data.rename(columns={data.columns[0]: 'file_name'}, inplace=True)

        # Initialize header_found flag
        header_found = False

        # Loop over the rows
        for i, row in data.iterrows():
            row = row.astype(str).str.lower()

            # If any pattern is in row.values
            if any(re.search(pattern, val) for val in row.values for pattern in patterns):
                # Rename columns and drop previous rows
                data.columns = data.iloc[i]
                data = data.iloc[i + 1:]
                print(f"Header row found at index {i}")  # Print statement for debugging
                header_found = True
                break

        # If no header row is found, check the entire data for potential CUSIPs or ISINs
        if not header_found:
            data = data.applymap(str)
            # Search for potential CUSIPs or ISINs
            potential_cusip = data[data.apply(lambda row: row.astype(str).str.contains(r'\b[A-Za-z0-9]{9}\b').any(), axis=1)]
            potential_isin = data[data.apply(lambda row: row.astype(str).str.contains(r'\b[A-Za-z0-9]{12}\b').any(), axis=1)]

            # If any CUSIPs or ISINs found, add them as new columns
            if not potential_cusip.empty:
                potential_cusip['CUSIP'] = potential_cusip.apply(lambda row: next((val for val in row if re.match(r'\b[A-Za-z0-9]{9}\b', val)), None), axis=1)
                data = pd.concat([data, potential_cusip['CUSIP']], axis=1)
                header_found = True  # Update the flag
            if not potential_isin.empty:
                potential_isin['ISIN'] = potential_isin.apply(lambda row: next((val for val in row if re.match(r'\b[A-Za-z0-9]{12}\b', val)), None), axis=1)
                data = pd.concat([data, potential_isin['ISIN']], axis=1)
                header_found = True  # Update the flag

        # If no CUSIPs or ISINs found, print message and continue with next file
        if not header_found:
            print("NO Cusip or ISIN found")
            continue

        # Convert column names to lowercase for case-insensitive matching
        data.columns = data.columns.astype(str).str.lower()

        # Find the 'isin', 'cusip', 'isin/cusip', or 'unique identifier' columns, if they exist
        isin_cols = [col for col in data.columns if re.search(r'\bisin\b', str(col), re.I) and not re.search(r'\bcusip\b', str(col), re.I)]
        cusip_cols = [col for col in data.columns if re.search(r'\bcusip\b', str(col), re.I) and not re.search(r'\bisin\b', str(col), re.I)]
        isin_cusip_col = next((str(col) for col in data.columns if re.search(r'\bcusip\b', str(col), re.I) and re.search(r'\bisin\b', str(col), re.I)), None)
        unique_id_col = next((str(col) for col in data.columns if re.search(r'\bunique identifier\b', str(col), re.I)), None)

        # Add the 'file_name' column
        data.rename(columns={data.columns[0]: 'file_name'}, inplace=True)

        # Prepare the columns to be output
        output_columns = ['file_name']
        output_columns.extend(isin_cols)
        output_columns.extend(cusip_cols)
        if isin_cusip_col:
            output_columns.append(isin_cusip_col)
        if unique_id_col:
            output_columns.append(unique_id_col)
            
        output_data = data[output_columns].copy()

        # Remove "-0-pdf" and "-Protocol" from 'file_name'
        output_data['file_name'] = output_data['file_name'].str.replace('-0-pdf', '').str.replace('-Protocol', '')

        # Remove duplicate columns
        output_data = output_data.loc[:,~output_data.columns.duplicated()]

        # Modify column names as requested
        output_data.columns = output_data.columns.str.replace(r'[\r\n\s:]*unique identifier[\r\n\s:]*\( isin \)[\r\n\s:]*', 'isin', regex=True)
        output_data.columns = output_data.columns.str.replace(r'isin[\s]*no\.', 'isin', regex=True)


        # Modify column names as requested
        output_data.columns = output_data.columns.str.replace(r'[\r\n\s:]*unique identifier[\r\n\s:]*\( cusip \)[\r\n\s:]*', 'cusip', regex=True)



        # Define the output file path
        output_file_path = os.path.join(output_directory, f"{os.path.splitext(output_data['file_name'].iloc[0])[0]}.csv")
        print(f"Saving file: {output_file_path}")  # Print statement for debugging

        # Save the DataFrame to a CSV file
        output_data.to_csv(output_file_path, index=False)

# Define the specific file
file = "20090114_ecuado_CDS_deliverable-obligations-0-pdf.csv"

# Read the CSV file
df = pd.read_csv(os.path.join(raw_data_directory, file), header=None)

# Construct column names from second and third row, and skip the first and third row
colnames = [f"{str(col1)}_{str(col2)}" for col1, col2 in zip(df.iloc[1], df.iloc[2])]
df.columns = ['file_name'] + colnames[1:]
df = df.drop([0, 1, 2])

# Only select necessary columns
df = df[['file_name', colnames[4], colnames[5], colnames[6], colnames[7]]]

# Replace file name
df['file_name'] = df['file_name'].str.replace('.pdf', '', regex=False)

# Write to a new CSV file
output_file = os.path.join(output_directory, file.replace('-0-pdf.csv', '.csv'))
df.to_csv(output_file, index=False)

print("Cleaning process completed.")
