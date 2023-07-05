import os
import pandas as pd
import csv


def parse_and_split_regulation(x):
    if "\n" in x:  # multiple isin codes in a cell
        lines = x.split("\n")
        regulation = [lines[i].strip(" ()") for i in range(1, len(lines), 2)]
        code = [lines[i-1] for i in range(1, len(lines), 2)]
    elif " (" in x:  # single isin code with regulation in a cell
        code, reg = x.split(" (")
        code = [code]
        regulation = [reg.strip(" )")]
    else:  # single isin code without regulation
        code = [x]
        regulation = [None]
    return pd.Series([code, regulation])

def split_newlines(x):
    if "\n" in x:  # multiple isin codes in a cell
        codes = x.split("\n")
    else:  # single isin code in a cell
        codes = [x]
    return codes

def split_slash(x):
    if '/' in x:  # Values separated by "/"
        codes = x.split('/')
    else:
        codes = [x]
    return codes

current_directory = os.getcwd()
data_directory = os.path.join(current_directory, 'data')
output_directory = os.path.join(data_directory, 'deliverable_obligations', 'intermediate')
csv_files = [f for f in os.listdir(output_directory) if f.endswith('.csv')]

for file in csv_files:
    df = pd.read_csv(os.path.join(output_directory, file))

    # Check for 'unique identifier (cusip) :'
    if df.columns[1] == 'unique\nidentifier\n( cusip ) :':
        df.columns.values[1] = 'cusip'
    # Check for 'unique identifier :' and 'CUSIP :' in cell values
    elif df.columns[1] == 'unique identifier :' and df.iloc[0,1].startswith('CUSIP :'):
        df.columns.values[1] = 'cusip'
        df['cusip'] = df['cusip'].str.replace('CUSIP :', '').str.strip()


    column = 'isin' if 'isin' in df.columns else 'cusip' if 'cusip' in df.columns else None
    if column is None:
        print(f"File {file} doesn't have 'isin' or 'cusip' column.")
        continue

    df[column] = df[column].astype(str)
    df = df[df[column] != '-']
    df = df[df[column] != 'n / a']    
    df = df[df[column] != 'N / A'] 

    if not df[column].str.contains("144A|Reg S|Regulation S").any():
        df[column] = df[column].apply(split_newlines)
        df = df.explode(column).reset_index(drop=True)
        df[column] = df[column].apply(split_slash)
        df = df.explode(column).reset_index(drop=True)

    if "DIAMSPO" in file:  # adjust this as per your needs
        df[['isin', 'Regulation']] = df[column].apply(parse_and_split_regulation)
        df = df.explode('isin').explode('Regulation')
    elif df[column].str.contains("144A|Reg S|Regulation S").any():
        df[['isin', 'Regulation']] = df[column].apply(parse_and_split_regulation)
        df = df.explode('isin').explode('Regulation')


    df.to_csv(os.path.join(output_directory, file), index=False)


# Set the path and file names

file_names = ['20191030_THCP_CDS_deliverable-obligations.csv', '20190807_GALAPHO_CDS_deliverable-obligations.csv', '20190605_NEWLOOAC_CDS_deliverable-obligations.csv', '20181129_ASTL_CDS_deliverable-obligations.csv']

# Perform the transformation for each file
for file_name in file_names:
    file_path = os.path.join(output_directory, file_name)

    # Read the original file
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        transformed_data = []
        isin_regulation = set()  # Track unique ISIN and Regulation combinations

        # Process each row and create the transformed data
        for row in reader:
            file_name = row[0]
            isin_regulation_1 = row[1].split(': ')
            isin = isin_regulation_1[-1].strip()
            regulation_1 = isin_regulation_1[0].strip()

            # Additional transformation for ASTL file
            if "ASTL" in file_name:
                # Skip the row if ISIN and Regulation are the same and already encountered before
                if isin == regulation_1:
                    if (isin, regulation_1) in isin_regulation:
                        continue
                    else:
                        transformed_row_1 = [file_name, isin, '']
                        isin_regulation.add((isin, regulation_1))
                else:
                    transformed_row_1 = [file_name, isin, regulation_1]

                transformed_data.append(transformed_row_1)

            isin_regulation_2 = row[2].split(': ')
            isin_2 = isin_regulation_2[-1].strip()
            regulation_2 = isin_regulation_2[0].strip()

            # Additional transformation for ASTL file
            if "ASTL" in file_name:
                # Skip the row if ISIN and Regulation are the same and already encountered before
                if isin_2 == regulation_2:
                    if (isin_2, regulation_2) in isin_regulation:
                        continue
                    else:
                        transformed_row_2 = [file_name, isin_2, '']
                        isin_regulation.add((isin_2, regulation_2))
                else:
                    transformed_row_2 = [file_name, isin_2, regulation_2]

                transformed_data.append(transformed_row_2)

            # Additional transformation for non-ASTL files
            if "ASTL" not in file_name:
                transformed_data.append([file_name, isin_2, regulation_2])

    # Write the transformed data back to the file
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["file_name", "isin", "Regulation"])  # Write the header row
        writer.writerows(transformed_data)

