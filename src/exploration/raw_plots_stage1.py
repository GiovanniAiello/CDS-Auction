# %% [markdown]
# ### Physical Settlement Requests and IMM

# %%
## import necessary libraries
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os
import glob
from matplotlib.lines import Line2D
import matplotlib.colors as mcolors # used for creating a color map for the dots
import re # used for regular expressions
from matplotlib.patches import Patch


# Set the default font size
matplotlib.rcParams.update({'font.size': 12})

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
            #plt.axvline(IMM, color='green', linestyle='dashed', label='Computed IMM')
            
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
                real_IMM = row['IMM'].values[0]
                print("Real IMM: ", real_IMM)
                plt.axvline(real_IMM, color='red', linestyle='solid', label='IMM')

                # Compare the computed IMM with the real one
                if computed_IMM is not None:
                    difference = computed_IMM - real_IMM
                    print("Difference: ", difference)



            plt.legend(handles=[Line2D([0], [0], marker='s', color='w', label='Offer', markerfacecolor=offer_color, markersize=11),
                    Line2D([0], [0], marker='s', color='w', label='Bid', markerfacecolor=bid_color, markersize=11), 
                    Line2D([0], [0], color='red', label='IMM', linestyle='solid'),
                    #Line2D([0], [0], color='brown', label='Computed IMM', linestyle='dashed'),
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

        # Separate the data based on the sign of Size_signed
        bid_data = df[df["Size_signed"] < 0]
        offer_data = df[df["Size_signed"] > 0]
        flat_data = df[df["Size_signed"] == 0]

        # Create the bar plots
        plt.barh(bid_data['Dealer'], bid_data['Size_signed'], color= bid_color, label= 'Bid')
        plt.barh(offer_data['Dealer'], offer_data['Size_signed'], color= offer_color, label= 'Offer')
        plt.barh(flat_data['Dealer'], flat_data['Size_signed'], color='green')
        #plt.scatter(flat_data['Dealer'], flat_data['Size_signed'], marker='x', color='green', label='Flat')

        plt.axvline(x=0, linestyle='--', color="darkgrey")

        plt.xlabel("Size signed")
        plt.ylabel("Dealer")
        legend_handles = [
            plt.Rectangle((0, 0), 1, 1, color=bid_color),
            plt.Rectangle((0, 0), 1, 1, color=offer_color)
        ]
        legend_labels = ['Bid', 'Offer']
        plt.legend(legend_handles, legend_labels)


        plt.savefig(os.path.join(path_out_fig_first, "PSR", name + "_q.png"), format='png', bbox_inches='tight')
        plt.close()
            
