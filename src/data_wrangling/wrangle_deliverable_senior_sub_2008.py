import os
import pandas as pd
import re

def process_data(data, filename, isin_col, cusip_col):
    data.insert(0, 'File Name', filename)

    if isin_col and cusip_col:
        print(f"Both 'isin' and 'cusip' found in file: {filename}")
        output_data = data[['File Name', isin_col, cusip_col]].copy()
        output_data.columns = ['final_name', 'isin', 'cusip']
    elif isin_col:
        print(f"Only 'isin' found in file: {filename}")
        output_data = data[['File Name', isin_col]].copy()
        output_data.columns = ['final_name', 'isin']
    elif cusip_col:
        print(f"Only 'cusip' found in file: {filename}")
        output_data = data[['File Name', cusip_col]].copy()
        output_data.columns = ['final_name', 'cusip']

    if 'isin' in output_data.columns:
        print(f"Processing 'isin' values in file: {filename}")
        output_data['isin'] = output_data['isin'].astype(str)
        output_data['isin'] = output_data['isin'].str.replace(',', '\n')
        output_data['isin'] = output_data['isin'].str.replace(' and ', '\n')
        output_data['isin'] = output_data['isin'].str.replace(' / ', '\n')
        output_data['isin'] = output_data['isin'].str.split('\n')
        output_data = output_data.explode('isin')

    output_data = output_data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    if 'isin' in output_data.columns and 'cusip' in output_data.columns:
        output_data = output_data.dropna(subset=['isin', 'cusip'], how='all')
    elif 'isin' in output_data.columns:
        output_data = output_data.dropna(subset=['isin'])
    elif 'cusip' in output_data.columns:
        output_data = output_data.dropna(subset=['cusip'])

    if 'isin' in output_data.columns and 'cusip' in output_data.columns:
        output_data = output_data[((output_data['isin'].str.len() >= 5) & (output_data['isin'].str.len() <= 30)) | 
                                  ((output_data['cusip'].str.len() >= 5) & (output_data['cusip'].str.len() <= 30))]
    elif 'isin' in output_data.columns:
        output_data = output_data[(output_data['isin'].str.len() >= 5) & (output_data['isin'].str.len() <= 30)]
    elif 'cusip' in output_data.columns:
        output_data = output_data

    filter_words = ['notes', 'loan', 'security', 'cusip', 'numbers']

    if 'isin' in output_data.columns:
        for word in filter_words:
            output_data = output_data[~output_data['isin'].str.contains(word, case=False, na=False)]
    if 'cusip' in output_data.columns:
        for word in filter_words:
            output_data = output_data[~output_data['cusip'].str.contains(word, case=False, na=False)]
    
    return output_data

current_directory = os.getcwd()
data_directory = os.path.join(current_directory, 'data')
raw_data_directory = os.path.join(data_directory, 'deliverable_obligations', 'raw')
output_directory = os.path.join(data_directory, 'deliverable_obligations', 'intermediate')
patterns = [r'\bisin\b', r'\bcusip\b']

files_to_process = [
    "20081106_kaupth_deliverable-obligations.xls",
    "20081105_glitni_deliverable-obligations.xls",
    "20081104_landsb_deliverable-obligations.xls",
]

year=2008
year_folder_path = os.path.join(raw_data_directory, str(year))

