# -*- coding: utf-8 -*-
# Importing Reddit library and Error handlers
import praw
from praw.exceptions import APIException
import prawcore

# Importing config file with information
import config

# Importing pandas for data manipulation
import pandas as pd

# Importing requests library for HTTP requests
import requests

# Importing datetime library for debugging and time libraries for displaying time
from datetime import datetime, timedelta, date
import time
from pytz import timezone

# Adding EST timezone
est_timezone = timezone('US/Eastern')

# Importing OS library to read/write files
import os

# Importing Boto3 to communicate with Amazon DynamoDB
import boto3

<<<<<<< HEAD
=======
# Libraries to start headless Firefox browser on the virtual machine
>>>>>>> origin
from pyvirtualdisplay import Display
from selenium import webdriver

display = Display(visible=0, size=(800, 600))
display.start()
browser = webdriver.Firefox()

session = boto3.Session(
    aws_access_key_id = config.aws_access_key,
    aws_secret_access_key = config.aws_secret_access_key,
    region_name = config.region_name
)

dynamodb = session.resource('dynamodb')
table = dynamodb.Table('StockInfoBot')

# Creating Pandas DataFrame
nasdaq = pd.read_csv('nasdaq-listed-symbols.csv')

# Assigning a variable to the Symbol column in the DataFrame
nasdaq_list = nasdaq.Symbol.values

# subreddits = 'wallstreetbets+investing+SecurityAnalysis+InvestmentClub+RobinHood+StockMarket+Stock_Picks+Forex+options+stocks\
#               +pennystocks+finance+algotrading+CFA+1kRobinHoodProject+tastytrade+bitcoinhistory+ValueInvesting+Shorting+\
#               forexbets+FinancialCareers+optionstrading+quant+TradingEducation+daytraders+ONCS+digitalcoin+passiveincome+\
#               foreignpolicyanalysis+SHMPstreetbets+AMD_Stock+thewallstreet+RobinHoodPennyStocks'
             
ignored_subreddits = ["wallstreetbets", "personalfinance", "weedstocks", "resumes", "sysadmin", "DestinyTheGame", "PowerShell",\
                      "RealTesla", "linuxquestions", "stocks", "zsh", "linuxmasterrace", "communism101", "thewallstreet",\
                      "AskReddit"]

# Creating login function for PRAW
def bot_login():
    bot_login_info = praw.Reddit(username = config.username,
                password = config.password,
                client_id = config.client_id,
                client_secret = config.client_secret,
                user_agent = config.user_agent)
    
    print(f"Successfully logged in the bot as {bot_login_info.user.me()}")
    
    return bot_login_info

