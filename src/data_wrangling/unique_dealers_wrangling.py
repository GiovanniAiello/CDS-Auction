import pandas as pd
import os

# Set the file path
file_path = os.path.join('output', 'tables', 'unique_dealers.csv')

# Read the unique_dealers.csv file
df = pd.read_csv(file_path)

# Define a dictionary mapping dealers to their respective financial group
financial_groups = {
    'ABN AMRO Bank NV': 'ABN AMRO',
    'BNP Paribas': 'BNP Paribas',
    'BNP Paribas SA': 'BNP Paribas',
    'BNP Paribas Securities (Japan) LTD': 'BNP Paribas',
    'Barclays': 'Barclays',
    'Barclays Bank PLC': 'Barclays',
    'Barclays Capital Inc': 'Barclays',
    'Barclays Capital Japan LTD': 'Barclays',
    'Barclays Capital Japan LTD (A)': 'Barclays',
    'Bear Stearns & Co Inc': 'Bear Stearns',
    'Bear Stearns Credit Products Inc': 'Bear Stearns',
    'BofA': 'Bank of America',
    'BofA / Merrill Lynch': 'Bank of America',
    'BofA NA': 'Bank of America',
    'BofA Securities Inc': 'Bank of America',
    'BofA Securities LLC': 'Bank of America',
    'Citibank': 'Citigroup',
    'Citibank Global Markets Inc': 'Citigroup',
    'Citibank NA': 'Citigroup',
    'Citigroup': 'Citigroup',
    'Citigroup Financial Products Inc': 'Citigroup',
    'Citigroup Global Markets Inc': 'Citigroup',
    'Citigroup Global Markets Japan Inc': 'Citigroup',
    'Citigroup Global Markets LTD': 'Citigroup',
    'Citigroup Global Markets LTD PLC': 'Citigroup',
    'Credit Suisse': 'Credit Suisse',
    'Credit Suisse AG': 'Credit Suisse',
    'Credit Suisse First Boston LLC': 'Credit Suisse',
    'Credit Suisse International': 'Credit Suisse',
    'Credit Suisse Securities (Japan) LTD': 'Credit Suisse',
    'Credit Suisse Securities (USA) LLC': 'Credit Suisse',
    'Deutsche Bank': 'Deutsche Bank',
    'Deutsche Bank AG': 'Deutsche Bank',
    'Deutsche Bank AG London': 'Deutsche Bank',
    'Deutsche Bank Securities Inc': 'Deutsche Bank',
    'Deutsche Securities Inc': 'Deutsche Bank',
    'Dresdner Bank AG': 'Dresdner Bank',
    'Goldman Sachs': 'Goldman Sachs',
    'Goldman Sachs & Co': 'Goldman Sachs',
    'Goldman Sachs & Co LLC': 'Goldman Sachs',
    'Goldman Sachs Credit Partners LP': 'Goldman Sachs',
    'Goldman Sachs International': 'Goldman Sachs',
    'Goldman Sachs Lending Partners LP': 'Goldman Sachs',
    'Goldman Sachs Loan Partners': 'Goldman Sachs',
    'HSBC': 'HSBC',
    'HSBC Bank': 'HSBC',
    'HSBC Bank PLC': 'HSBC',
    'HSBC Bank USA': 'HSBC',
    'HSBC Bank USA NA': 'HSBC',
    'HSBC LTD': 'HSBC',
    'HSBC USA NA': 'HSBC',
    'ING Bank NV': 'ING Bank',
    'JPM Chase': 'JPMorgan',
    'JPM Chase Bank NA': 'JPMorgan',
    'JPM Securities Inc': 'JPMorgan',
    'JPM Securities Japan Co LTD': 'JPMorgan',
    'JPM Securities LLC': 'JPMorgan',
    'JPM Securities PLC': 'JPMorgan',
    'Lehman Brothers Inc': 'Lehman Brothers',
    'Merrill Lynch': 'Merrill Lynch',
    'Merrill Lynch Capital Services Inc': 'Merrill Lynch',
    'Merrill Lynch Credit Products LLC': 'Merrill Lynch',
    'Merrill Lynch Government Securities Inc': 'Merrill Lynch',
    'Merrill Lynch International': 'Merrill Lynch',
    'Merrill Lynch Japan Securities Co LTD': 'Merrill Lynch',
    'Merrill Lynch Pierce Fenner & Smith': 'Merrill Lynch',
    'Merrill Lynch Pierce Fenner & Smith Inc': 'Merrill Lynch',
    'Mitsubishi UFJ Securities Co LTD': 'Mitsubishi UFJ',
    'Mizuho Securities Co LTD': 'Mizuho',
    'Morgan Stanley': 'Morgan Stanley',
    'Morgan Stanley & Co Inc': 'Morgan Stanley',
    'Morgan Stanley & Co International': 'Morgan Stanley',
    'Morgan Stanley & Co International PLC': 'Morgan Stanley',
    'Morgan Stanley & Co LLC': 'Morgan Stanley',
    'Morgan Stanley Emerging Markets Inc': 'Morgan Stanley',
    'Morgan Stanley Japan Securities Co LTD': 'Morgan Stanley',
    'Morgan Stanley MUFG Securities Co LTD': 'Morgan Stanley',
    'Morgan Stanley Senior Funding Inc': 'Morgan Stanley',
    'Nomura': 'Nomura',
    'Nomura International PLC': 'Nomura',
    'Nomura Securities Co LTD': 'Nomura',
    'RBC Capital Markets LLC': 'RBC Capital Markets',
    'Royal Bank of Scotland': 'Royal Bank of Scotland',
    'Royal Bank of Scotland PLC': 'Royal Bank of Scotland',
    'Societe Generale': 'Societe Generale',
    'Societe Generale SA': 'Societe Generale',
    'Standard Chartered Bank': 'Standard Chartered Bank',
    'UBS': 'UBS',
    'UBS AG': 'UBS',
    'UBS LTD': 'UBS',
    'UBS Securities Japan LTD': 'UBS',
    'UBS Securities LLC': 'UBS'
}

