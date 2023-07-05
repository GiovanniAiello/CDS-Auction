## Webscrape creditfixing.com

# Import necessary libraries
import csv # to save the data in csv format
import requests # to get the html source code of the page
from bs4 import BeautifulSoup # to parse the html source code
import pandas #
import os # to create directories
import shutil # to save the image
import pathlib # to create directories
from PIL import Image
import re
import glob
import pandas as pd
import dateparser
import operator


# Create a Session object to persist certain parameters across requests
session = requests.Session() 

# Define range of years for scraping
years_image = range(2005, 2010)
years_2005_2007 = range(2005, 2008)
post_2009_years  = range(2010, 2024)

# Define URLs for different year ranges
main_url = 'https://www.creditfixings.com{id}'
urlyears_2005_2007 = 'https://www.creditfixings.com/CreditEventAuctions/static/credit_event_auction/{year}.shtml'
url2008id = 'https://www.creditfixings.com/CreditEventAuctions/static/credit_event_auction/2008/{id}'
url2009id = 'https://www.creditfixings.com/CreditEventAuctions/static/credit_event_auction/{id}'
urlyears_post2009 = 'https://www.creditfixings.com/CreditEventAuctions/AuctionByYear.jsp?year={year}'
urlid = 'https://www.creditfixings.com/CreditEventAuctions/{id}'


# Define paths for saving scraped data
path_output_csv = os.getcwd() + "/data/raw_auction_csv"
path_output_img = os.getcwd() + "/data/raw_auction_image"


# Create directories if they do not exist
pathlib.Path(path_output_csv).mkdir(parents=True, exist_ok=True)
pathlib.Path(path_output_img).mkdir(parents=True, exist_ok=True)

# Create a list to store the auction information
auction_info = []

# Add Delphi auction info
# Replace 'auction_date', 'ticker', 'box_title', 'multiple_final_prices', 'final_price', 'IMM', 'NOI' with actual values
delphi_auction_info = ['20051104_delphi_CDS', 'Delphi', '4th November 2005', 'delphi', 'CDS', 'False', '63.375', '66', '$99 million to sell']
auction_info.append(delphi_auction_info)
dura_sub_auction_info = ['20061128_dura_subordinated_CDS', 'Dura Subordinated', '28th November 2006', 'dura_subordinated', 'CDS', 'False', '3.5', '4.5', '$77 million to sell']
auction_info.append(dura_sub_auction_info)
dana_auction_info = ['20060331_dana_corporation_CDS', 'Dana Corporation', '31st March 2006', 'dana_corporation', 'CDS', 'False', '75', '75.125', '$41 million to sell']
auction_info.append(dana_auction_info)
calpine_auction_info = ['20060117_calpine_CDS', 'Calpine', '17th January 2006', 'calpine', 'CDS', 'False', '19.125', '20', '$45 million to sell']
auction_info.append(calpine_auction_info)
NOVOBAN_Senior_auction_info = ['20181127_NOVOBAN_CDS-Senior','NOVO BCO SA (senior SRO transactions only)','27 November 2018','NOVOBAN','CDS-Senior','False','89.96','NA','NA']
auction_info.append(NOVOBAN_Senior_auction_info)
# Function to request and parse HTML by year
def reqpars_y(source, year):
    html = session.get(source.format(year=year)).text  # request the html by year
    soup = BeautifulSoup(html, "html.parser")
    return soup

# Function to request and parse HTML by id
def reqpars_id(source, id):
    html = session.get(source.format(id=id)).text  # request the html by year
    soup = BeautifulSoup(html, "html.parser")
    return soup



