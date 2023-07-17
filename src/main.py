"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import argparse
import yaml
import os
import sys
import requests
import time
import aiohttp
import asyncio
import json
import pandas as pd
import numpy as np
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from ccxt import binance

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Private functions
async def get_crypto_price_prive(symbol:list) -> dict:
    """Get the price of input symbol"""
    ex = binance()
    ex.load_markets()
    crypto_quote = [quote.split("/")[0] for quote in ex.symbols if quote.endswith("/USDT")]
    query_crypto = [quote for quote in symbol if quote in crypto_quote]
    crypto_price = {}
    for quote in query_crypto:
        crypto_price[quote] = ex.fetch_ticker(quote+"/USDT")["last"]
    return crypto_price

async def get_stock_price_prive(symbol:list,api_key:str) -> dict:
    """Get the price of input symbol"""
    nasdaq_quote = pd.read_csv("https://datahub.io/core/nasdaq-listings/r/1.csv")["Symbol"].tolist()
    nyse_quote = pd.read_csv("https://datahub.io/core/nyse-other-listings/r/1.csv")["ACT Symbol"].tolist()
    query_sotck = [quote for quote in symbol if quote in nasdaq_quote or quote in nyse_quote]
    print(query_sotck)
    #get the price
    if len(query_sotck) > 0:
        stock_price = await get_stock_price(query_sotck,api_key)
    #combine the price and return
    return stock_price

async def get_stock_price(symbol:list,api_key:str) -> dict:
    """Get the price of stock"""
    query_url = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={}&apikey={}"
    stock_price = {}
    async with aiohttp.ClientSession() as session:
        tasks = []
        for quote in symbol:
            task = asyncio.ensure_future(fetch(session, query_url.format(quote,api_key)))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        
        for quote, response in zip(symbol, responses):
            data = json.loads(response)
            stock_price[quote] = data["Global Quote"]["05. price"]
    return stock_price

async def fetch(session:aiohttp.ClientSession, url:str) -> str:
    async with session.get(url) as response:
        return await response.text()

async def get_history_share_devide(symbol:list,api_key:str) -> dict:
    query_url = "https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={}&apikey={}"
    stock_info = {}
    devide_info = {}
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for quote in symbol:
            task = asyncio.ensure_future(fetch(session, query_url.format(quote,api_key)))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        
        for quote, response in zip(symbol, responses):
            data = json.loads(response)
            stock_info[quote] = data["Monthly Adjusted Time Series"]
        
    for quote in stock_info.keys():
        temp_data = {}
        for date in stock_info[quote].keys():
            year = date.split("-")[0]
            if year not in temp_data:
                temp_data[year] = 0
            temp_data[year] += float(stock_info[quote][date]["7. dividend amount"])
        devide_info[quote] = sum(list(temp_data.values())[1:6:])/5
    
    return devide_info

# Telegram bot commands functions
# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
🔰Commands
   /start - start the bot user guide
   /help - get help on how to use the bot
   /price - get the price of given stock
   /crypto - get the price of given crypto
   /devide - get the devide of given stock for the past 5 years
   /twse - get the best stocks in TWSE (It will take a while to get the result)
   /nasdaq - get the best stocks in Nasdaq (It will take a while to get the result)
   /nyse - get the best stocks in NYSE (It will take a while to get the result)
   /check - check the stock is good to buy or not
   /status - check the status of the bot

