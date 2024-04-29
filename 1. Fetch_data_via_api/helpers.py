import lzma
import dill as pickle
import requests
import pandas as pd
from datetime import datetime
from time import sleep


def save_pickle(path,obj):
    with lzma.open(path,"wb") as fp:
        pickle.dump(obj,fp)

def load_pickle(path):
    try:
        with lzma.open(path, "rb") as fp:
            return pickle.load(fp)
    except FileNotFoundError:
        print("File not found. Initializing an empty dictionary.")
        return {}  # Return an empty dictionary if the file does not exist
    

def fetch_data(ticker, year, month, api_key):
    """Fetch data from Alpha Vantage API for a given month."""
    url = (
        "https://learn-api.wqu.edu/1/data-services/alpha-vantage/query?"
        "function=TIME_SERIES_INTRADAY&"
        f"symbol={ticker}&"
        "interval=5min&"
        f"month={year}-{month:02d}&"  # Corrected to use 'month' parameter
        "adjusted=true&"
        "outputsize=full&"  # Ensures full data for the specified month
        "extended_hours=false&"  # Optional: Includes extended trading hours
        f"apikey={api_key}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")

def process_data(data):
    """Process JSON data into a pandas DataFrame."""
    time_series = data.get('Time Series (5min)', {})
    data_list = [
        {
            'datetime': pd.to_datetime(dt),
            'open': float(info['1. open']),
            'high': float(info['2. high']),
            'low': float(info['3. low']),
            'close': float(info['4. close']),
            'volume': int(info['5. volume'])
        }
        for dt, info in time_series.items()
    ]
    df = pd.DataFrame(data_list)
    df.set_index('datetime', inplace=True)
    return df

def aggregate_data(ticker, start_year, end_year, api_key):
    """Aggregate data over several years and months."""
    frames = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            try:
                raw_data = fetch_data(ticker, year, month, api_key)
                if 'Time Series (5min)' in raw_data:
                    df = process_data(raw_data)
                    frames.append(df)

            except Exception as e:
                print(e)


    # Concatenate all DataFrames
    full_df = pd.concat(frames, axis=0)
    full_df.sort_index(inplace=True)  # Ensure the DataFrame is sorted by datetime
    return full_df