# Loop through each year in the first range (2005-2006) where there are images
for year in years_image:
    # Extract auction IDs for the year
    auctionIds = reqpars_y(urlyears_2005_2007, year).find_all("a", class_="standalonelink") 
    length = len(auctionIds)  # how many auction for each year
    for i in range(length):
        id = auctionIds[i]['href']  #  extract the link to each auction
        soup = reqpars_id(main_url, id)  # parse the html
        ticker = id.split(str(year) + "/", 1)[1][:-6]
        auction_text = auctionIds[i].text.strip()
        auction_name, date = auction_text.rsplit(" - ", 1)
      
        parsed_date = dateparser.parse(date).strftime("%Y%m%d")

        for idx, img_url in enumerate(soup.select('img[src^="/information/affiliations/fixings/20"]')):
            # requests to get the image content
            sc = requests.get(main_url.format(id=img_url['src']), stream=True)
            table_title = img_url.find_previous('h2').text
            # define the image saving path
            output_img = path_output_img + "/" + parsed_date + "_" + ticker +  "_CDS_" + str(table_title)[0:34] + "_" + str(idx) + img_url['src'][-4:]
            if sc.status_code == 200:
                # Open a local file with wb ( write binary ) permission.
                with open(output_img,'wb') as f:
                    shutil.copyfileobj(sc.raw, f)
            img = Image.open(output_img).convert('RGB')
            img.save(path_output_img + "/" + parsed_date + "_" + ticker +  "_CDS_" + str(table_title)[0:34]+ "_" + str(idx) +".jpg")

# specifying the path to csv files
path_converted_image = path_output_img + "/converted_csv"

# csv files in the path
files = glob.glob(path_converted_image + "/*jpg.csv")


# checking all the csv files in the
# specified path
for filename in files:
    # reading content of csv file
    # content.append(filename)
    df = pd.read_csv(filename, index_col=None)
    dataset = df.dropna(axis=1, how='all')
    dataset.columns = dataset.iloc[0]
    dataset = dataset[1:]
    filename = filename.replace("/Output_image", "/Output_csv")
    filename = filename.replace("-0-jpg", "")
    # Update the filename to the output CSV path
    output_filename = filename.replace(path_converted_image, path_output_csv)
    # Save the dataset as CSV
    dataset.to_csv(output_filename, index=False)


# Loop through each year in the second range (2006-2009)
for year in years_2005_2007:
    auctionIds = reqpars_y(urlyears_2005_2007, year).find_all("a", class_="standalonelink")  
    length = len(auctionIds)  # how many auction for each year
    for i in range(length):
        id = auctionIds[i]['href']  # now let's extract the link to each auction
        soup = reqpars_id(main_url, id)  # parse the html
        ticker = id.split(str(year) + "/", 1)[1][:-6]
        auction_text = auctionIds[i].text.strip()
        auction_name, date = auction_text.rsplit(" - ", 1)
        print(auction_name)
        print(date)
        parsed_date = dateparser.parse(date).strftime("%Y%m%d")

                # Add code here to scrape final price
        h_boxes_div = soup.find_all('div', class_='highlightbox')
        for span in h_boxes_div:
            if "Final Price" in span.text:
                try:
                    hbox_span = soup.find('span', class_='highlightbox')
                    final_price = hbox_span.find('span', class_='highlightvalue').text
                    box_title = "CDS"
                    if auction_name == "Movie Gallery":
                        box_title = "LCDS"
                    identifier = f"{parsed_date}_{ticker}_{box_title}"
                    multiple_final_prices = False
                    print(f"Identifier: {identifier}")
                    print(f"Final Price: {final_price}")
                except AttributeError:
                    print("Final price not found.")
                    final_price = "NA"
                output_csv = path_output_csv + "/" + parsed_date + "_" + ticker + "_" + box_title + "_" + "Final Price" + ".csv"
                with open(output_csv, 'w', newline='') as csvfile:
                    fieldnames = ['final_price']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerow({'final_price': final_price})
                
            #box_title_div = span.find_previous('div', class_='boxtitle')
            #if box_title_div:
            #    box_title = box_title_div.text.strip()
                # Scrape inside market midpoint (IMM)


            if "Inside Market Midpoint" in span.text:
                try:
                    inside_market_midpoint = span.find('span', class_='highlightvalue').text.strip()
                    print(f"Inside Market Midpoint: {inside_market_midpoint}")

                    # Save inside market midpoint to CSV
                    output_csv_imm = path_output_csv + "/" + parsed_date + "_" + ticker + "_" + box_title + "_" + "IMM.csv"
                    with open(output_csv_imm, 'w', newline='') as csvfile_imm:
                        fieldnames_imm = ['inside_market_midpoint']
                        writer_imm = csv.DictWriter(csvfile_imm, fieldnames=fieldnames_imm)
                        writer_imm.writeheader()
                        writer_imm.writerow({'inside_market_midpoint': inside_market_midpoint})

                except AttributeError:
                    print("Inside Market Midpoint not found.")

                        # Scrape net open interest (NOI)
            if "Net Open" in span.text:
                try:
                    net_open_interest = span.find('span', class_='highlightvalue').text.strip()
                    
                    print(f"Net Open Interest: {net_open_interest}")
                    auction_info.append([identifier, auction_name, date, ticker, box_title, multiple_final_prices, final_price, inside_market_midpoint, net_open_interest])
                    # Save net open interest to CSV
                    output_csv_noi = path_output_csv + "/" + parsed_date + "_" + ticker + "_" + box_title + "_" + "NOI.csv"
                    with open(output_csv_noi, 'w', newline='') as csvfile_noi:
                        fieldnames_noi = ['net_open_interest']
                        writer_noi = csv.DictWriter(csvfile_noi, fieldnames=fieldnames_noi)
                        writer_noi.writeheader()
                        writer_noi.writerow({'net_open_interest': net_open_interest})

                except AttributeError:
                    print("Net Open Interest not found.")

        for idx, table in enumerate(
                soup.find_all('table')):  # add the name of the company whose CDS are auctioned before each table
            temp = pandas.read_html(str(table))  # print all the table
            df = pandas.DataFrame(temp[0])  # title = str(year)+ " " +auction_name+str(idx)+".csv"
            table_title = table.find_previous('h2').text
            df.to_csv(path_output_csv + "/" + parsed_date + "_" + ticker + "_" + box_title + "_" +str(table_title)[0:34] + "_" + str(idx) + ".csv", index=False)
                    # Save final price to CSV



                     

