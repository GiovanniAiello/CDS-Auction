import pandas as pd
import os
import numpy as np
#Directory containing the CSV files
current_directory = os.getcwd()
data_directory = os.path.join(current_directory, 'data')
directory = os.path.join(data_directory, 'deliverable_obligations', 'intermediate')

# Define your original
file = '20171101_MONTE_CDS-2003_deliverable-obligations.csv'
file_path = os.path.join(directory, file)

# Read the original file
df = pd.read_csv(file_path)

# Extract the first 5 rows
df_first_five = df.head(5)

# Save the first 5 rows to a new file
new_file = '20171101_MONTE_CDS-2003-Bucket-1_deliverable-obligations.csv'
new_file_path = os.path.join(directory, new_file)
df_first_five.to_csv(new_file_path, index=False)

# Rename the original file
renamed_file = '20171101_MONTE_CDS-2003-Bucket-2_deliverable-obligations.csv'
renamed_file_path = os.path.join(directory, renamed_file)
os.rename(file_path, renamed_file_path)


# Define your original
file = '20171005_BPESP_CDS-2003_deliverable-obligations.csv'
file_path = os.path.join(directory, file)

# Read the original file
df = pd.read_csv(file_path)

# Extract the first row to form Bucket 1
df_bucket_1 = df.iloc[:1]

# Save the first row to a new file
new_file_1 = '20171005_BPESP_CDS-2003-Bucket-1_deliverable-obligations.csv'
new_file_path_1 = os.path.join(directory, new_file_1)
df_bucket_1.to_csv(new_file_path_1, index=False)

# Extract the rest of the rows to form the intermediate bucket
df_intermediate_bucket = df.iloc[1:2]  # as you want to include second row in Bucket 2

# Create Bucket 2 by appending Bucket 1 to the intermediate bucket
df_bucket_2 = pd.concat([df_bucket_1, df_intermediate_bucket])

# Save Bucket 2 to a new file
new_file_2 = '20171005_BPESP_CDS-2003-Bucket-2_deliverable-obligations.csv'
new_file_path_2 = os.path.join(directory, new_file_2)
df_bucket_2.to_csv(new_file_path_2, index=False)

# delete the original file
os.remove(file_path)


# NSINO 2016 (number 1 removed)

# Define your original file and paths for new files
original_file = '20160622_NSINO_CDS_deliverable-obligations.csv'
file_path = os.path.join(directory, original_file)

new_file_path_1 = os.path.join(directory, '20160622_NSINO_CDS-Bucket_deliverable-obligations.csv')
new_file_path_2 = os.path.join(directory, '20160622_NSINO_CDS-Bucket-3_deliverable-obligations.csv')
new_file_path_3 = os.path.join(directory, '20160622_NSINO_CDS-Bucket-4_deliverable-obligations.csv')

# Read in the CSV file
data = pd.read_csv(file_path)

# Delete the old file
os.remove(file_path)

# Extract rows 2-3 and save them to new file
bucket_1 = data.iloc[1:3]  # Python uses 0-based indexing
bucket_1.to_csv(new_file_path_1, index=False)

# Extract rows 2-4 and save them to new file
bucket_2 = data.iloc[1:4]
bucket_2.to_csv(new_file_path_2, index=False)

# Extract rows 2-6 and save them to new file
bucket_3 = data.iloc[1:6]
bucket_3.to_csv(new_file_path_3, index=False)




# File paths
file_path = os.path.join(directory, '20130605_BANKSA_CDS-SNR-or-SUB_deliverable-obligations.csv')
new_file_path_1 = os.path.join(directory, '20130605_BANKSA_CDS-SNR-or-SUB-Bucket-1_deliverable-obligations.csv')
new_file_path_2 = os.path.join(directory, '20130605_BANKSA_CDS-SNR-or-SUB-Bucket-2_deliverable-obligations.csv')
new_file_path_3 = os.path.join(directory, '20130605_BANKSA_CDS-SNR-or-SUB-Bucket-3_deliverable-obligations.csv')

# Load the data
df = pd.read_csv(file_path)

# Save different parts of the data into different files
bucket_1 = df.iloc[np.r_[0:11, 19:21], :]
bucket_1.to_csv(new_file_path_1, index=False)

