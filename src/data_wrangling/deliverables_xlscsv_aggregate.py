import os
import pandas as pd

# Define the directory containing the PDF files
current_directory = os.getcwd()
data_directory = os.path.join(current_directory, 'data')

# Define the directory containing the XLS files and CSV
raw_data_directory = os.path.join(data_directory, 'deliverable_obligations', 'raw')

# Define the output file path
output_file_path = os.path.join(data_directory, 'deliverable_obligations', 'intermediate', 'deliverable_obligations_xls.csv')

# Create an empty DataFrame to store the data
df = pd.DataFrame()

# Loop through each year from 2006 to 2023
for year in range(2006, 2024):
    year_folder_path = os.path.join(raw_data_directory, str(year))
    
    if os.path.isdir(year_folder_path):
        # Loop through each XLS file in the folder
        for filename in os.listdir(year_folder_path):
            if filename.endswith('.xls') or filename.endswith('.xlsx'):
                # File path
                file_path = os.path.join(year_folder_path, filename)

                # Read the XLS file
                xls_data = pd.read_excel(file_path)

                # Extract the column titles
                xls_columns = xls_data.columns.tolist()

                # Add the 'File Name' column
                xls_data.insert(0, 'File Name', filename)

                # Append DataFrame to the main DataFrame
                df = df.append(xls_data, ignore_index=True)


   # Process CSV files
    year_folder_path = os.path.join(raw_data_directory, str(year))
    
    if os.path.isdir(year_folder_path):
        # Loop through each CSV file in the folder
        for filename in os.listdir(year_folder_path):
            if filename.endswith('.csv'):
                # File path
                file_path = os.path.join(year_folder_path, filename)

                # Read the CSV file
                csv_data = pd.read_csv(file_path, delimiter=',', quoting=1)

                # Extract the column titles
                csv_columns = csv_data.columns.tolist()

                # Add the 'File Name' column
                csv_data.insert(0, 'File Name', filename)
                
                # Append DataFrame to the main DataFrame
                df = df.append(csv_data, ignore_index=True)

# Save the DataFrame to a CSV file
df.to_csv(output_file_path, index=False)