year = 2008
auctionIds = reqpars_y(urlyears_2005_2007, year).find_all("span", class_="standalonelink")
length = len(auctionIds)  # how many auctions for each year

for i in range(length):
    id1 = auctionIds[i].find('a')['href']  # now let's extract the link to each auction
    auction_name = auctionIds[i].text.split(" - ")[0].strip()
    print(auction_name)
    date = auctionIds[i].text.split(" - ")[1].strip()
    print(date)
    parsed_date = dateparser.parse(date).strftime("%Y%m%d")
    results_elements = reqpars_id(main_url, id1).find_all("a", class_="standalonelink")
    # Find the element containing 'res' in its href attribute
    results = None
    for result in results_elements:
        href = result['href']
        if "res" in href:
            results = result
            break

    if results is None:
        result = results_elements[0]
        id2 = result['href'].replace("dis", "res")
    else:
        id2 = results['href'].replace("dis", "res")
    
    soup3 = reqpars_id(url2008id, id2.split(str(year) + "/", 1)[-1])
    ticker = id2.split(str(year) + "/", 1)[-1][:-10].replace('/', '_')

    # Scrape final price
    final_price = "NA"  # Default value for final price
    net_open_interest = "NA"  # Default value for net open interest
    inside_market_midpoint = "NA"  # Default value for inside market midpoint
    h_boxes_div = soup3.find_all('div', class_='highlightbox')
    final_price_boxes = [box for box in h_boxes_div if "Final Price" in box.text]
    multiple_final_prices = len(final_price_boxes) > 1
    if multiple_final_prices:
        print("Multiple Auctions")
    for span in h_boxes_div:
        if "Final Price" in span.text:
            try:
                final_price = span.find('span', class_='highlightvalue').text.strip()
            except AttributeError:
                print("Final price not found.")
                final_price = "NA"

            box_title_div = span.find_previous('div', class_='boxtitle')
            if box_title_div:
                box_title = box_title_div.text.strip()
                if not multiple_final_prices:
                    box_title = "CDS"
                if ticker.lower() in ['hawtel', 'masoni']:  # Add this line
                    box_title = "LCDS"  # And this line
                if not multiple_final_prices or box_title != auction_name:  
                    print(f"Box Title: {box_title}")
                    box_title = box_title.replace(" ", "-")  # Replace spaces with underscores
                    identifier = f"{parsed_date}_{ticker}_{box_title}"
                    print(f"Identifier: {identifier}")
                    print(f"Final Price: {final_price}")
            else:
                print("Box title not found.")
                box_title = "NA"

            # Save final price to CSV
            output_csv_final_price = path_output_csv + "/" + parsed_date + "_" + ticker + "_" + box_title + "_" + "Final Price.csv"
            with open(output_csv_final_price, 'w', newline='') as csvfile_final_price:
                fieldnames_final_price = ['final_price']
                writer_final_price = csv.DictWriter(csvfile_final_price, fieldnames=fieldnames_final_price)
                writer_final_price.writeheader()
                writer_final_price.writerow({'final_price': final_price})

            # Scrape net open interest (NOI)


        # Scrape inside market midpoint (IMM)
        if "Inside Market Midpoint" in span.text:
            try:
                inside_market_midpoint = span.find('span', class_='highlightvalue').text.strip()
                print(f"Inside Market Midpoint: {inside_market_midpoint}")

                # Save inside market midpoint to CSV
                output_csv_imm = path_output_csv + "/" + parsed_date + "_" + ticker + "_" + box_title + "_" + "IMM.csv"
                with open(output_csv_imm, 'w', newline='') as csvfile_imm:
                    fieldnames_imm = ['inside_market_midpoint']
                    writer_imm = csv.DictWriter(csvfile_imm, fieldnames=fieldnames_imm)
                    writer_imm.writeheader()
                    writer_imm.writerow({'inside_market_midpoint': inside_market_midpoint})

            except AttributeError:
                print("Inside Market Midpoint not found.")

        if "Net Open" in span.text:
            try:
                net_open_interest = span.find('span', class_='highlightvalue').text.strip()
                print(f"Net Open Interest: {net_open_interest}")
                auction_info.append([identifier, auction_name, date, ticker, box_title, multiple_final_prices, final_price, inside_market_midpoint, net_open_interest])
                # Save net open interest to CSV
                output_csv_noi = path_output_csv + "/" + parsed_date + "_" + ticker + "_" + box_title + "_" + "NOI.csv"
                with open(output_csv_noi, 'w', newline='') as csvfile_noi:
                    fieldnames_noi = ['net_open_interest']
                    writer_noi = csv.DictWriter(csvfile_noi, fieldnames=fieldnames_noi)
                    writer_noi.writeheader()
                    writer_noi.writerow({'net_open_interest': net_open_interest})

            except AttributeError:
                print("Net Open Interest not found.")

    for idx, table in enumerate(soup3.find_all('table')):
        temp = pandas.read_html(str(table))
        if not temp:
            continue
        df = pandas.DataFrame(temp[0])
        box_title_div = table.find_previous('div', class_='boxtitle')
        if box_title_div:
            box_title = box_title_div.text.strip()
            if not multiple_final_prices:
                box_title = "CDS"
            if not multiple_final_prices or box_title != auction_name:  
                box_title = box_title.replace(" ", "-")  # Replace spaces with underscores

        table_title = table.find_previous('h2').text

        # Create the CSV file title for tables
        csv_title = f"{parsed_date}_{ticker}_{box_title}_{table_title[:34]}_{idx}.csv"

        # Save the DataFrame to the CSV file
        df.to_csv(os.path.join(path_output_csv, csv_title), index=False)