🌐Website
  ⚡[Alpaca](https://alpaca.markets/)⚡
  ⚡[Binance](https://www.binance.info/zh-TC/activity/referral-entry/CPA/incremental?ref=CPA_00JTV45LM5)⚡
  ⚡[Firstrade](https://www.firstrade.com/)⚡
  ⚡[MEXC](https://www.mexc.com/register?inviteCode=1fFm4)⚡
  ⚡[TD Ameritrade](https://www.tdameritrade.com/home.page)⚡
  
🪪Author
  ⚡[Github](https://www.github.com/hibana2077)⚡
  ⚡[Website](https://www.hibana2077.com)⚡
    """
    await update.message.reply_text(help_text, parse_mode="markdown")

async def twse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get the best stocks in TWSE"""
    STOCK_DAY_AVG_ALL = 'https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL'
    STOCK_DEVIDE = "https://openapi.twse.com.tw/v1/opendata/t187ap40_L"
    new_price = pd.read_json(STOCK_DAY_AVG_ALL)
    devide = pd.read_json(STOCK_DEVIDE)


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check the stock is good to buy or not"""
    print("check")
    symbols = update.message.text.split()[1:]
    api_key = ""
    with open('config.yaml', 'r') as yaml_file:api_key = yaml.load(yaml_file, Loader=yaml.FullLoader)["api_key"]
    stock_price = await get_stock_price(symbols,api_key)
    stock_devide = await get_history_share_devide(symbols,api_key)
    result_data = {}
    for symbol in symbols:
        result_data[symbol] = float(stock_price[symbol]) - (float(stock_devide[symbol])/0.05)
    result_data = sorted(result_data.items(), key=lambda x: x[1], reverse=True)
    result_text = "📊Check result\n"
    for data in result_data:
        result_text += f"*{data[0]}*:\t *Fair Value*: {float(stock_devide[data[0]])/0.05}, *Market Price*: {float(stock_price[data[0]])}, *Status*: {'Good to buy😊' if data[1] < 0 else 'Not good to buy😢'}\n"
    await update.message.reply_text(result_text, parse_mode="markdown")

async def get_nasdaq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get the Nasdaq stocks"""
    print("get_nasdaq")
    url = "https://datahub.io/core/nasdaq-listings/r/1.csv"
    df = pd.read_csv(url)
    symbols = df["Symbol"].tolist()
    api_key = ""
    with open('config.yaml', 'r') as yaml_file:api_key = yaml.load(yaml_file, Loader=yaml.FullLoader)["api_key"]
    stock_price = await get_stock_price(symbols,api_key)
    stock_devide = await get_history_share_devide(symbols,api_key)
    df["Price"] = df["Symbol"].map(stock_price)
    df["Devide"] = df["Symbol"].map(stock_devide)
    df["5percent"] = df["Devide"]/0.05
    df["is_good"] = df["5percent"] < df["Price"]
    df = df[df["is_good"] == True]
    df = df.sort_values(by=["price"] - ["5percent"], ascending=False)
    df:pd.DataFrame = df[["Symbol","Name","Price","Devide","5percent"]]
    df = df.head(10)
    text = "📈Nasdaq📈\n"
    for index, row in df.iterrows():
        text += f"*{row['Symbol']}*: price: {row['Price']}, devide: {row['Devide']:.4f}\n"
    await update.message.reply_text(text, parse_mode="markdown")

async def get_nyse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get the NYSE stocks"""
    url = "https://datahub.io/core/nyse-other-listings/r/1.csv"
    df = pd.read_csv(url)
    await update.message.reply_text("Function is not ready yet")

async def get_stock_devide(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get the devide of a stock"""
    symbols = update.message.text.split()[1:]
    api_key = ""
    with open('config.yaml', 'r') as yaml_file:api_key = yaml.load(yaml_file, Loader=yaml.FullLoader)["api_key"]
    devide = await get_history_share_devide(symbols,api_key)
    text = "💲Devide💲\n"
    for quote in devide:
        text += f"*{quote}*: {devide[quote]}\n"
    await update.message.reply_text(text, parse_mode="markdown")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def get_stock_price_pub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get the price of a stock"""
    #get the stock symbol
    symbol = update.message.text.split()[1:]
    #get the api_key from config.yaml
    api_key = ""
    with open('config.yaml', 'r') as yaml_file:api_key = yaml.load(yaml_file, Loader=yaml.FullLoader)["api_key"]
    #get the price
    price = await get_stock_price_prive(symbol,api_key)
    print(price)
    #make markdown text
    text = "💲Price💲\n"
    for quote in price:
        text += f"*{quote}*: _{price[quote]}_\n"
    await update.message.reply_text(text=text,parse_mode="markdown")

async def get_crypto_price_pub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get the price of a crypto"""
    #get the crypto symbol
    symbol = update.message.text.split()[1:]
    #get the price
    price = await get_crypto_price_prive(symbol)
    #make markdown text
    text = "💲Price💲\n"
    for quote in price:
        text += f"*{quote}*: _{price[quote]}_\n"
    await update.message.reply_text(text=text,parse_mode="markdown")

def main(token:str,api_key:str) -> None:
    """Start the bot."""
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    #check if config.yaml exists
    if not os.path.exists("config.yaml"):
        # save token and api_key to config.yaml
        config = {
            'token': token,
            'api_key': api_key
        }
        with open('config.yaml', 'w') as yaml_file:
            yaml.dump(config, yaml_file, default_flow_style=False)

    else:
        # replace token and api_key in config.yaml
        with open('config.yaml', 'r') as yaml_file:
            config = yaml.load(yaml_file, Loader=yaml.FullLoader)
        config['token'] = token
        config['api_key'] = api_key
        with open('config.yaml', 'w') as yaml_file:
            yaml.dump(config, yaml_file, default_flow_style=False)

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token=token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("price", get_stock_price_pub))
    application.add_handler(CommandHandler("crypto", get_crypto_price_pub))
    application.add_handler(CommandHandler("devide", get_stock_devide))
    application.add_handler(CommandHandler("nasdaq", get_nasdaq))
    application.add_handler(CommandHandler("nyse", get_nyse))
    application.add_handler(CommandHandler("check", check))
    application.add_handler(CommandHandler("twse", twse))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    #get arguments
    parser = argparse.ArgumentParser(description='Telegram bot for Stock Market')
    parser.add_argument('--token', type=str, help='Telegram bot token')
    parser.add_argument('--api_key', type=str, help='Alpha vantage api key')
    args = parser.parse_args()
    main(token=args.token,api_key=args.api_key)