<h3 align="center">Stock Info Bot for Reddit</h3>

<p align="center">
  <a href="" rel="noopener">
 <img src="https://i.imgur.com/FWRhIcJ.png" alt="Bot logo" height = "100" weight = "100"></a>
</p>

<p align="center"> 🤖 A reddit bot that displays the last closing price information of a stock. Simply enter: $(stock ticker) and the bot will reply to you with the name of the company, closing price, 52 week high and low prices, weekly high and low, monthly high and low prices and the P/E ratio.
    <br> 
</p>

## 📝 Table of Contents
+ [About](#about)
+ [How it works](#howitworks)
+ [Usage](#usage)
+ [Example](#example)
+ [Built Using](#built_using)
+ [Author](#author)
+ [License](#license)
+ [Acknowledgments](#acknowledgement)

## 🧐 About <a name = "about"></a>
A convenient bot that displays a snippet of a stock by showing the full name of the company, last closing price (latest) and the 52 week high and 52 week low price, weekly high and low, monthly high and low prices.

Stock Info Bot uses the Alpha Vantage API for the closing price, weekly and monthly prices and Barchart API for 52 week prices. It uses Google Finance data to get the P/E ratio data.

The bot is running on Ubuntu 16.04 which is hosted on Amazon's AWS EC2. The reddit comment data is stored on Amazon's DynamoDB.

## 💭 How it works <a name = "howitworks"></a>

The bot first connects to reddit by logging in with the login credentials and reddit's client id and client secret. After successfully authenticating the bot, it scans all of reddit's comments to search for the keyword $(stock ticker) and whenever it finds it, it triggers the bot to reply. 

The bot searches for the ticker symbol in the Pandas Dataframe (converted from a csv file) and then returns the stock ticker and the corresponding name of the company. It then uses Alpha Vantage's realtime API to get closing price information and returns the last closing price and weekly and monthly prices. It also uses Barchart's API (delayed by 15 minutes) to return the stock's 52 week high and low prices. It scrapes Google Finance data and gets the P/E ratio. After getting all the information necessary to reply to the original user, Stock Info Bot replies to the comment in under a minute.

The comment information is saved to DynamoDB afterwards.

The entire bot is written in Python 3.7

## 🖋️ Usage <a name = "usage"></a>

To use the bot, type the following in a reddit comment box:
```
> $NVDA
```
There has to be a $ in front of the stock ticker, otherwise it will not work.

The bot will then swiftly reply.

### 📷 Example: <a name = "example"></a>

<p align="left">
  <a href="" rel="noopener">
 <img src="https://i.imgur.com/GhM884P.png" alt="Bot example for $TSLA"></a>
</p>

## ⛏️ Built Using <a name = "built_using"></a>
+ [PRAW](https://praw.readthedocs.io/en/latest/) - Reddit's Python wrapper
+ [Amazon AWS EC2](https://aws.amazon.com/ec2/) - Amazon AWS's cloud computing service
+ [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) - Amazon AWS's nonrelational database service
+ [Selenium](https://www.seleniumhq.org/) - Browser Automation Library
+ [Alpha Vantage API](https://www.alphavantage.co/) - Alpha Vantage's realtime API
+ [Barchart API](https://www.barchart.com/ondemand/api/getQuote) - Barchart's financial data API
+ [Pandas](https://pandas.pydata.org/) - Library for data manipulation and analysis
+ Requests - Library for HTTP requests
+ Time / DateTime / TimeDelta / PyTZ - Time libraries for time usage
+ OS - Library to read/write files

## ✍️ Author <a name = "author"></a>
+ Sumit Agrawal

## 📗 License <a name = "license"></a>
This project is licensed under the MIT License - see the LICENSE file for more details.

## 🎉 Acknowledgements <a name = "acknowledgement"></a>
+ Thank you to [Datahub](https://datahub.io/core/nasdaq-listings) for providing the NASDAQ listing data in a clean, readable format.
+ A big thank you to all the developers of the python libraries used in this bot.