year = 2009
auctionIds = reqpars_y(urlyears_2005_2007, year).find_all("span", class_="standalonelink")

length = len(auctionIds)
for i in range(length):
    id1 = auctionIds[i].find('a')['href']
    auction_name = auctionIds[i].text

    if "index" in id1: 
        id2 = id1.replace("index", "results")
    else:
        id2 = id1.rsplit('.', 1)[0] + "-res." + id1.rsplit('.', 1)[1]
    soup2 = reqpars_id(url2009id, id2)
    auction_name = auctionIds[i].text.split(" - ")[0].strip()
    print(auction_name)
    date = auctionIds[i].text.split(" - ")[1].strip()
    print(date)
    parsed_date = dateparser.parse(date).strftime("%Y%m%d")
    ticker = id2.split(str(year) + "/", 1)[1][:-14]
    
    # Scrape final prices
    h_boxes_div = soup2.find_all('div', class_='highlightbox')
    final_price_boxes = [box for box in h_boxes_div if "Final Price" in box.text]
    multiple_final_prices = len(final_price_boxes) > 1
    if multiple_final_prices:
        print("Multiple Auctions")
    for idx, span in enumerate(h_boxes_div):
        if "Final Price" in span.text:  # Check if "Final Price" label is present
            try:
                final_price = span.find('span', class_='highlightvalue').text.strip()
            except AttributeError:
                print("Final price not found.")
                final_price = "NA"

            box_title_div = span.find_previous('div', class_='boxtitle')
            if box_title_div:
                box_title = box_title_div.text.strip()
                if "Nortel" in box_title:
                    box_title = "CDS"
                elif box_title in ["Edscha", "Ferretti", "SSP"]:
                    box_title = "LCDS" 
                    print(f"Final Price: {final_price}")
                if not multiple_final_prices or box_title != auction_name:  
                    print(f"Box Title: {box_title}")
                    box_title = box_title.replace(" ", "-")  # Replace spaces with underscores
                    identifier = f"{parsed_date}_{ticker}_{box_title}"
                    print(f"Identifier: {identifier}")
                   
            else:
                print("Box title not found.")
                box_title = "NA"
                
            output_csv = path_output_csv + "/" + parsed_date + "_" + ticker + "_" + box_title + "_" + "Final Price" + ".csv"
            with open(output_csv, 'w', newline='') as csvfile:
                fieldnames = ['final_price']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow({'final_price': final_price})

        # Scrape Inside Market Midpoint values

        if "Inside Market Midpoint" in span.text:  # Check if "Inside Market Midpoint" label is present
            try:
                inside_market_midpoint = span.find('span', class_='highlightvalue').text.strip()
            except AttributeError:
                print("Inside Market Midpoint not found.")
                inside_market_midpoint = "NA"

            if not multiple_final_prices or box_title != auction_name:  
                print(f"Inside Market Midpoint: {inside_market_midpoint}")


            output_csv = path_output_csv + "/" + parsed_date + "_" + ticker + "_" + box_title + "_" + "IMM" + ".csv"
            with open(output_csv, 'w', newline='') as csvfile:
                fieldnames = ['inside_market_midpoint']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow({'inside_market_midpoint': inside_market_midpoint})

                # Scrape Net Open Interest values
        if "Net Open Interest" in span.text:  # Check if "Net Open Interest" label is present
            try:
                net_open_interest = span.find('span', class_='highlightvalue').text.strip()
            except AttributeError:
                print("Net Open Interest not found.")
                net_open_interest = "NA"
            if not multiple_final_prices or box_title != auction_name:  
                    print(f"Net Open Interest: {net_open_interest}")

            output_csv = path_output_csv + "/" + parsed_date + "_" + ticker + "_" + box_title + "_" + "NOI" + ".csv"
            with open(output_csv, 'w', newline='') as csvfile:
                fieldnames = ['net_open_interest']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow({'net_open_interest': net_open_interest})

            auction_info.append([identifier, auction_name, date, ticker, box_title, multiple_final_prices, final_price, inside_market_midpoint, net_open_interest])        

    for idx, table in enumerate(soup2.find_all('table')):
        temp = pandas.read_html(str(table))
        if not temp:
            continue
        df = pandas.DataFrame(temp[0])
        table_title = table.find_previous('h2').text
        
        # Get the previous box title
        box_title = table.find_previous('div', class_='boxtitle').text.strip()
        if "Nortel" in box_title:
            box_title = "CDS"
        elif box_title in ["Edscha", "Ferretti", "SSP"]:
            box_title = "LCDS" 
        box_title = box_title.replace(" ", "-")  # Replace spaces with underscores
        # Create the CSV file title
        csv_title = parsed_date + "_" + ticker + "_" + box_title + "_" + str(table_title)[:34]  + "_" + str(idx) + ".csv"
        
        # Save the DataFrame to the CSV file
        df.to_csv(path_output_csv + "/" + csv_title, index=False)


