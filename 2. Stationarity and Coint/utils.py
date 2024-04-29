import lzma
import dill as pickle
import pandas as pd
import numpy as np


def save_pickle(path,obj):
    with lzma.open(path,"wb") as fp:
        pickle.dump(obj,fp)

def load_pickle(path):
    with lzma.open(path,"rb") as fp:
        file = pickle.load(fp)
    return file


def clean_data(ticker_dfs,tickers):
    intraday_range = ticker_dfs[tickers[0]].index
    for inst in tickers:
        ticker_dfs[inst] = ticker_dfs[inst].reindex(intraday_range)
    closes = []

    for tk in tickers:
        close = ticker_dfs[tk].close
        closes.append(close)

    pricing = pd.concat(closes,axis = 1)
    pricing.columns = tickers

    return pricing



def get_data(data_path,dfs_path):

    # data_path = "/content/drive/My Drive/constituents.csv"
    # dfs_path = "/content/drive/My Drive/new_dfs.obj"

    ticker_dfs = load_pickle(dfs_path)
    snp_data = pd.read_csv(data_path)
    tickers = []

    for i in range(499):
      tickers.append(snp_data.Symbol[i])

    tickers.remove("BF.B")
    tickers.remove("BRK.B")
    tickers.remove("CPAY")
    tickers.remove("DAY")
    tickers.remove("GEV")
    tickers.remove("SOLV")

    return tickers,ticker_dfs