bucket_2 = pd.concat([bucket_1, df.iloc[11:18, :]])
bucket_2.to_csv(new_file_path_2, index=False)

bucket_3 = pd.concat([bucket_2, df.iloc[21:23, :]])
bucket_3.to_csv(new_file_path_3, index=False)

# Concatenate bucket 1, bucket 2, and bucket 3 with row 19 and update the original file
concatenated_bucket = pd.concat([ bucket_3, df.iloc[18:19, :]])
concatenated_bucket.to_csv(file_path, index=False)




# File path and paths for new files
original_file = '20130404_SNSBNK_CDS-SNR-or-SUB_deliverable-obligations.csv'
file_path = os.path.join(directory, original_file)

new_file_path_1 = os.path.join(directory, '20130404_SNSBNK_CDS-SNR-or-SUB-Bucket-1_deliverable-obligations.csv')


# Read the CSV file
data = pd.read_csv(file_path)

# Extract the first 6 rows and save to new file
bucket_1 = data.iloc[:6]
bucket_1.to_csv(new_file_path_1, index=False)




# Read the CSV file
file_path = os.path.join(directory, '20120202_NRAMC_CDS_deliverable-obligations.csv')
df = pd.read_csv(file_path)

# Create Bucket 1 (bonds from 1 to 16)
bucket_1 = df.iloc[0:16]

# Create intermediate bucket (bonds from 17 to 22)
intermediate_bucket = df.iloc[16:22]

# Combine Bucket 1 and intermediate bucket to form Bucket 2
bucket_2 = pd.concat([bucket_1, intermediate_bucket])

# Save Bucket 1 to a new CSV file
bucket_1.to_csv(os.path.join(directory, '20120202_NRAMC_CDS-Bucket-1_deliverable-obligations.csv'), index=False)

# Save Bucket 2 to a new CSV file
bucket_2.to_csv(os.path.join(directory, '20120202_NRAMC_CDS-Bucket-2_deliverable-obligations.csv'), index=False)

# delete the original file
os.remove(file_path)


# Define your original file and paths for new files
original_file = '20111005_IPBS2_CDS-Sen_deliverable-obligations.csv'
file_path = os.path.join(directory, original_file)

new_file_path_1 = os.path.join(directory, '20111005_IPBS2_CDS-Senior-Bucket-1_deliverable-obligations.csv')
new_file_path_2 = os.path.join(directory, '20111005_IPBS2_CDS-Senior-Bucket-2_deliverable-obligations.csv')

# Read the original file
df = pd.read_csv(file_path)

# Extract rows 1-13 to form Bucket 1
bucket_1 = df.iloc[0:13]

# Save Bucket 1 to a new file
bucket_1.to_csv(new_file_path_1, index=False)

# Extract rows 14-23 to form Bucket 2
bucket_2 = pd.concat([bucket_1, df.iloc[13:23]])

# Save Bucket 2 to a new file
bucket_2.to_csv(new_file_path_2, index=False)

# delete the original file
os.remove(file_path)

original_file = '20111005_IPBS2_CDS-Sub_deliverable-obligations.csv'
file_path = os.path.join(directory, original_file)
os.remove(file_path)


# Define your original file and paths for new files
original_file = '20110729_IPBS_CDS-Sub_deliverable-obligations.csv'
file_path = os.path.join(directory, original_file)

new_file_path_2 = os.path.join(directory, '20110729_IPBS_CDS-Subordinated-Bucket1_deliverable-obligations.csv')
new_file_path_4 = os.path.join(directory, '20110729_IPBS_CDS-Subordinated-Bucket2_deliverable-obligations.csv')
new_file_path_6 = os.path.join(directory, '20110729_IPBS_CDS-Subordinated-Bucket3_deliverable-obligations.csv')

# Read the CSV file
data = pd.read_csv(file_path)

# Extract rows 1 to 13 and save them to new files (Bucket 1)
bucket_1 = data.iloc[0:14]
bucket_1.to_csv(new_file_path_2, index=False)

# Extract rows 15 to 25 and save them to new files (Bucket 2)
bucket_2 = pd.concat([bucket_1, data.iloc[14:25]])
bucket_2.to_csv(new_file_path_4, index=False)

