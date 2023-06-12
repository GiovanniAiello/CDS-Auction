import pandas as pd
import re
import os
print(os.getcwd())
# Specify the file path to the dataset
dataset_path = 'data/final_database/auctions_main.csv'
# Read the dataset
data = pd.read_csv(dataset_path)


# Function to extract numeric value from a string
def extract_numeric_value(string):
    match = re.search(r'\d+(\.\d+)?', string)
    if match:
        return float(match.group())
    return None

# Create the new columns
data['noi_absolute_value'] = data['NOI'].apply(lambda x: extract_numeric_value(x) if isinstance(x, str) else None)
data['noi_absolute_value'] = data['noi_absolute_value']*1000000

# Round the 'noi_absolute_value' to 2 decimal places
data['noi_absolute_value'] = data['noi_absolute_value'].round(2)

data['noi_direction'] = data['NOI'].apply(lambda x: -1 if isinstance(x, str) and ('to buy' in x or 'bid' in x) else (1 if isinstance(x, str) and ('to sell' in x or 'offer' in x) else 0 if isinstance(x, str) and extract_numeric_value(x) == 0 else None))

data['currency'] = data['NOI'].apply(lambda x: re.findall(r'[^\d\s]+', x)[0] if isinstance(x, str) and re.findall(r'[^\d\s]+', x) else None)


database_path = 'data/raw_auction_csv'

# Iterate over each row of the dataset
for index, row in data.iterrows():
    identifier = row['identifier']
    
    # Find the file based on the identifier
    matching_files = [file for file in os.listdir(database_path) if file.endswith('.csv') and "Final Results" in file and identifier in file]
    
    if matching_files:
        file_path = os.path.join(database_path, matching_files[0])
        df = pd.read_csv(file_path, header=None)
        
        # Check if the first line is "Relevant Currency"
        if df.iloc[0, 0] == "Relevant Currency":
            # Update the 'currency' column with the value from the second line
            data.loc[data['identifier'] == identifier, 'currency'] = df.iloc[1, 0]



# Substitute $ with USD, € with EUR, and £ with GBP in the 'currency' column
data['currency'] = data['currency'].str.replace('$', 'USD').str.replace('€', 'EUR').str.replace('£', 'GBP')

# Remove all spaces from the 'currency' column
data['currency'] = data['currency'].str.replace(' ', '')


# Iterate over each row of the dataset
for index, row in data.iterrows():
    identifier = row['identifier']
    currency = row['currency']
    exchange_rate = None
    currencies_exchange = None

    # Check if currency is USD or $
    if currency is not None and ('USD' in currency or currency == '$'):
        exchange_rate = 1
        currencies_exchange = "USD/USD"
        print(f"Identifier: {identifier} - Currency is USD or $, exchange rate set to 1")
    else:
        # Look for CSV files in the folder
        csv_files = [file for file in os.listdir(database_path) if file.endswith('.csv') and all(word not in file for word in ['Final Price', 'Limit Orders', 'NOI', 'IMM', 'Physical', 'Markets'])]
        #print(f"Identifier: {identifier} - CSV files in folder: {csv_files}")

        # Check if the identifier matches any CSV file name
        matching_files = [file for file in csv_files if identifier in file]
        #print(f"Identifier: {identifier} - Matching files: {matching_files}")

        if matching_files:
            for csv_file in matching_files:
                csv_path = os.path.join(database_path, csv_file)
                df_csv = pd.read_csv(csv_path, header=None)
                if 'Auction Currency Rates' in str(df_csv.iloc[0, 0]):
                    usd_rates = df_csv[df_csv.iloc[:, 0].str.contains('USD')]
                    if not usd_rates.empty:
                        exchange_rate = usd_rates.iloc[-1, 1]
                        currencies_exchange = usd_rates.iloc[-1, 0]
                        break  # Break the loop if a match is found
                    else:
                        exchange_rate = df_csv.iloc[-1, 1]
                        currencies_exchange = df_csv.iloc[-1, 0]
                        

    # Update the exchange_rate column in the data at the corresponding row of the identifier
    data.loc[index, 'exchange_rate'] = exchange_rate
    data.loc[index, 'currencies_exchange'] = currencies_exchange

# Fill empty 'currency' values with the first three letters of 'currencies_exchange'
data['currency'].fillna(data['currencies_exchange'].str[:3], inplace=True)

# Fill values that have 'million', 'Million', or '.' with the first three letters of 'currencies_exchange'
data.loc[data['currency'].isin(['million', 'Million', '.']), 'currency'] = data['currencies_exchange'].str[:3]

# Fill empty 'currency' values with the first three letters of 'currencies_exchange'
data['currency'].fillna(data['currencies_exchange'].str[:3], inplace=True)


# Replace the null values in currency_exchange with the combination of currency1/currency2
data['currencies_exchange'].fillna(data['currency'] + '/' + data['currency'], inplace=True)

# Set the exchange rate to 1 for the rows where currency_exchange is None
data.loc[data['exchange_rate'].isnull(), 'exchange_rate'] = 1


from currency_converter import CurrencyConverter
from dateutil import parser

# Create an instance of CurrencyConverter
c = CurrencyConverter()

# Function to get the exchange rate from USD to a specific currency on a given date
def get_exchange_rate(date, currency):
    return c.convert(1, 'USD', currency, date=date)

# Iterate over each row of the dataset
for index, row in data.iterrows():
    currency = row['currency']
    currencies_exchange = row['currencies_exchange']
    date_str = row['date']

    # Parse the date string into a datetime object
    date = parser.parse(date_str).date()

    # Check if the currency is not USD and 'USD' is not present in currencies_exchange
    if currency != 'USD': #and not re.search(r'USD', currencies_exchange)
        # Get the exchange rate from USD to the specific currency on the given date
        exchange_rate = get_exchange_rate(date, currency)
        currencies_exchange = 'USD/' + currency

        # Update the exchange_rate and currencies_exchange columns
        data.at[index, 'exchange_rate'] = exchange_rate
        data.at[index, 'currencies_exchange'] = currencies_exchange
    # Convert 'noi_absolute_value' to USD
    data.at[index, 'noi_usd'] = row['noi_absolute_value'] / exchange_rate


# Specify the file path and name for saving the updated DataFrame
output_folder = "../../data/final_database"
os.makedirs(output_folder, exist_ok=True)
output_csv = os.path.join(output_folder, "auctions_main_updated.csv")

# Save the updated DataFrame as CSV
data.to_csv(output_csv, index=False)
print(f"Updated DataFrame saved as: {output_csv}")