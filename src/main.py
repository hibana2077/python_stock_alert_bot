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
import pandas as pd
import numpy as np
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from ccxt import binance, bybit

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


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
   /price - get the price of a stock
🌐Website
  ⚡[Firstrade](https://www.firstrade.com/)⚡
  ⚡[Alpaca](https://alpaca.markets/)⚡
  ⚡[TD Ameritrade](https://www.tdameritrade.com/home.page)⚡
    """
    await update.message.reply_text(help_text, parse_mode="markdown")

async def get_nasdaq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get the Nasdaq stocks"""
    url = "https://datahub.io/core/nasdaq-listings/r/1.csv"
    df = pd.read_csv(url)

async def get_nyse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get the NYSE stocks"""
    url = "https://datahub.io/core/nyse-other-listings/r/1.csv"
    df = pd.read_csv(url)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get the price of a stock"""
    #get the stock symbol
    symbol = update.message.text.split()[1:]
    #get the price
    print(symbol)
    await update.message.reply_text("*TEST*",parse_mode="markdown")

def main(token:str,api_key:str) -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token=token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("price", get_price))

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