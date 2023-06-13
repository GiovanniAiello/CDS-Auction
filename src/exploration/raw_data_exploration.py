# %% [markdown]
# ### Physical Settlement Requests and IMM

# %%
## import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os
import glob
from matplotlib.lines import Line2D
import matplotlib.colors as mcolors # used for creating a color map for the dots
import re # used for regular expressions
from matplotlib.patches import Patch


## set up the directories
path = os.getcwd()
data_path = os.path.join(path, "data/raw_auction_csv")
path_out_fig_first =  os.path.join(path, "output/figures/first_stage")
if not os.path.exists(path_out_fig_first):
    os.makedirs(path_out_fig_first)

csv_files = glob.glob(os.path.join(data_path, "*.csv"))
csv_files = [file for file in csv_files if "Limit Orders" not in file]


## create colors for plots
# Load the auctions_main_updated DataFrame
auctions_main_updated_path = 'data/final_database/auctions_main_updated.csv'
full_auction_main_updated_path = os.path.abspath(auctions_main_updated_path)

print(f"Full path: {full_auction_main_updated_path}")
auctions_main_updated = pd.read_csv(auctions_main_updated_path)

# Create colors for plots
bid_color = 'darkorange'
offer_color = 'royalblue'

counter = 0
for file in csv_files:
    try:
        if "Dealer,Bid,Offer" in open(file).read():
            df = pd.read_csv(file)
            df = df.dropna(how='all')

            dealers = df['Dealer'].unique()
            plt.figure(figsize=(18, 10))

            filename = os.path.basename(file)
            name, ext = os.path.splitext(filename)
            #plt.suptitle(name, y=title_padding)

            for i, dealer in enumerate(dealers):
                group = df[df['Dealer'] == dealer]
                x = [i for _ in range(len(group))]
                bid_x = group['Bid'].values
                plt.scatter(bid_x, x, color=bid_color, marker='s', label='Bid' if i == 0 else '')
                offer_x = group['Offer'].values
                plt.scatter(offer_x, x, color=offer_color, marker='s', label='Offer' if i == 0 else '')
                plt.plot([bid_x[0], offer_x[0]], [i, i], color='black', linestyle=':')
            average_bid = df['Bid'].mean()
            average_offer = df['Offer'].mean()
            average_all = (df['Bid'].mean() + df['Offer'].mean())/2

            #plt.axvline(average_bid, color='darkgrey', linestyle='dashed', label='Avg Bid')  # Changed to axvline for x-axis
            #plt.axvline(average_offer, color='grey', linestyle='dashed', label='Avg Offer')  # Changed to axvline for x-axis
            plt.axvline(average_all, color='grey', linestyle='solid', label='Avg Bid and Offer')  # Changed to axvline for x-axis

            df['Dealer_short'] = df['Dealer'].str.slice(stop=36)
            plt.yticks(range(len(dealers)), df['Dealer_short'], rotation=0)  # Set y-axis ticks and disable rotation

            plt.gca().invert_yaxis()  # Invert y-axis

            # Order the bids and offers in decreasing and increasing order respectively:
            df_bid_asc = df.sort_values(by=['Bid'], ascending=False)
            df_off_desc = df.sort_values(by=['Offer'], ascending=True)

            # Compare the bids and offers, and store the remaining bids and offers in the variables defined in step 2:
            # Order the bids and offers in decreasing and increasing order respectively:
            df_bid_asc = df.sort_values(by=['Bid'], ascending=False)
            df_off_desc = df.sort_values(by=['Offer'], ascending=True)

            i,j = 0,0
            while i < len(df_bid_asc) and j < len(df_off_desc):
                if df_bid_asc.iloc[i]['Bid'] >= df_off_desc.iloc[j]['Offer']:
                    df_bid_asc = df_bid_asc.drop(df_bid_asc.index[i])
                    df_off_desc = df_off_desc.drop(df_off_desc.index[j])
                else:
                    i+=1
                    j+=1

            n = len(df_bid_asc)
            if n == 0:
                IMM = None
            else:
                IMM = (df_off_desc['Offer'].mean() + df_bid_asc['Bid'].mean())/2
            computed_IMM = round(IMM * 8) / 8
            print(name)
            print("Computed IMM: ",IMM)

            # Add the computed and real IMM values to the plot
            plt.axvline(IMM, color='green', linestyle='dashed', label='Computed IMM')
            
            # Extract the relevant parts from the name of the file
            name_parts = name.split("_")[:3]
            identifier = "_".join(name_parts)

            # Find the corresponding row in auctions_main_updated
            row = auctions_main_updated[auctions_main_updated['identifier'] == identifier]

            if not row.empty:
                real_IMM = row['IMM'].values[0]
                print("Real IMM: ", real_IMM)
                plt.axvline(real_IMM, color='orange', linestyle='solid', label='Real IMM')

                # Compare the computed IMM with the real one
                if computed_IMM is not None:
                    difference = computed_IMM - real_IMM
                    print("Difference: ", difference)

            name_parts = name.split("_")[:4]
            identifier = "_".join(name_parts)

            # Find the corresponding row in auctions_main_updated
            row = auctions_main_updated[auctions_main_updated['identifier'] == identifier]

            if not row.empty:
                real_IMM = row['IMM'].values[0]
                print("Real IMM: ", real_IMM)
                plt.axvline(real_IMM, color='orange', linestyle='solid', label='Real IMM')
                # Compare the computed IMM with the real one
                if computed_IMM is not None:
                    difference = computed_IMM - real_IMM
                    print("Difference: ", difference)

            plt.legend(handles=[Line2D([0], [0], marker='s', color='w', label='Offer', markerfacecolor=offer_color, markersize=11),
                    Line2D([0], [0], marker='s', color='w', label='Bid', markerfacecolor=bid_color, markersize=11), 
                    Line2D([0], [0], color='red', label='IMM', linestyle='solid'),
                    Line2D([0], [0], color='green', label='Computed IMM', linestyle='dashed'),
                    Line2D([0], [0], color='grey', linestyle='solid', label='Avg Bid and Offer')], loc='upper left')
            plt.subplots_adjust(top=0.9, bottom=0.05)  # Adjust the top and bottom spacing as desired
            plt.savefig(os.path.join(path_out_fig_first, "Initial_Market_Submissions", name + "_p.png"), format='png', bbox_inches='tight')
            plt.close()  # Close the current figure
   # The code is clearing the current figure to free up memory
    except Exception as e:
        print(f'An error occurred while processing {file} : {e}')
        with open('error_log.txt', 'a') as f:
            f.write(f'An error occurred while processing {file} : {e}\n')
        counter += 1
        if counter > 3:
            break
    continue
    


