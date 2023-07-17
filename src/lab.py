'''
Author: hibana2077 hibana2077@gmail.com
Date: 2023-07-12 18:01:50
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2023-07-17 10:16:08
FilePath: \python_stock_alert_bot\src\lab.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# import pandas as pd

# df = pd.read_csv("https://datahub.io/core/nasdaq-listings/r/1.csv")
# symbols = df["Symbol"].tolist()
# print(f"symbols type: {type(symbols)} , symbols length: {len(symbols)}")
# from ccxt import binance
# ex = binance()
# ex.load_markets()
# print([quote.split("/")[0] for quote in ex.symbols if quote.endswith("/USDT")])
import pandas as pd

STOCK_DAY_AVG_ALL = 'https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL'
STOCK_DEVIDE = "https://openapi.twse.com.tw/v1/opendata/t187ap40_L"
new_price = pd.read_json(STOCK_DAY_AVG_ALL)
devide = pd.read_json(STOCK_DEVIDE)

print(new_price.columns)
print(devide.columns)

print(new_price.head())
print(devide["出表日期"].head())