print("Transformation complete. Output files created.")


# Set the path and file name
file = '20171213_PDV_CDS_deliverable-obligations.csv'
file_path = os.path.join(output_directory, file)

# Read the original file
df = pd.read_csv(file_path)

# Create a new dataframe to store the transformed data
transformed_data = pd.DataFrame(columns=['file_name', 'isin', 'Regulation'])

# Iterate over each row in the original dataframe
for index, row in df.iterrows():
    file_name = row['file_name']
    isin_regulation_s = row['isin ( regulation s )']
    isin_rule_144a = row['isin ( rule 144a )']

    # Append a row with isin and regulation s to the transformed dataframe
    if pd.notnull(isin_regulation_s):
        transformed_data = transformed_data.append({'file_name': file_name, 'isin': isin_regulation_s, 'Regulation': 'regulation s'}, ignore_index=True)

    # Append a row with isin and rule 144A to the transformed dataframe
    if pd.notnull(isin_rule_144a):
        transformed_data = transformed_data.append({'file_name': file_name, 'isin': isin_rule_144a, 'Regulation': 'rule 144A'}, ignore_index=True)

# Write the transformed data back to the file
output_file_path = os.path.join(output_directory, file)
transformed_data.to_csv(output_file_path, index=False)

print("Transformation complete. Output file created:", file_name)


file_names = ['20131009_CODSA-Fin_CDS_deliverable-obligations.csv', '20160824_GRUPOIS_CDS_deliverable-obligations.csv', '20170914_NSINO_CDS_deliverable-obligations.csv', '20160622_NSINO_CDS_deliverable-obligations.csv']

for file_name in file_names:
    file_path = os.path.join(output_directory, file_name)

    # Read the original file
    df = pd.read_csv(file_path)

    # Remove parentheses and whitespace from "isin" and "Regulation" columns
    df['isin'] = df['isin'].str.replace(r'\(|\)', '').str.strip()
    df['Regulation'] = df['Regulation'].str.replace(r'\(|\)', '').str.strip()

    # Create two separate dataframes for isin and regulation
    isin_df = df[['file_name', 'isin']]
    regulation_df = df[['file_name', 'Regulation']]

    # Rename the columns in regulation_df to 'isin'
    regulation_df.columns = ['file_name', 'isin']

    # Concatenate the two dataframes vertically
    combined_df = pd.concat([isin_df, regulation_df], ignore_index=True)

    # Split the 'isin' column by double space into 'isin' and 'Regulation' columns
    combined_df[['isin', 'Regulation']] = combined_df['isin'].str.split('  ', n=1, expand=True)

    # Write the transformed data back to the file
    output_file_path = os.path.join(output_directory, file_name)
    combined_df.to_csv(output_file_path, index=False)

    print("Transformation complete. Output file created:", file_name)


# Set the path and file name
file_name = '20120509_SIFO_CDS_deliverable-obligations.csv'
file_path = os.path.join(output_directory, file_name)

# Read the original file
df = pd.read_csv(file_path)

# Remove parentheses and double quotes from "isin" and "Regulation" columns
df['isin'] = df['isin'].str.replace(r'["()]', '').str.strip()
df['Regulation'] = df['Regulation'].str.replace(r'["()]', '').str.strip()

# Drop duplicate isin values while keeping the first occurrence
df = df.drop_duplicates(subset='isin', keep='first')

# Reset the index
df = df.reset_index(drop=True)

# Create a new column "Regulation_cleaned" to alternate between "Rule 144A" and "Regulation S"
df['Regulation'] = 'Rule 144A'
df.loc[df.index % 2 == 1, 'Regulation'] = 'Regulation S'

# Select the final columns
transformed_data = df[['file_name', 'isin', 'Regulation']]

# Write the transformed data back to the file
output_file_path = os.path.join(output_directory, file_name)
transformed_data.to_csv(output_file_path, index=False)

print("Transformation complete. Output file created:", file_name)


# Set the path and file name
file = '20160504_PLCOAL_CDS_deliverable-obligations.csv'
file_path = os.path.join(output_directory, file)

# Read the original file
df = pd.read_csv(file_path)

# Create a new DataFrame to store cleaned data
cleaned_data = pd.DataFrame(columns=['file_name', 'cusip / isin'])

# Split the alphanumeric codes into separate rows
for index, row in df.iterrows():
    file_name = row['file_name']
    codes = row['cusip / isin'].split('\n')
    
    # Remove any leading/trailing whitespaces from the codes
    codes = [code.strip() for code in codes]
    
    # Add each code as a new row to the cleaned data DataFrame
    for code in codes:
        cleaned_data = cleaned_data.append({'file_name': file_name, 'cusip / isin': code}, ignore_index=True)