# ### Physical Settlement Requests and NOI

def size_signed(row):
    if row["Bid/Offer"] == "Bid":
        return -1 * row["Size"]
    else:
        return row["Size"]

for file in csv_files:
    if "Dealer,Bid/Offer,Size" in open(file).read() or "Bidder,Bid / Offer," in open(file).read():
        df = pd.read_csv(file)
        df = df.rename(columns={"Bid / Offer": "Bid/Offer", "Size / $ m": "Size", "Size / $m": "Size", "Bidder": "Dealer" })

        df["Size_signed"] = df.apply(size_signed, axis=1)
        computed_NOI = sum(df["Size_signed"])
        print("Computed NOI is " + str(computed_NOI))

        filename = os.path.basename(file)
        name, ext = os.path.splitext(filename)
        plt.figure(figsize=(18, 10))  # Set the figure size to 18x10
        #plt.suptitle(name)

        plt.scatter(df[df["Size_signed"] > 0]['Size_signed'], df[df["Size_signed"] > 0]['Dealer'], marker='s')
        plt.scatter(df[df["Size_signed"] < 0]['Size_signed'], df[df["Size_signed"] < 0]['Dealer'], marker='o')
        plt.scatter(df[df["Size_signed"] == 0]['Size_signed'], df[df["Size_signed"] == 0]['Dealer'], marker='x')
        plt.axvline(x=0, linestyle='--', color="darkgrey")

        plt.xlabel("Size signed")
        plt.ylabel("Dealer")
        plt.legend(["Flat", "Bid", "Offer"])  # Add legend

        plt.savefig(os.path.join(path_out_fig_first, "PSR", name + "_q.png"), format='png', bbox_inches='tight')
        plt.close()
            