for filename in files_to_process:
    print(f"Processing file: {filename}")

    file_path = os.path.join(year_folder_path, filename)
    data = pd.read_excel(file_path, header=None)
    data_str = data.astype(str)

    if (data_str.applymap(lambda x: "seniority" in x.lower())).any().any():
        print(f"'Seniority' found in file: {filename}")
        
        for i, row in data.iterrows():
            row = row.astype(str).str.lower()
            if any(re.search(pattern, val) for val in row.values for pattern in patterns):
                data.columns = data.iloc[i]
                data = data.iloc[i + 1:]
                print(f"Found header row at index {i}")
                break

        data.columns = data.columns.str.lower()
        isin_col = next((str(col) for col in data.columns if re.search(r'\bisin\b', str(col), re.I)), None)
        cusip_col = next((str(col) for col in data.columns if re.search(r'\bcusip\b', str(col), re.I)), None)

        if isin_col is None and cusip_col is None:
            print(f"No 'isin' or 'cusip' in file: {filename}. Skipping file.")
            continue
        
        seniority_col = next((str(col) for col in data.columns if re.search(r'\bseniority\b', str(col), re.I)), None)

        if seniority_col is None:
            print(f"No 'seniority' in file: {filename}. Skipping file.")
            continue

        sub_data = data[data[seniority_col].str.contains('SUBLT2|Sub', case=False, na=False)]
        output_sub_data = process_data(sub_data, filename, isin_col, cusip_col)
        output_file_path = os.path.join(output_directory, f"{os.path.splitext(filename)[0].replace('deliverable-obligations', 'Subordinate')}_deliverable-obligations.csv")
        print(f"Saving file: {output_file_path}")
        output_sub_data.to_csv(output_file_path, index=False)

        snr_data = data[data[seniority_col].str.contains('SNRFOR|Senior', case=False, na=False)]
        output_snr_data = process_data(snr_data, filename, isin_col, cusip_col)
        output_file_path = os.path.join(output_directory, f"{os.path.splitext(filename)[0].replace('deliverable-obligations', 'Senior')}_deliverable-obligations.csv")
        print(f"Saving file: {output_file_path}")
        output_snr_data.to_csv(output_file_path, index=False)
    else:
        print(f"No 'seniority' in file:{filename}. Skipping file.")
        continue






filename = "20081006_famefrmc_deliverable-obligations.xls"

year_folder_path = os.path.join(raw_data_directory, str(year))
file_path = os.path.join(year_folder_path, filename)

data = pd.read_excel(file_path, header=None)
data_str = data.astype(str)

for i, row in data.iterrows():
    row = row.astype(str).str.lower()
    if any(re.search(pattern, val) for val in row.values for pattern in [r'\bisin\b', r'\bcusip\b']):
        data.columns = data.iloc[i]
        data = data.iloc[i + 1:]
        print(f"Found header row at index {i}")
        break

data.columns = data.columns.str.lower()

seniority_col = next((str(col) for col in data.columns if re.search(r'\bseniority\b', str(col), re.I)), None)
issuer_col = next((str(col) for col in data.columns if re.search(r'\bissuer\b', str(col), re.I)), None)

# Subordinate obligations
sub_data = data[data[seniority_col].str.contains('SUBLT2|Sub', case=False, na=False)]
sub_data_fannie = sub_data[sub_data[issuer_col].str.contains('FNMA', case=False, na=False)]
sub_data_freddie = sub_data[sub_data[issuer_col].str.contains('FHLMC', case=False, na=False)]

# Process and save subordinated data
output_sub_data_fannie = process_data(sub_data_fannie, filename, isin_col, cusip_col)
output_file_path_fannie_sub = os.path.join(output_directory, f"{os.path.splitext(filename)[0].replace('deliverable-obligations', 'Fannie-Mae-Subordinated')}_deliverable-obligations.csv")
output_sub_data_fannie.to_csv(output_file_path_fannie_sub, index=False)

output_sub_data_freddie = process_data(sub_data_freddie, filename, isin_col, cusip_col)
output_file_path_freddie_sub = os.path.join(output_directory, f"{os.path.splitext(filename)[0].replace('deliverable-obligations', 'Freddie-Mac-Subordinated')}_deliverable-obligations.csv")
output_sub_data_freddie.to_csv(output_file_path_freddie_sub, index=False)

# Senior obligations
snr_data = data[data[seniority_col].str.contains('SNRFOR|Senior', case=False, na=False)]
snr_data_fannie = snr_data[snr_data[issuer_col].str.contains('FNMA', case=False, na=False)]
snr_data_freddie = snr_data[snr_data[issuer_col].str.contains('FHLMC', case=False, na=False)]

# Process and save senior data
output_snr_data_fannie = process_data(snr_data_fannie, filename, isin_col, cusip_col)
output_file_path_fannie_snr = os.path.join(output_directory, f"{os.path.splitext(filename)[0].replace('deliverable-obligations', 'Fannie-Mae-Senior')}_deliverable-obligations.csv")
output_snr_data_fannie.to_csv(output_file_path_fannie_snr, index=False)

output_snr_data_freddie = process_data(snr_data_freddie, filename, isin_col, cusip_col)
output_file_path_freddie_snr = os.path.join(output_directory, f"{os.path.splitext(filename)[0].replace('deliverable-obligations', 'Freddie-Mac-Senior')}_deliverable-obligations.csv")
output_snr_data_freddie.to_csv(output_file_path_freddie_snr, index=False)
