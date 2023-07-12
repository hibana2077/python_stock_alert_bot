# import pandas as pd

# df = pd.read_csv("https://datahub.io/core/nasdaq-listings/r/1.csv")
# symbols = df["Symbol"].tolist()
# print(f"symbols type: {type(symbols)} , symbols length: {len(symbols)}")
# from ccxt import binance
# ex = binance()
# ex.load_markets()
# print([quote.split("/")[0] for quote in ex.symbols if quote.endswith("/USDT")])
d1 = {"a":1,"b":2}
d2 = {"c":3,"d":4}
c3 = {**d1,**d2}
print(c3)