# ### Limit Orders when NOI to Buy


## set up the directories

path_lo_fig =  os.path.join(path, "output/figures/second_stage/Limit_Orders_Graphs") #concatenates the path variable with the string "Limit Orders" and assigns it to the variable path_lo_fig.
#checks if the directory specified by path_lo_fig exists, and if it does not, it creates the directory using os.makedirs(path_lo_fig).
if not os.path.exists(path_lo_fig):
    os.makedirs(path_lo_fig)
# find all the csv files in the directory specified by path whose names contain the string "Limit Orders". 
csv_files = glob.glob(os.path.join(data_path, "*Limit Orders*.csv"))

## create colors for plots
# Create a color map for the dots
cmap = cm.get_cmap('tab20')  # Example using 'tab20' colormap# Set the number of colors you want
n_colors = 15
# sort the files by the first four characters of their filename
csv_files.sort(key=lambda x: int(os.path.basename(x)[:8]))


unique_dealers = set() # Create an empty set

## Create Limit Order Plots: left side by dealer and right side aggregate
for file in csv_files:
    try: #to handle errors
        if "Offer" in open(file).read(): # Open the file and check if the string "Offer" is present in the file's contents. If it is, the code continues to execute.
            print(file)
            df = pd.read_csv(file) # Read the csv file and assign it to a dataframe called df.
            df['Offer'] = df['Offer'].astype(str)
            df['Offer'] = df['Offer'].replace(to_replace='#', value='', regex=True) # Replacing the '#' character with nothing in the 'Offer' column.
            # Replace '*' character with an escaped version in the 'Dealer' column
            df['Dealer'] = df['Dealer'].str.replace(r'\*', '', regex=True)

            # Remove '*' and '**' characters from column names using regular expression pattern
            df.columns = [re.sub(r'\*{1,2}', '', col) for col in df.columns]
            df= df.dropna()
            df = df.reset_index(drop=True)

            df['Filled'] = 0
            df.loc[df['Offer'].str.contains('\^'), 'Filled'] = 1
            df.loc[df['Offer'].str.contains('\*') & (df['Filled'] == 0), 'Filled'] = 1
            df['Fully_Filled'] = 0
            df.loc[df['Offer'].str.contains('\*'), 'Fully_Filled'] = 1
            df['Part_Filled'] = 0
            df.loc[df['Offer'].str.contains('\^'), 'Part_Filled'] = 1

            df['Offer'] = df['Offer'].replace(to_replace='\^', value='', regex=True) # Replacing the '^' character with nothing in the 'Offer' column.
            df = df.replace(regex=r'\*|\*\*', value='') # Replacing the '*' and '**' characters with nothing in all columns of the dataframe.
            df['Offer'] = pd.to_numeric(df['Offer']) # Convert the 'Offer' column in df to a numeric data type.
            
            df_agg = df.groupby(['Dealer', 'Offer', 'Filled'])['Size'].sum().reset_index() # Create a new dataframe called df_agg that groups by 'Dealer', 'Offer', and 'Filled' columns and sums the 'Size' column.
            df_agg['CumulativeSize'] = df_agg.groupby(['Dealer'])['Size'].cumsum() # Add a new column 'CumulativeSize' to df_agg that is the cumulative sum of the 'Size' column grouped by 'Dealer'

            auction_outcome = df_agg[df_agg['Filled'] == 1]['Offer'].max() # Getting the final price of the auction by finding the minimum value in the 'Offer' column of the df_agg dataframe.
            dealers = df_agg.Dealer.unique() # Create a list of unique dealers
            unique_dealers.update(dealers) # Add the unique values to the set

            # Create a figure with 2 subplots, one for the dealer plots and one for the aggregate supply
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))
            filename = os.path.basename(file)
            name, ext = os.path.splitext(filename)  # Split the file name into name and extension parts and assign them to the variables name and ext respectively
            #fig.suptitle(name) # Set the title of the figure as the name of the file

            # Compute Cumulative Size and NOI
            df = df.sort_values(by='Offer', ascending=True) # Sort the dataframe by 'Offer' in ascending order
            df['CumulativeSize'] = df['Size'].cumsum() # Add a new column 'CumulativeSize' to df_supply that is the cumulative sum of the 'Size' column
            df = df.reset_index(drop=True)
            
            # Plot dealer's supply data on the left axes
            for i, dealer in enumerate(dealers):
                temp_df = df[df['Dealer'] == dealer].copy() # Create a new dataframe called temp_df that contains only the rows from df_agg that have the current dealer
                temp_df_agg = df_agg[df_agg['Dealer'] == dealer] # Create a new dataframe called temp_df that contains only the rows from df_agg that have the current dealer
                temp_df_agg = temp_df_agg.sort_values(by='Offer') # Sort the dataframe by 'Offer' in ascending order
                temp_df['CumulativeSize_byD'] = temp_df['Size'].cumsum() # Add a new column 'CumulativeSize' to df_supply that is the cumulative sum of the 'Size' column
                if len(temp_df_agg) < 2:  # If the number of rows in temp_df is less than 2, then it will plot the data as scatter plot
                    ax1.scatter(temp_df['Offer'],temp_df['CumulativeSize_byD'], color=cmap(i/n_colors), label = dealer)
                else:  # If the number of rows in temp_df is more than 2, then it will plot the data as line plot
                    ax1.step(temp_df['Offer'], temp_df['CumulativeSize_byD'], where='post', color=cmap(i/n_colors), label=dealer)
                ax2.scatter( temp_df['Offer'],temp_df['CumulativeSize'],color=cmap(i/n_colors), label = dealer)  # Plot the aggregate supply data on the right axes
            if df['Filled'].sum() == 0:
                ax1.set_title("No second stage Auction")
            else:
                ax1.set_title("Individual Limit Orders")
                ax1.axvline(auction_outcome, color='blue',  linestyle='dotted', linewidth=2, label="Auction Outcome") # Plot a horizontal line at the final price
            ax1.set_ylabel('Cumulative Size') # Set the x-axis label as 'Cumulative Size'
            ax1.set_xlabel('Offer') # Set the y-axis label as 'Offer'
            ax1.legend(loc = 'best', fontsize=7)  # Create a legend and set the location as 'best' and font size as 7
            
            ax2.set_title("Aggregate Supply")
            ax2.step(df['Offer'], df['CumulativeSize'], where='post', color='grey')  # Plot the aggregate supply data on the right axes using step function
            ax2.set_ylabel('Cumulative Size') # Set the x-axis label as 'Cumulative Size'
            ax2.axvline(auction_outcome, color='blue', linestyle='dotted', linewidth=2, label="Auction Outcome")
            ax2.set_xlabel('Offer')  # Set the y-axis label as 'Offer'
            
           # Split the filename by underscores
            name_parts = name.split('_')

            # If the filename has 4 parts, join the first 3 parts to form the identifier
            if len(name_parts) == 5:
                identifier = "_".join(name_parts[:3])
            # If the filename has more parts, join the first 4 parts to form the identifier
            elif len(name_parts) > 5:
                identifier = "_".join(name_parts[:4])
            # Otherwise, use the whole name as the identifier
            else:
                identifier = name

            # Find the corresponding row in auctions_main_updated
            row = auctions_main_updated[auctions_main_updated['identifier'] == identifier]

            if not row.empty:
                real_noi = row['noi_absolute_value'].values[0]/1000000  # Get the real NOI value from the row   
                print("Real NOI is " + str(real_noi) + " million" )
                ax2.axhline(real_noi, color='red', linestyle='dashed', label='NOI')  # Plot the real NOI line
                # Add the price_limit to the DataFrame
                price_floor = row['price_limit'].values[0]
                ax2.axvline(price_floor, color='brown', linestyle='dashdot', label='Price Limit')  # Plot the real NOI line
                real_final_price = row['final_price'].values[0]  # Get the real NOI value from the row   
                ax2.axvline(real_final_price, color='green', linestyle='dashed', label='Final Price')  # Plot the real NOI line
                imm = row['IMM'].values[0]  # Get the real NOI value from the row   
                ax2.axvline(imm, color='darkgrey', linestyle='dotted', label='IMM')  # Plot the real NOI line
            else:
                print("No corresponding NOI file found for identifier: " + identifier)
                
            # find the last offer fully filled and shade the second graph with a dark orange
            last_filled_offer = df[df['Fully_Filled'] == 1]['Offer'].max()
            ax2.fill_betweenx(df['CumulativeSize'], price_floor, last_filled_offer, color='darkorange', alpha=0.2)
            
            # if there are partially filled, find the last partially filled offer and shade with a light orange
            if df['Part_Filled'].sum() > 0:
                last_partial_offer = df[df['Part_Filled'] == 1]['Offer'].max()
                ax2.fill_betweenx(df['CumulativeSize'], last_filled_offer, last_partial_offer, color='yellow', alpha=0.2)
            # Your previous legends' handles and labels
            handles, labels = ax2.get_legend_handles_labels()
            # Create legend handles
            filled_patch = Patch(color='darkorange', label='Fully Filled Orders', alpha=0.2)
            partial_patch = Patch(color='yellow', label='Partially Filled Orders', alpha=0.2)

            # Combine them
            handles.extend([filled_patch, partial_patch])

            # And add them all to the legend
            ax2.legend(handles=handles, loc='best', fontsize=7) # Create a legend and set the location as 'best' and font size as 7
            # Saving the figure and displying it 
            plt.savefig(os.path.join(path_lo_fig, name + "Offer.png"), format='png', bbox_inches='tight') # The code is saving the figure in the path specified by the path_lo_fig variable and appending the name of the file with 'Offer.png' and format is set to png
            plt.close()   # The code is clearing the current figure to free up memory
    # Handling exceptions        
    except Exception as e:
        print(f'An error occurred while processing {file} at iteration {i} : {e}')
        with open('error_log.txt', 'a') as f:
            f.write(f'An error occurred while processing {file} at iteration {i} : {e}\n')
     # Handling any exceptions that may occur during the processing of the file by printing an error message and writing the error message to an 'error_log.txt' file. 