# Extract rows 26 to 29 and save them to new files (Bucket 3)
bucket_3 = pd.concat([bucket_2, data.iloc[25:29]])
bucket_3.to_csv(new_file_path_6, index=False)

# Remove the old file
os.remove(file_path)


# Define your original file and paths for new files
original_file = '20110729_IPBS_CDS-Sen_deliverable-obligations.csv'
file_path = os.path.join(directory, original_file)

new_file_path_1 = os.path.join(directory, '20110729_IPBS_CDS-Senior-Bucket1_deliverable-obligations.csv')
new_file_path_3 = os.path.join(directory, '20110729_IPBS_CDS-Senior-Bucket2_deliverable-obligations.csv')
new_file_path_5 = os.path.join(directory, '20110729_IPBS_CDS-Senior-Bucket3_deliverable-obligations.csv')

# Read the CSV file
data = pd.read_csv(file_path)

# Extract rows 1 to 14 and save them to new files (Bucket 1)
bucket_1 = data.iloc[0:13]
bucket_1.to_csv(new_file_path_1, index=False)

# Extract rows 15 to 25 and save them to new files (Bucket 2)
bucket_2 = pd.concat([bucket_1, data.iloc[13:23]])
bucket_2.to_csv(new_file_path_3, index=False)

# Extract rows 26 to 29 and save them to new files (Bucket 3)
bucket_3 = pd.concat([bucket_2, data.iloc[23:24]])
bucket_3.to_csv(new_file_path_5, index=False)

# Remove the old file
os.remove(file_path)


# Define your original file and paths for new files
original_file = '20110728_BKIR_CDS-Sub_deliverable-obligations.csv'
file_path = os.path.join(directory, original_file)

new_file_path_1 = os.path.join(directory, '20110728_BKIR_CDS-SNR-or-SUB-Bucket1_deliverable-obligations.csv')
new_file_path_3 = os.path.join(directory, '20110728_BKIR_CDS-Subordinated-Bucket2_deliverable-obligations.csv')
new_file_path_5 = os.path.join(directory, '20110728_BKIR_CDS-Subordinated-Bucket3_deliverable-obligations.csv')
new_file_path_7 = os.path.join(directory, '20110728_BKIR_CDS-Subordinated-Bucket6_deliverable-obligations.csv')

# Read the CSV file
data = pd.read_csv(file_path)

# Extract rows 1 to 54 for Bucket 1
bucket_1 = data.iloc[0:55]
bucket_1.to_csv(new_file_path_1, index=False)

# Extract rows 1 to 78 for Bucket 2
bucket_2 = pd.concat([bucket_1, data.iloc[55:80]])
bucket_2.to_csv(new_file_path_3, index=False)

# Extract rows 1 to 79 for Bucket 3
bucket_3 = pd.concat([bucket_2, data.iloc[80:83]])
bucket_3.to_csv(new_file_path_5, index=False)

# Extract rows 1 to 83 for Bucket 6
bucket_6 = pd.concat([bucket_3, data.iloc[83:89]])
bucket_6.to_csv(new_file_path_7, index=False)
os.remove(file_path)


# Define your original file and paths for new files
original_file = '20110728_BKIR_CDS-Sen_deliverable-obligations.csv'
file_path = os.path.join(directory, original_file)

new_file_path_2 = os.path.join(directory, '20110728_BKIR_CDS-Senior-Bucket2_deliverable-obligations.csv')
new_file_path_4 = os.path.join(directory, '20110728_BKIR_CDS-Senior-Bucket3_deliverable-obligations.csv')
new_file_path_6 = os.path.join(directory, '20110728_BKIR_CDS-Senior-Bucket6_deliverable-obligations.csv')

# Read the CSV file
data = pd.read_csv(file_path)

# Extract rows 1 to 54 for Bucket 1
bucket_1 = data.iloc[0:55]

# Extract rows 1 to 78 for Bucket 2
bucket_2 = pd.concat([bucket_1, data.iloc[55:79]])
bucket_2.to_csv(new_file_path_2, index=False)

# Extract rows 1 to 79 for Bucket 3
bucket_3 = pd.concat([bucket_2, data.iloc[79:80]])
bucket_3.to_csv(new_file_path_4, index=False)