# Write the cleaned data to a new file
output_file_path = os.path.join(output_directory, file)
cleaned_data.to_csv(output_file_path, index=False)

print("Transformation complete. Output file created:", file_name)


# Read the original file
file_name = '20160114_ABNG_CDS_deliverable-obligations.csv'
file_path = os.path.join(output_directory, file_name)
df = pd.read_csv(file_path)

# Split the data into three dataframes based on specific conditions
# Replace missing values with empty strings
df['Regulation'] = df['Regulation'].fillna('')
df_notes = df[df['isin'].str.contains('Notes')]
df_reg_s = df[df['isin'].str.contains('Reg S')]
df_144A = df[df['Regulation'].str.contains('144A')]
df_two_columns = df[df.iloc[:, 2].isna() | df.iloc[:, 2].str.strip().eq('')]

# Reset index for df_two_columns
df_two_columns.reset_index(drop=True, inplace=True)

# Invert column names and positions for 'df_notes'
df_notes = df_notes.rename(columns={'Regulation': 'isin', 'isin': 'Regulation'})
df_notes = df_notes[['file_name', 'isin', 'Regulation']]

# Split 'df_reg_s' at the parenthesis, strip spaces and parenthesis, and pile the alphanumeric codes
df_reg_s[['isin', 'Regulation']] = df_reg_s['isin'].str.split(r'[\(\)]', n=1, expand=True)
df_reg_s['isin'] = df_reg_s['isin'].str.strip()
df_reg_s['Regulation'] = df_reg_s['Regulation'].str.strip(')').str.strip()

# Create 'file_name' column for 'df_reg_s'
df_reg_s['file_name'] = df_reg_s['file_name'].fillna(file_name)
df_reg_s = df_reg_s[['file_name', 'isin', 'Regulation']]

df_144A[['isin', 'Regulation']] = df_144A['Regulation'].str.split(r'[\(\)]', expand=True)
df_144A = df_144A[['file_name', 'isin', 'Regulation']]
df_144A.index += 1  # Add +1 to the index

# Merge df_reg_s and df_144A using the index
df_reg = pd.concat([df_reg_s, df_144A])
df_reg = df_reg.sort_index()
# Concatenate df_notes, df_reg, and df_two_columns
df_final = pd.concat([df_notes, df_reg, df_two_columns], ignore_index=True)


df_final.to_csv(file_path, index=False)

# Print the output file path
print("Output file saved:", output_file_path)

import pandas as pd

# Read the file
file = '20090114_ecuado_CDS_deliverable-obligations.csv'
file_path = os.path.join(output_directory, file)
df = pd.read_csv(file_path)

# Create the first dataframe with columns 1, 2, and 4
df_first = df.iloc[:, [0, 1, 3]]
df_first.columns = ['file_name', 'isin', 'cusip']

# Create the second dataframe with columns 1, 3, and 5
df_second = df.iloc[:, [0, 2, 4]]
df_second.columns = ['file_name', 'isin', 'cusip']

# Concatenate the two dataframes
df_final = pd.concat([df_first, df_second])

# Save the final dataframe to the same CSV file
df_final.to_csv(file_path, index=False)

print("Final dataframe saved to:", file)

file_names = ['20200423_LEBAN_CDS_delivarable-obligations.csv', '20171212_VENZ_CDS_deliverable-obligations.csv']

for file_name in file_names:
    file_path = os.path.join(output_directory, file_name)

    # Read the file
    df = pd.read_csv(file_path)

    # Remove spaces in the second column based on position
    df.iloc[:, 1] = df.iloc[:, 1].str.replace(' ', '')

    # Write the modified data back to the file
    df.to_csv(file_path, index=False)

    print("Spaces removed in the second column for file:", file_path)