# ### Limit  orders when NOI to sell


## Create Auction to Sell Plots: left side by dealer and right side aggregate
for file in csv_files:
    try:
        if "Bid" in open(file).read():
            print(file)
            df = pd.read_csv(file)
            df['Bid'] = df['Bid'].astype(str)
            df['Bid'] = df['Bid'].replace(to_replace='#', value='', regex=True)
            # Replace '*' character with an escaped version in the 'Dealer' column
            df['Dealer'] = df['Dealer'].str.replace(r'\*', '', regex=True)

            # Remove '*' and '**' characters from column names using regular expression pattern
            df.columns = [re.sub(r'\*{1,2}', '', col) for col in df.columns]
            df= df.dropna()
            df = df.reset_index(drop=True)

            df['Filled'] = 0
            df.loc[df['Bid'].str.contains('\^'), 'Filled'] = 1
            df.loc[df['Bid'].str.contains('\*') & (df['Filled'] == 0), 'Filled'] = 1
            df['Fully_Filled'] = 0
            df.loc[df['Bid'].str.contains('\*'), 'Fully_Filled'] = 1
            df['Part_Filled'] = 0
            df.loc[df['Bid'].str.contains('\^'), 'Part_Filled'] = 1
            
            df['Bid'] = df['Bid'].replace(to_replace='\^', value='', regex=True)
            df = df.replace(regex=r'\*|\*\*', value='')
            df['Bid'] = pd.to_numeric(df['Bid'])
            
            df_agg = df.groupby(['Dealer', 'Bid', 'Filled'])['Size'].sum().reset_index()
            df_agg = df_agg.sort_values(by='Bid', ascending=False)
            df_agg['CumulativeSize'] = df_agg.groupby(['Dealer'])['Size'].cumsum()

            auction_outcome = df_agg[df_agg['Filled'] == 1]['Bid'].min()# Getting the final price of the auction by finding the msximum value in the 'Bid' column of the df_agg dataframe.
            dealers = df_agg.Dealer.unique() # Create a list of unique dealers
            unique_dealers.update(dealers) # Add the unique values to the set

            # Create a figure with 2 subplots, one for the dealer plots and one for the aggregate demand
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))
            filename = os.path.basename(file)
            name, ext = os.path.splitext(filename)  # Split the file name into name and extension parts and assign them to the variables name and ext respectively
            #fig.suptitle(name) # Set the title of the figure as the name of the file
            
            # Compute Cumulative Size and NOI
            df = df.sort_values(by='Bid', ascending=False) # Sort the dataframe by 'Bid' in ascending order
            df['CumulativeSize'] = df['Size'].cumsum() # Add a new column 'CumulativeSize' to df_supply that is the cumulative sum of the 'Size' column
            df = df.reset_index(drop=True)


            # Plot dealer's demand data on the left axes
            for i, dealer in enumerate(dealers):
                temp_df = df[df['Dealer'] == dealer].copy() # Create a new dataframe called temp_df that contains only the rows from df_agg that have the current dealer
                temp_df_agg = df_agg[df_agg['Dealer'] == dealer] # Create a new dataframe called temp_df that contains only the rows from df_agg that have the current dealer
                temp_df_agg = temp_df_agg.sort_values(by='Bid') # Sort the dataframe by 'Bid' in ascending order
                temp_df['CumulativeSize_byD'] = temp_df['Size'].cumsum() # Add a new column 'CumulativeSize' to df_demand that is the cumulative sum of the 'Size' column
                if len(temp_df_agg) < 2:  # If the number of rows in temp_df is less than 2, then it will plot the data as scatter plot
                    ax1.scatter(temp_df['Bid'],temp_df['CumulativeSize_byD'], color=cmap(i/n_colors), label = dealer)
                else:  # If the number of rows in temp_df is more than 2, then it will plot the data as line plot
                    ax1.step(temp_df['Bid'],temp_df['CumulativeSize_byD'],  where='post',color=cmap(i/n_colors), label = dealer)
                ax2.scatter(temp_df['Bid'],temp_df['CumulativeSize'], color=cmap(i/n_colors), label = dealer)  # Plot the aggregate demand data on the right axes    
            if df['Filled'].sum() == 0:
                ax1.set_title("No second stage Auction")
            else:
                ax1.set_title("Individual Limit Orders")
                ax1.axvline(auction_outcome, color='blue',  linestyle='dotted', linewidth=2, label="Auction Outcome") 
            ax1.set_ylabel('Cumulative Size') # Set the x-axis label as 'Cumulative Size'
            ax1.set_xlabel('Bid') # Set the y-axis label as 'Bid'
            ax1.legend(loc = 'best', fontsize=7)  # Create a legend and set the location as 'best' and font size as 7

            ax2.set_title("Aggregate Demand")
            ax2.step(df['Bid'], df['CumulativeSize'], where='post', color='grey')  # Plot the aggregate demand data on the right axes
            ax2.set_ylabel('Cumulative Size') # Set the x-axis label as 'Cumulative Size'
            ax2.axvline(auction_outcome, color='blue', linestyle='dotted', linewidth=2, label="Auction Outcome")
            ax2.set_xlabel('Bid')  # Set the y-axis label as 'Bid'
            # Split the filename by underscores
            name_parts = name.split('_')

            # If the filename has 4 parts, join the first 3 parts to form the identifier
            if len(name_parts) == 5:
                identifier = "_".join(name_parts[:3])
            # If the filename has more parts, join the first 4 parts to form the identifier
            elif len(name_parts) > 5:
                identifier = "_".join(name_parts[:4])
            # Otherwise, use the whole name as the identifier
            else:
                identifier = name

            # Find the corresponding row in auctions_main_updated
            row = auctions_main_updated[auctions_main_updated['identifier'] == identifier]

            if not row.empty:
                real_noi = row['noi_absolute_value'].values[0]/1000000  # Get the real NOI value from the row   
                print("Real NOI is " + str(real_noi) + " million" )
                ax2.axhline(real_noi, color='red', linestyle='dashed', label='NOI')  # Plot the real NOI line
                # Add the price_limit to the DataFrame
                price_cap = row['price_limit'].values[0]
                ax2.axvline(price_cap, color='brown', linestyle='dashdot', label='Price Limit')  # Plot the real NOI line
                real_final_price = row['final_price'].values[0]  # Get the real NOI value from the row   
                ax2.axvline(real_final_price, color='green', linestyle='dashed', label='Final Price')  # Plot the real NOI line
                imm = row['IMM'].values[0]  # Get the real NOI value from the row   
                ax2.axvline(imm, color='darkgrey', linestyle='dotted', label='IMM')  # Plot the real NOI line
            else:
                print("No corresponding NOI file found for identifier: " + identifier)
                
            # find the last bid fully filled and shade the second graph with a dark orange
            last_filled_bid = df[df['Fully_Filled'] == 1]['Bid'].min()
            ax2.fill_betweenx(df['CumulativeSize'], price_cap, last_filled_bid, color='darkorange', alpha=0.2)
            
            # if there are partially filled, find the last partially filled bids and shade with a light orange
            if df['Part_Filled'].sum() > 0:
                last_partial_bid = df[df['Part_Filled'] == 1]['Bid'].min()
                ax2.fill_betweenx(df['CumulativeSize'], last_filled_bid, last_partial_bid, color='yellow', alpha=0.2)
            # Your previous legends' handles and labels
            handles, labels = ax2.get_legend_handles_labels()
            # Create legend handles
            filled_patch = Patch(color='darkorange', label='Fully Filled Orders', alpha=0.2)
            partial_patch = Patch(color='yellow', label='Partially Filled Orders', alpha=0.2)

            # Combine them
            handles.extend([filled_patch, partial_patch])

            ax2.legend(handles=handles, loc='best', fontsize=7) # Create a legend and set the location as 'best' and font size as 7
            # Saving the figure and displying it 
            plt.savefig(os.path.join(path_lo_fig, name + "Bid.png"), format='png', bbox_inches='tight') # The code is saving the figure in the path specified by the path_lo_fig variable and appending the name of the file with 'Bid.png' and format is set to png
            plt.close()   # The code is clearing the current figure to free up memory
    # Handling exceptions        
    except Exception as e:
        print(f'An error occurred while processing {file} at iteration {i} : {e}')
        with open('error_log.txt', 'a') as f:
            f.write(f'An error occurred while processing {file} at iteration {i} : {e}\n')
     # Handling any exceptions that may occur during the processing of the file by printing an error message and writing the error message to an 'error_log.txt' file. 

