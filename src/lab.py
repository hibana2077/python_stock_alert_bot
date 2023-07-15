# import pandas as pd

# df = pd.read_csv("https://datahub.io/core/nasdaq-listings/r/1.csv")
# symbols = df["Symbol"].tolist()
# print(f"symbols type: {type(symbols)} , symbols length: {len(symbols)}")
# from ccxt import binance
# ex = binance()
# ex.load_markets()
# print([quote.split("/")[0] for quote in ex.symbols if quote.endswith("/USDT")])
dict1 = {"2021":15,"2022":20,"2023":25}
print(dict1.values().tolist())