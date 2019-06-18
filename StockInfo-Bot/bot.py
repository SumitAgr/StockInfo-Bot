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
from datetime import datetime, timedelta
import time
from pytz import timezone

# Adding EST timezone
est_timezone = timezone('US/Eastern')

# Importing OS library to read/write files
import os

# Creating Pandas DataFrame
nasdaq = pd.read_csv('nasdaq-listed-symbols.csv')

# Assigning a variable to the Symbol column in the DataFrame
nasdaq_list = nasdaq.Symbol.values

subreddits = 'wallstreetbets+investing+SecurityAnalysis+InvestmentClub+RobinHood+StockMarket+Stock_Picks+Forex+options+stocks\
              +pennystocks+finance+algotrading+CFA+1kRobinHoodProject+tastytrade+bitcoinhistory+ValueInvesting+Shorting+\
              forexbets+FinancialCareers+optionstrading+quant+TradingEducation+daytraders+ONCS+digitalcoin+passiveincome+\
              foreignpolicyanalysis+SHMPstreetbets+AMD_Stock+thewallstreet+RobinHoodPennyStocks'
             
ignored_subreddits = ["wallstreetbets", "personalfinance", "weedstocks", "resumes", "sysadmin", "DestinyTheGame", "PowerShell",\
                      "RealTesla", "linuxquestions"]

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
                        daily = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={config.av_apikey}"
                        daily_data = pd.DataFrame(requests.get(daily).json()['Time Series (Daily)']).T
                        price = daily_data['4. close'][0]
                        
                        weekly = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={symbol}&apikey={config.av_apikey}"
                        weekly_data = pd.DataFrame(requests.get(weekly).json()['Weekly Time Series']).T
                        weekly_data_high = weekly_data['2. high'][1]
                        weekly_data_low = weekly_data['3. low'][1]
                        
                        monthly = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={symbol}&apikey={config.av_apikey}"
                        monthly_data = pd.DataFrame(requests.get(monthly).json()['Monthly Time Series']).T
                        monthly_data_high = monthly_data['2. high'][1]
                        monthly_data_low = monthly_data['3. low'][1]
                        
                        valid_av_data = True
                        
                        if valid_av_data:
                            continue
                    except:
                        print("Too many Alpha Vantage API Calls! Sleeping for two minutes")
                        time.sleep(120)
                
                # Gettin company name data from the DataFrame
                company_name = nasdaq.loc[nasdaq['Symbol'] == symbol, 'Company Name'].iloc[0]
                
                valid_bc_data = False
                
                # While loop to get barchart data until there's no error
                while not valid_bc_data:
                    try:
                        bc_url = f"https://marketdata.websol.barchart.com/getQuote.csv?apikey={config.bc_apikey}&symbols={symbol}&fields=fiftyTwoWkHigh%2CfiftyTwoWkHighDate%2CfiftyTwoWkLow%2CfiftyTwoWkLowDate"
                        bc_df = pd.read_csv(bc_url)
                        fiftytwo_wk_low = bc_df["fiftyTwoWkLow"].iloc[0]
                        fiftytwo_wk_high = bc_df["fiftyTwoWkHigh"].iloc[0]
                        valid_bc_data = True
                        
                        if valid_bc_data:
                            continue
                    except:
                        print("Too many Barchart API Calls! Sleeping for a minute")
                        time.sleep(60)
               
                # Appending comment.id to the txt file
                comments_replied_to.append(comment.id)
                
                # Writing the comment.id to the txt file
                with open ("replied_comments.txt", "a") as file:
                    file.write(comment.id + "\n")
                    
                # Declaring US/Eastern timezone
                est_time = datetime.now(est_timezone)
                
                # Logic to get last month's name
                last_month_name = (pd.Period(datetime.now(), 'M') - 1).strftime('%B %Y')
                
                # Logic to get last friday's date
                now = datetime.now()
                closest_friday = now + timedelta(days = (4 - now.weekday()))
                last_friday = closest_friday if closest_friday < now else closest_friday - timedelta(days = 7)
                
                # Defining the variables to show in our comment reply
                stock_info = f"The last price for {company_name} (Nasdaq: {symbol}) was **${float(price):.2f}**"
                high_low_info = f"\n\n The 52 week high is **${fiftytwo_wk_high}** and 52 week low is **${fiftytwo_wk_low}**"
                price_action_info = "\n\n Price action (weekly and monthly):"
                weekly_info = f"\n\n **Weekly:** {symbol} made a weekly high of **${float(weekly_data_high):.2f}** and a low of **${float(weekly_data_low):.2f}** (for the week ending on {last_friday.strftime('%b %d, %Y')})"
                monthly_info = f"\n\n **Monthly:** {symbol} made a monthly high of **${float(monthly_data_high):.2f}** and a low of **${float(monthly_data_low):.2f}** (for the month of {last_month_name})"
                time_info = f" (as of {est_time.strftime('%I:%M %p EST on %b %d, %Y')})"
                bot_info = "\n\n ^^I ^^am ^^a ^^new ^^bot ^^and ^^I'm ^^still ^^improving, ^^you ^^can ^^provide ^^feedback ^^and ^^suggestions ^^by ^^DMing ^^me!"
                full_comment = f"{stock_info} {time_info} {high_low_info} {price_action_info} {weekly_info} {monthly_info} {bot_info}"
                
                # Replying to the comment on reddit
                comment.reply(full_comment)
                
                # Print statements for debugging
                print(f"Replied to author {comment.author} and comment {comment.id}")
                print(stock_info + time_info + high_low_info)
                print(f"Full path - {comment.permalink}")
                
                # Sleeping for 60 seconds to limit 5 API Calls per minute
                print("Sleeping for 60 seconds to limit 5 API Calls per minute...")
                time.sleep(60)
                
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
        print("\n", datetime.now())
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