for file in csv_files:
    file_path = os.path.join(output_directory, file)

    # Read the original file
    df = pd.read_csv(file_path)

    # Clean the data
    df.columns = df.columns.str.strip().str.replace(r'\*|\**', '')
    df = df.dropna(subset=df.columns[0:], how='all')
    df = df[df.iloc[:, 0].str.len() > 0]
    df.iloc[:, 1:] = df.iloc[:, 1:].astype(str).apply(lambda x: x.str.replace(',', '').str.strip())
    df.iloc[:, 1:] = df.iloc[:, 1:].astype(str).apply(lambda x: x.str.replace('\xb9', '').str.strip())
    df.iloc[:, 1:] = df.iloc[:, 1:].astype(str).apply(lambda x: x.str.replace('\xb2', '').str.strip())
    df = df[df.iloc[:, 1].astype(str).str.len() > 4]
    df = df[df.iloc[:, 1].astype(str).str.len() <= 30]
    df.iloc[:, 1:] = df.iloc[:, 1:].astype(str).apply(lambda x: x.str.replace('*', '').str.strip())
    df = df[~(df.iloc[:, 1].str.strip().str.upper() == 'CUSIP')]
    df = df[~(df.iloc[:, 1].str.strip().str.title().isin(['Spread', 'Final Maturity']))]


    # Rename the first column dynamically
    df = df.rename(columns={df.columns[0]: 'file_name'})

    # Check second column for ISIN or CUSIP
    if df.iloc[:, 1].str.match(r'^[A-Z]{2}[A-Z0-9]{9}\d?$').all():
        df = df.rename(columns={df.columns[1]: 'isin'})
    elif df.iloc[:, 1].str.match(r'^[A-Z0-9]{9}$').all():
        df = df.rename(columns={df.columns[1]: 'cusip'})
    
    # Check third column for ISIN or CUSIP
    if len(df.columns) > 2:
        if df.iloc[:, 2].str.match(r'^[A-Z]{2}[A-Z0-9]{9}\d?$').all():
            df = df.rename(columns={df.columns[2]: 'isin'})
        elif df.iloc[:, 2].str.match(r'^[A-Z0-9]{9}$').all():
            df = df.rename(columns={df.columns[2]: 'cusip'})


    # Write the cleaned data to a new CSV file
    output_file_path = os.path.join(output_directory,  file)
    df.to_csv(output_file_path, index=False)

    print("Cleaning complete. Output file created:", output_file_path)




file_name = '20130404_SNSBNK_CDS-SNR-or-SUB_deliverable-obligations.csv'
file_path = os.path.join(output_directory, file_name)

# Read the file
df = pd.read_csv(file_path)

# Filter rows with valid ISIN codes
invalid_isin = df[~df['isin'].str.match(r'^[A-Z]{2}[A-Z0-9]{9}\d{1}$')]
valid_isin = df[df['isin'].str.match(r'^[A-Z]{2}[A-Z0-9]{9}\d{1}$')]


# Write the cleaned data back to the file
valid_isin.to_csv(file_path, index=False)

print("Cleaning complete. Output file created:", file_path)



# Set the path and file name
file = '20160504_PLCOAL_CDS_deliverable-obligations.csv'
file_path = os.path.join(output_directory, file)

# Read the original file
df = pd.read_csv(file_path)

# Initialize empty lists for new columns
cusip = []
isin = []

# Loop through the 'cusip / isin' column
for index, row in df.iterrows():
    if len(row['cusip / isin']) == 9:  # CUSIPs are typically 9 characters
        cusip.append(row['cusip / isin'])
        isin.append(None)
    else:  # ISINs are typically 12 characters
        cusip.append(None)
        isin.append(row['cusip / isin'])

# Add the new cusip and isin columns to the DataFrame
df['cusip'] = cusip
df['isin'] = isin

# Drop the original 'cusip / isin' column
df = df.drop(columns=['cusip / isin'])

# Now your dataframe has separated columns for 'cusip' and 'isin'. We now fill in the missing 'cusip' and 'isin' values
df['cusip'] = df['cusip'].fillna(method='ffill')
df['isin'] = df['isin'].fillna(method='bfill')


# Drop the duplicated rows
df = df.drop_duplicates()

# Save it to the same file
df.to_csv(file_path, index=False)



# Set the output directory path and the list of files
files = ['20190724_WFT_CDS_deliverable-obligations.csv', '20111215_AMR_CDS_deliverable-obligations.csv']

# Loop over the files
for file in files:
    file_path = os.path.join(output_directory, file)

    # Read the file
    df = pd.read_csv(file_path)

    # Identify the name of the column
    if 'cusip / isin' in df.columns:
        col_name = 'cusip / isin'
    elif 'isin / cusip' in df.columns:
        col_name = 'isin / cusip'
    else:
        print(f"Unexpected column name in file {file}. Skipping this file.")
        continue

    # Create empty lists to hold the separated cusip and isin values
    cusip = []
    isin = []

    # Loop through the 'cusip / isin' or 'isin / cusip' column
    for index, row in df.iterrows():
        if len(row[col_name]) == 9:  # CUSIPs are typically 9 characters
            cusip.append(row[col_name])
            isin.append('')
        elif len(row[col_name]) == 12:  # ISINs are typically 12 characters
            cusip.append('')
            isin.append(row[col_name])
        else:
            cusip.append('')
            isin.append('')

    # Add the new cusip and isin columns to the DataFrame
    df['isin'] = isin
    df['cusip'] = cusip
    

    # Drop the original 'cusip / isin' or 'isin / cusip' column
    df = df.drop(columns=[col_name])

    # Save it to the same file
    df.to_csv(file_path, index=False)