# For Japaneses Airline, CEMEX, FGIC, Aiful, McCarthy
year = 2010
auctionIds = reqpars_y(urlyears_post2009, year).select('a[href^="/information/affiliations/fixings/20"]')
length = len(auctionIds)

for i in range(length):
    id1 = auctionIds[i].get('href')
    auction_name = auctionIds[i].text.split("-")[0].strip()
    print(auction_name)
    date = auctionIds[i].text.split("-")[1].strip()
    print(date)
    soup2 = reqpars_id(main_url, id1)
    id2 = id1.replace("index", "results")
    soup3 = reqpars_id(main_url, id2)

    h_boxes_spans = soup3.find_all('span', class_='highlightbox')
    final_price_boxes = [box for box in h_boxes_spans if "Final Price" in box.text]
    multiple_final_prices = len(h_boxes_spans) > 1
    if multiple_final_prices:
        print("Multiple Auctions")
    
    # Scrape inside market midpoint
    inside_market_midpoints = []
    imm_spans = soup3.find_all('span', class_='highlightbox')
    for idx, span in enumerate(imm_spans):

        if "Inside Market Midpoint" in span.text:
            try:
                box_title_div = span.find_previous('div', class_='boxtitle')
                if box_title_div:
                    box_title = box_title_div.text.strip()
                    if box_title == "McCarthy and Stone":
                        box_title = "LCDS-LIEN1"

                    print(f"Box Title: {box_title}")
                inside_market_midpoint = span.find('span', class_='highlightvalue').text
                inside_market_midpoints.append(inside_market_midpoint)
                print(f"Inside Market Midpoint: {inside_market_midpoint}")
            except AttributeError:
                print("Inside Market Midpoint not found.")

        # Scrape net open interest
    net_open_interests = []
    noi_spans = soup3.find_all('span', class_='highlightbox')
    for idx, span in enumerate(noi_spans):
        if "Net Open Interest" in span.text:
            try:
                net_open_interest = span.find('span', class_='highlightvalue').text
                net_open_interests.append(net_open_interest)
                print(f"Net Open Interest: {net_open_interest}")
            except AttributeError:
                print("Net Open Interest not found.")

  # Scrape final price
    final_prices = []
    for idx, span in enumerate(h_boxes_spans):
        if "Final Price" in span.text:
            try:
                final_price = span.find('span', class_='highlightvalue').text
                final_prices.append(final_price)
                print(f"Final Price: {final_price}")
            except AttributeError:
                print("Final price not found.")

    ticker = id2.split(str(year) + "/", 1)[1][:-14]
    parsed_date = dateparser.parse(date).strftime("%Y%m%d")
    identifier = f"{parsed_date}_{ticker}_{box_title}"
    print(f"Identifier: {identifier}")
    auction_info.append([identifier, auction_name, date, ticker, box_title, multiple_final_prices, final_price, inside_market_midpoint, net_open_interest])

     #Scrape the tables

    for idx, table in enumerate(soup3.find_all('table')):
        temp = pandas.read_html(str(table))
        if temp == []:
            continue
        df = pandas.DataFrame(temp[0])
        table_title = table.find_previous('h2').text
        df.to_csv(
            path_output_csv + "/" + parsed_date + "_" + ticker + "_" + box_title + "_" + str(table_title)[0:34] + "_" + str(idx) + ".csv",
            index=False)

    # Save final price to CSV
    output_csv_final_price = path_output_csv + "/" + parsed_date +  "_" + ticker + "_" + box_title + "_" + "Final Price.csv"
    with open(output_csv_final_price, 'w', newline='') as csvfile_final_price:
        fieldnames_final_price = ['final_price']
        writer_final_price = csv.DictWriter(csvfile_final_price, fieldnames=fieldnames_final_price)
        writer_final_price.writeheader()
        writer_final_price.writerow({'final_price': final_price})
    # Save net open interest to CSV
    output_csv_noi = path_output_csv + "/" + parsed_date + "_" + ticker + "_" + box_title + "_" + "NOI.csv"
    with open(output_csv_noi, 'w', newline='') as csvfile_noi:
        fieldnames_noi = ['net_open_interest']
        writer_noi = csv.DictWriter(csvfile_noi, fieldnames=fieldnames_noi)
        writer_noi.writeheader()
        writer_noi.writerow({'net_open_interest': net_open_interest})
    # Save inside market midpoint to CSV
    output_csv_imm = path_output_csv + "/" + parsed_date + "_" + ticker + "_" + box_title + "_" + "IMM.csv"
    with open(output_csv_imm, 'w', newline='') as csvfile_imm:
        fieldnames_imm = ['inside_market_midpoint']
        writer_imm = csv.DictWriter(csvfile_imm, fieldnames=fieldnames_imm)
        writer_imm.writeheader()
        writer_imm.writerow({'inside_market_midpoint': inside_market_midpoint})