# Extract rows 1 to 83 for Bucket 6
bucket_6 = pd.concat([bucket_3, data.iloc[80:84]])
bucket_6.to_csv(new_file_path_6, index=False)

# Remove the old file
os.remove(file_path)



# Define your original file and paths for new files
original_file = '20110202_ANGBKL2_CDS-Sen_deliverable-obligations.csv'
file_path = os.path.join(directory, original_file)

new_file_path = os.path.join(directory, '20110202_ANGBKL2_CDS-25-years-maturity_deliverable-obligations.csv')

# Read the CSV file
data = pd.read_csv(file_path)

# Extract rows 1 to 54 for Bucket 1
bucket_1 = data.iloc[0:38]
bucket_1.to_csv(new_file_path, index=False)

# Remove the old file
os.remove(file_path)



original_file = '20110202_ANGBKL2_CDS-Sub_deliverable-obligations.csv'
file_path = os.path.join(directory, original_file)
os.remove(file_path)


# Define your original file and paths for new files
original_file = '20101209_ANGBKL_CDS-Sub_deliverable-obligations.csv'
file_path = os.path.join(directory, original_file)

new_file_path_1 = os.path.join(directory, '20101209_ANGBKL_CDS-SNR-or-SUB-Bucket1_deliverable-obligations.csv')
new_file_path_3 = os.path.join(directory, '20101209_ANGBKL_CDS-Subordinated-Bucket2_deliverable-obligations.csv')
new_file_path_5 = os.path.join(directory, '20101209_ANGBKL_CDS-Subordinated-Bucket3_deliverable-obligations.csv')

# Read the CSV file
data = pd.read_csv(file_path)

# Extract rows 1 to 54 for Bucket 1
bucket_1 = data.iloc[0:36]
bucket_1.to_csv(new_file_path_1, index=False)

# Extract rows 1 to 78 for Bucket 2
bucket_2 = pd.concat([bucket_1, data.iloc[36:49]])
bucket_2.to_csv(new_file_path_3, index=False)

# Extract rows 1 to 79 for Bucket 3
bucket_3 = pd.concat([bucket_2, data.iloc[49:52]])
bucket_3.to_csv(new_file_path_5, index=False)


os.remove(file_path)


# Define your original file and paths for new files
original_file = '20101209_ANGBKL_CDS-Sen_deliverable-obligations.csv'
file_path = os.path.join(directory, original_file)

new_file_path_2 = os.path.join(directory, '20101209_ANGBKL_CDS-Senior-Bucket2_deliverable-obligations.csv')
new_file_path_4 = os.path.join(directory, '20101209_ANGBKL_CDS-Senior-Bucket3_deliverable-obligations.csv')

# Read the CSV file
data = pd.read_csv(file_path)

# Extract rows 1 to 54 for Bucket 1
bucket_1 = data.iloc[0:36]

# Extract rows 1 to 78 for Bucket 2
bucket_2 = pd.concat([bucket_1, data.iloc[36:48]])
bucket_2.to_csv(new_file_path_2, index=False)

# Extract rows 1 to 79 for Bucket 3
bucket_3 = pd.concat([bucket_2, data.iloc[48:50]])
bucket_3.to_csv(new_file_path_4, index=False)

# Remove the old file
os.remove(file_path)




# Define your original file and paths for new files
original_file = '20090730_brabin-Sen_deliverable-obligations.csv'
file_path = os.path.join(directory, original_file)

new_file_path = os.path.join(directory, '20090730_brabin_Sen_deliverable-obligations.csv')

# Read the CSV file
data = pd.read_csv(file_path)

# Extract rows 1 to 54 for Bucket 1
data.to_csv(new_file_path, index=False)

# Remove the old file
os.remove(file_path)



# Define your original file and paths for new files
original_file = '20090730_brabin-Sub_deliverable-obligations.csv'
file_path = os.path.join(directory, original_file)

new_file_path = os.path.join(directory, '20090730_brabin_Sub_deliverable-obligations.csv')

# Read the CSV file
data = pd.read_csv(file_path)

# Extract rows 1 to 54 for Bucket 1
data.to_csv(new_file_path, index=False)

# Remove the old file
os.remove(file_path)