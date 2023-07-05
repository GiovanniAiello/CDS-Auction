import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# Specify the file path to the dataset
dataset_path = 'data/final_database/auctions_main_updated.csv'

# Read the dataset
data = pd.read_csv(dataset_path)

# Extract the year from the first four digits of the "Identifier" column
data['Year'] = data['identifier'].str[:4]
data['Year'] = pd.to_numeric(data['Year'], errors='coerce')

# Count the number of auctions for each year
auctions_per_year = data['Year'].value_counts().sort_index()
total_auctions = auctions_per_year.sum()

# Print the results
print("Auctions per year:")
print(auctions_per_year)
print("Total auctions:", total_auctions)

# Filter the data for auctions with stage 2 after 2005
auctions_with_stage2_after_2005 = data[
    (data['noi_direction'].isin([-1, 1])) &
    (data['noi_usd'] != 0) &
    (data['Year'] > 2005)
]
auctions_stage2_after_2005_per_year = auctions_with_stage2_after_2005['Year'].value_counts().sort_index()
total_auctions_stage2_after_2005 = auctions_stage2_after_2005_per_year.sum()

# Print the results
print("Auctions with stage 2 after 2005:")
print(auctions_stage2_after_2005_per_year)
print("Total auctions with stage 2 after 2005:", total_auctions_stage2_after_2005)

# Save the tables as CSV files
output_folder = 'output/tables'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

auctions_per_year.to_csv(os.path.join(output_folder, 'auctions_per_year.csv'))
auctions_stage2_after_2005_per_year.to_csv(os.path.join(output_folder, 'auctions_stage2_after_2005_per_year.csv'))

print("CSV files saved successfully.")

# Count the number of auctions to buy and to sell
auctions_to_buy = auctions_with_stage2_after_2005[auctions_with_stage2_after_2005['noi_direction'] == -1].shape[0]
auctions_to_sell = auctions_with_stage2_after_2005[auctions_with_stage2_after_2005['noi_direction'] == 1].shape[0]

# Print the results
print("Number of auctions to buy:", auctions_to_buy)
print("Number of auctions to sell:", auctions_to_sell)

# Save the counts as a DataFrame
auction_counts = pd.DataFrame({'Auctions to Buy': [auctions_to_buy], 'Auctions to Sell': [auctions_to_sell]})

# Save the counts as a CSV file
auction_counts.to_csv(os.path.join(output_folder, 'auction_counts.csv'), index=False)

print("CSV files saved successfully.")


# Compute descriptive statistics for final price
descriptive_stats_final_price = auctions_with_stage2_after_2005['final_price'].describe()

# Compute descriptive statistics for IMM
descriptive_stats_imm = auctions_with_stage2_after_2005['IMM'].describe()

# Compute descriptive statistics for absolute value of NOI
descriptive_stats_noi_absolute_value = auctions_with_stage2_after_2005['noi_usd'].describe()/1000000

# Compute 10th and 90th percentiles separately for final price
percentile_10_final_price = np.percentile(auctions_with_stage2_after_2005['final_price'], 10)
percentile_90_final_price = np.percentile(auctions_with_stage2_after_2005['final_price'], 90)

# Compute 10th and 90th percentiles separately for IMM
percentile_10_imm = np.percentile(auctions_with_stage2_after_2005['IMM'], 10)
percentile_90_imm = np.percentile(auctions_with_stage2_after_2005['IMM'], 90)


# Compute 10th and 90th percentiles separately for absolute value of NOI
percentile_10_noi_absolute_value = np.percentile(auctions_with_stage2_after_2005['noi_absolute_value'], 10)/1000000
percentile_90_noi_absolute_value = np.percentile(auctions_with_stage2_after_2005['noi_absolute_value'], 90)/1000000



# Round the descriptive statistics to the second decimal place
round_descriptive_stats_final_price = descriptive_stats_final_price.round(2)
round_descriptive_stats_imm = descriptive_stats_imm.round(2)
round_descriptive_stats_noi_absolute_value = descriptive_stats_noi_absolute_value.round(2)
percentile_10_final_price = round(percentile_10_final_price, 2)
percentile_90_final_price = round(percentile_90_final_price, 2)
percentile_10_imm = round(percentile_10_imm, 2)
percentile_90_imm = round(percentile_90_imm, 2)
percentile_10_noi_absolute_value = round(percentile_10_noi_absolute_value, 2)
percentile_90_noi_absolute_value = round(percentile_90_noi_absolute_value, 2)

# Create a DataFrame to store the descriptive statistics
descriptive_stats = pd.DataFrame(columns=['Variable', 'N', 'Mean', 'SD', 'Min', 'P10', 'P50', 'P90', 'Max'])

# Final Price
descriptive_stats.loc[0] = ['Final Price', auctions_with_stage2_after_2005.shape[0], round_descriptive_stats_final_price['mean'], round_descriptive_stats_final_price['std'],
                           round_descriptive_stats_final_price['min'], percentile_10_final_price,
                           round_descriptive_stats_final_price['50%'], percentile_90_final_price,
                           round_descriptive_stats_final_price['max']]

# IMM
descriptive_stats.loc[1] = ['IMM', auctions_with_stage2_after_2005.shape[0], round_descriptive_stats_imm['mean'], round_descriptive_stats_imm['std'],
                           round_descriptive_stats_imm['min'], percentile_10_imm,
                           round_descriptive_stats_imm['50%'], percentile_90_imm,
                           round_descriptive_stats_imm['max']]

# Absolute Value of NOI
descriptive_stats.loc[2] = ['|NOI| (M)', auctions_with_stage2_after_2005.shape[0], round_descriptive_stats_noi_absolute_value['mean'], round_descriptive_stats_noi_absolute_value['std'],
                           round_descriptive_stats_noi_absolute_value['min'], percentile_10_noi_absolute_value,
                           round_descriptive_stats_noi_absolute_value['50%'], percentile_90_noi_absolute_value,
                           round_descriptive_stats_noi_absolute_value['max']]

# Compute descriptive statistics for n_dealers
descriptive_stats_n_dealers = auctions_with_stage2_after_2005['n_dealers'].describe()

# Compute 10th and 90th percentiles separately for n_dealers
percentile_10_n_dealers = np.percentile(auctions_with_stage2_after_2005['n_dealers'], 10)
percentile_90_n_dealers = np.percentile(auctions_with_stage2_after_2005['n_dealers'], 90)

# Round the descriptive statistics and percentiles to the second decimal place
round_descriptive_stats_n_dealers = descriptive_stats_n_dealers.round(2)
percentile_10_n_dealers = round(percentile_10_n_dealers, 2)
percentile_90_n_dealers = round(percentile_90_n_dealers, 2)

# Add the n_dealers summary statistics to the descriptive_stats DataFrame
descriptive_stats.loc[3] = ['N Dealers', auctions_with_stage2_after_2005.shape[0], round_descriptive_stats_n_dealers['mean'], round_descriptive_stats_n_dealers['std'],
                            round_descriptive_stats_n_dealers['min'], percentile_10_n_dealers,
                            round_descriptive_stats_n_dealers['50%'], percentile_90_n_dealers,
                            round_descriptive_stats_n_dealers['max']]

# Save the descriptive statistics as CSV
descriptive_stats.to_csv('output/tables/descriptive_stats.csv', index=False)

# Save the descriptive statistics as LaTeX table
descriptive_stats.to_latex('output/tables/descriptive_stats.tex', index=False)