# Define a list of identifiers to be excluded
exclude_identifiers = ['20170914_NSINO_CDS-Bucket', '20170914_NSINO_CDS-Bucket-3', '20170914_NSINO_CDS-Bucket-4', '20160622_NSINO_CDS']

for year in post_2009_years:
    auctionIds = reqpars_y(urlyears_post2009, year).select('a[href^="holdings.jsp"]')
    length = len(auctionIds)
    for i in range(length):
        id1 = auctionIds[i].get('href')
        auction_text = auctionIds[i].text.strip()
        auction_name, date = auction_text.rsplit(" - ", 1)
        auction_name = auction_name.strip()
        print(auction_name)
        print(date)
        parsed_date = dateparser.parse(date).strftime("%Y%m%d")

        anchor = reqpars_id(urlid, id1).select('a[href^="results.jsp"]')
        if anchor == []:
            continue
        id2 = anchor[0].get('href')
        soup3 = reqpars_id(urlid, id2)
        ticker = id2.replace('results.jsp?ticker=', '').replace(' ', '').replace('.', '')

        # Scrape final prices
        h_boxes_div = soup3.find_all('div', class_='highlightbox')
        final_price_boxes = [box for box in h_boxes_div if "Final Price" in box.text]
        multiple_final_prices = len(final_price_boxes) > 1
        if multiple_final_prices:
            print("Multiple Auctions")

        initial_market_midpoint = "NA"  # Default value for initial market midpoint
        sanitized_box_title = "NA"  # Default value for sanitized box title
        net_open_interest = "NA"  # Default value for net open interest
        for idx, span in enumerate(h_boxes_div):
            if "Final Price" in span.text:
                try:
                    final_price = span.find('span', class_='highlightvalue').text.strip()
                except AttributeError:
                    print("Final price not found.")
                    final_price = "NA"

            if "Initial Market Midpoint" in span.text:
                try:
                    initial_market_midpoint = span.find('span', class_='highlightvalue').text.strip()

                        
                except AttributeError:
                    print("Initial Market Midpoint not found.")
            if "Net Open Interest" in span.text:  # Check if "Net Open Interest" label is present
                try:
                    net_open_interest = span.find('span', class_='highlightvalue').text.strip()  

                except AttributeError:
                    print("Net Open Interest not found.")
        
                
                box_title_div = span.find_previous('div', class_='boxtitle')
                if box_title_div:
                    box_title = box_title_div.text.strip()
                    if not multiple_final_prices or (box_title != auction_name):

                        box_title = box_title.replace('.', '').replace(',', '')
                        # Replace problematic characters in box title
                        sanitized_box_title = re.sub(r"/", "-or-", box_title)  # Remove special characters
                        sanitized_box_title = sanitized_box_title.replace(" ", "-")  # Replace spaces with underscores
                        print(f"Box Title: {box_title}")
                        print(f"Final Price: {final_price}")
                        print(f"Initial Market Midpoint: {initial_market_midpoint}")
                        print(f"Net Open Interest: {net_open_interest}")
                        identifier = f"{parsed_date}_{ticker}_{sanitized_box_title}"
                        print(f"Identifier: {identifier}")
                            # Check if identifier is in exclude_identifiers
                        if identifier in exclude_identifiers:
                            continue  # Skip to the next iteration
                        auction_info.append([identifier, auction_name, date, ticker, sanitized_box_title, multiple_final_prices, final_price, initial_market_midpoint, net_open_interest])
                        
        # Create sanitized file name for Final Price
        file_name_final_price = f"{parsed_date}_{ticker}_{sanitized_box_title} Final Price.csv"
        # Create the CSV file path for Final Price
        output_csv_final_price = os.path.join(path_output_csv, file_name_final_price)
        # Write the Final Price to the CSV file
        with open(output_csv_final_price, 'w', newline='') as csvfile_final_price:
            fieldnames_final_price = ['final_price']
            writer_final_price = csv.DictWriter(csvfile_final_price, fieldnames=fieldnames_final_price)
            writer_final_price.writeheader()
            writer_final_price.writerow({'final_price': final_price})
        
        # Create sanitized file name for NOI
        file_name_noi = f"{parsed_date}_{ticker}_{sanitized_box_title} NOI.csv"
        # Create the CSV file path for NOI
        output_csv_noi = os.path.join(path_output_csv, file_name_noi)
        # Write the NOI to the CSV file
        with open(output_csv_noi, 'w', newline='') as csvfile_noi:
            fieldnames_noi = ['net_open_interest']
            writer_noi = csv.DictWriter(csvfile_noi, fieldnames=fieldnames_noi)
            writer_noi.writeheader()
            writer_noi.writerow({'net_open_interest': net_open_interest})
        
        # Create sanitized file name for Initial Market Midpoint
        file_name_imm = f"{parsed_date}_{ticker}_{sanitized_box_title} IMM.csv"
        # Create the CSV file path for Initial Market Midpoint
        output_csv_imm = os.path.join(path_output_csv, file_name_imm)
        # Write the Initial Market Midpoint to the CSV file
        with open(output_csv_imm, 'w', newline='') as csvfile_imm:
            fieldnames_imm = ['initial_market_midpoint']
            writer_imm = csv.DictWriter(csvfile_imm, fieldnames=fieldnames_imm)
            writer_imm.writeheader()
            writer_imm.writerow({'initial_market_midpoint': initial_market_midpoint})

        for idx, table in enumerate(soup3.find_all('table')):
            temp = pandas.read_html(str(table))
            if not temp:
                continue
            df = pandas.DataFrame(temp[0])
            table_title = table.find_previous('h2').text
            # Get the previous box title
            box_title_div = table.find_previous('div', class_='boxtitle')
            if box_title_div:
                box_title = box_title_div.text.strip()
                box_title = box_title.replace('.', '').replace(',', '')
                if not multiple_final_prices or box_title != auction_name:
                    # Create the CSV file title for tables
                    sanitized_box_title = re.sub(r"/", "-or-", box_title)  # Remove special characters
                    sanitized_box_title = sanitized_box_title.replace(" ", "-")  # Replace spaces with underscores
                    csv_title = f"{parsed_date}_{ticker}_{sanitized_box_title}_{table_title[:34]}_{idx}.csv"
                    # Save the DataFrame to the CSV file
                    df.to_csv(os.path.join(path_output_csv, csv_title), index=False)

# Specify the file path and name
output_folder = "data/final_database"
os.makedirs(output_folder, exist_ok=True)
output_csv = os.path.join(output_folder, "auctions_main.csv")

auction_info = sorted(auction_info, key=lambda x: x[0])



# Filter the rows by excluding rows with the identifiers
auction_info = [row for row in auction_info if row[0] not in exclude_identifiers]


with open(output_csv, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['identifier', 'auction_name', 'date', 'ticker', 'box_title',  'multiple_final_prices', 'final_price','IMM', 'NOI'])

    for row in auction_info:
        writer.writerow(row)