# Add a new column 'Group' based on the financial_groups dictionary
df['Group'] = df['Dealer'].map(financial_groups)



# Define a dictionary mapping full group names to their shorter labels
group_labels = {
    'ABN AMRO': 'ABN',
    'BNP Paribas': 'BNP',
    'Barclays': 'Barclays',
    'Bear Stearns': 'Bear Stearns',
    'Bank of America': 'BofA',
    'Citigroup': 'Citigroup',
    'Credit Suisse': 'Credit Suisse',
    'Deutsche Bank': 'Deutsche Bank',
    'Dresdner Bank': 'Dresdner Bank',
    'Goldman Sachs': 'Goldman Sachs',
    'HSBC': 'HSBC',
    'ING Bank': 'ING',
    'JPMorgan': 'JPM',
    'Lehman Brothers': 'Lehman Brothers',
    'Merrill Lynch': 'Merrill Lynch',
    'Mitsubishi UFJ': 'Mitsubishi UFJ',
    'Mizuho': 'Mizuho',
    'Morgan Stanley': 'Morgan Stanley',
    'Nomura': 'Nomura',
    'RBC Capital Markets': 'RBC',
    'Royal Bank of Scotland': 'RBS',
    'Societe Generale': 'Societe Generale',
    'Standard Chartered Bank': 'Standard Chartered',
    'UBS': 'UBS'
}



# Add a new column 'Label' with the shorter group labels
df['Label'] = df['Group'].map(group_labels)


# Check for NaN values in the 'Label' column
nan_labels = df[df['Label'].isna()]

# Check for empty spaces in the 'Label' column
empty_labels = df[df['Label'].str.strip() == '']

# Combine NaN and empty spaces
missing_labels = pd.concat([nan_labels, empty_labels])

# Print the missing labels
print(missing_labels)


# Count the number of unique groups
num_groups = len(df['Label'].unique())

# Print the number of groups
print("Number of unique groups:", num_groups)
print(df['Label'].unique())
# Save the updated dataframe to a new CSV file
output_path = os.path.join('output', 'tables', 'unique_dealers_updated.csv')
df.to_csv(output_path, index=False)