# Creating function to run bot and reply to comments
def run_bot(bot_login_info, comments_replied_to):
    
    print("Running the bot and getting the latest comments...")
    
    for comment in bot_login_info.subreddit('all').comments(limit = None):
        
        for symbol in nasdaq_list:
            stock_comment = f"${symbol}"
            if stock_comment in comment.body and comment.id not in comments_replied_to and comment.author != config.username and comment.subreddit not in ignored_subreddits:
                
                # Defining the url to get data from and creating a DataFrame and then extracting price and company name
                valid_av_data = False
                
                # While loop to get Alpha Vantage data until there's no error
                while not valid_av_data:
                    try:
                        # daily = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={config.av_apikey}"
                        # daily_data = pd.DataFrame(requests.get(daily).json()['Time Series (Daily)']).T
                        # price = daily_data['4. close'][0]
                        
                        # print("Sleeping after first loop for 5 seconds")
                        # time.sleep(5)
                        
                        weekly = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={symbol}&apikey={config.av_apikey}"
                        weekly_data = pd.DataFrame(requests.get(weekly).json()['Weekly Time Series']).T
                        weekly_data_high = weekly_data['2. high'][1]
                        weekly_data_low = weekly_data['3. low'][1]
                        
                        # print("Sleeping after second loop for 5 seconds")
                        # time.sleep(5)
                        
                        monthly = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={symbol}&apikey={config.av_apikey}"
                        monthly_data = pd.DataFrame(requests.get(monthly).json()['Monthly Time Series']).T
                        monthly_data_high = monthly_data['2. high'][1]
                        monthly_data_low = monthly_data['3. low'][1]
                        
                        valid_av_data = True
                        
                        if valid_av_data:
                            continue
                    except Exception as e:
                        print(f"Error occured: {e} Sleeping for two minutes")
                        time.sleep(120)
                
                valid_bc_data = False
                
                # While loop to get barchart data until there's no error
                while not valid_bc_data:
                    try:
                        bc_url = f"https://marketdata.websol.barchart.com/getQuote.csv?apikey={config.bc_apikey}&symbols={symbol}&fields=fiftyTwoWkHigh%2CfiftyTwoWkLow%2ClastPrice%2CfiftyTwoWkHighDate%2CfiftyTwoWkLowDate"
                        bc_df = pd.read_csv(bc_url)
                        fiftytwo_wk_low = bc_df["fiftyTwoWkLow"].iloc[0]
                        fiftytwo_wk_low_date = bc_df["fiftyTwoWkLowDate"].iloc[0]
                        fiftytwo_wk_high = bc_df["fiftyTwoWkHigh"].iloc[0]
                        fiftytwo_wk_high_date = bc_df["fiftyTwoWkHighDate"].iloc[0]
                        last_price = bc_df["lastPrice"].iloc[0]

                        valid_bc_data = True
                        
                        if valid_bc_data:
                            continue
                    except Exception as e:
                        print(f"Error occured: {e} Sleeping for a minute")
                        time.sleep(60)
               
                # Appending comment.id to the txt file
                comments_replied_to.append(comment.id)
                
                # Writing the comment.id to the txt file
                with open ("replied_comments.txt", "a") as file:
                    file.write(comment.id + "\n")

                # Gettin company name data from the DataFrame
                company_name = nasdaq.loc[nasdaq['Symbol'] == symbol, 'Company Name'].iloc[0]

                # Declaring US/Eastern timezone
                est_time = datetime.now(est_timezone)
                
                # Logic to get last month's name
                last_month_name = (pd.Period(datetime.now(), 'M') - 1).strftime('%B %Y')
                
                # Logic to get last friday's date
                now = datetime.now()
                closest_friday = now + timedelta(days = (4 - now.weekday()))
                last_friday = closest_friday if closest_friday < now else closest_friday - timedelta(days = 7)

                # Get 52wk high and low dates and split them to get individual integers
                low_date = fiftytwo_wk_low_date.split('-')
                high_date = fiftytwo_wk_high_date.split('-') 

                # Convert integers into readable, displayable text by using strftime module
                low_date_display = date(day = int(low_date[2]), month = int(low_date[1]), year = int(low_date[0])).strftime('on %b %d, %Y')
                high_date_display = date(day = int(high_date[2]), month = int(high_date[1]), year = int(high_date[0])).strftime('on %b %d, %Y')

                # Getting P/E ratio from Google Finance
                try:
                    browser.get(f'https://www.google.com/search?q={symbol}')
                    pe_ratio_finder = browser.find_element_by_css_selector('#knowledge-finance-wholepage__entity-summary > div > div > g-card-section:nth-child(2) > div > div > div:nth-child(1) > table > tbody > tr:nth-child(5) > td.iyjjgb').text
                except:
                    pe_ratio_finder = '-'

                # Reddit comment variables
                headline = f"{company_name} (Nasdaq: {symbol})"
                columns = f"Timeframe | {symbol} | Date and Time"
                divider = "---|---|---"
                last_price = f"Last Price | ${float(last_price):.2f} | as of {est_time.strftime('%I:%M %p EST on %b %d, %Y')}"
                week_high = f"1-wk High | ${float(weekly_data_high):.2f} | for the week ending on {last_friday.strftime('%b %d, %Y')}"
                week_low = f"1-wk Low | ${float(weekly_data_low):.2f} | "
                month_high = f"1-mnth High | ${float(monthly_data_high):.2f} | for the month of {last_month_name}"
                month_low = f"1-mnth Low | ${float(monthly_data_low):.2f} | "
                fivetwo_high = f"52-wk High | ${fiftytwo_wk_high} | {high_date_display}"
                fivetwo_low = f"52-wk Low | ${fiftytwo_wk_low} | {low_date_display}"
                pe_ratio = f"P/E ratio |   {pe_ratio_finder} | "
                bot_info = "^^I ^^am ^^a ^^new ^^bot ^^and ^^I'm ^^still ^^improving, ^^you ^^can ^^provide ^^feedback ^^and ^^suggestions ^^by ^^DMing ^^me!"
                full_comment = f"{headline} \n\n {columns} \n {divider} \n {last_price} \n {week_high} \n {week_low} \n {month_high} \n {month_low} \n {fivetwo_high} \n {fivetwo_low} \n {pe_ratio} \n\n {bot_info}"

                # Replying to the comment on reddit
                comment.reply(full_comment)

                # Print statements for debugging
                print(f"Replied to author {comment.author} and comment {comment.id}")
                #print(stock_info + time_info + high_low_info)
                print(f"Full path - {comment.permalink}")

                # Inserting data into Amazon DynamoDB
                insert_into_db = table.put_item(
                    Item = {
                        'Time': f"{est_time.strftime('%Y-%m-%d %H:%M:%S')}",
                        'Author': f"{comment.author}",
                        'Stock': f"{symbol}",
                        'Company Name': f"{company_name}",
                        'Comment': f"{comment.permalink}"
                    }
                )
                
                print(insert_into_db)

                # Sleeping for 20 seconds to limit 5 API Calls per minute
                print("Sleeping for 20 seconds to limit 5 API Calls per minute...")
                time.sleep(20)
                
# Creating comment saving function
def get_replied_comments():
    # Creating a list if txt file is unavailable else reading the txt file
    if not os.path.isfile("replied_comments.txt"):
        replied_comments = []
    else:
        with open("replied_comments.txt", "r") as file:
            replied_comments = file.read()
            replied_comments = replied_comments.split("\n")
    
    return replied_comments

# Assigning a variable to the get_replied_comments() function
comments_replied_to = get_replied_comments()

# While loop to continuosly run the run_bot function
while True:
    try:
        est_time = datetime.now(est_timezone)
        print("\n", est_time.strftime('%I:%M:%S %p'))
        run_bot(bot_login(), comments_replied_to)
    except APIException:
        print("PRAW API Exception was raised! Sleeping for 10 minutes")
        time.sleep(600)
    except prawcore.exceptions.Forbidden:
        print("PRAW 403 HTTP RESPONSE occured! Sleeping for 10 minutes")
        time.sleep(600)
    except prawcore.ResponseException:
        print("PRAW 503 HTTP REsponse! SLeeping for a minute...")
        time.sleep(60)
