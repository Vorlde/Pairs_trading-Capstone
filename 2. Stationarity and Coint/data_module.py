import pandas as pd
import numpy as np
from datetime import datetime, timedelta



def generate_trading_data_blocks(df, month,year,days_per_block=9, step_days=5):
    """
    Generate rolling blocks of data consisting of 9 trading days,
    advancing the window by 5 days after each block from the original dataframe.
    """

    if month == 12:
      month = 1
      year +=1

    else:
      month+=1

    month_data =df[(df.index.year == year) & (df.index.month == month)]

    # Extract unique trading days from the index
    unique_days = month_data.index.normalize().unique()

    for start_day_idx in range(0, len(unique_days) - days_per_block + 1, step_days):
        # Identify start and end day for the block
        start_day = unique_days[start_day_idx]
        end_day_idx = start_day_idx + days_per_block - 1  # inclusive end day index
        if end_day_idx >= len(unique_days):  # Ensure we don't go out of bounds
            break
        end_day = unique_days[end_day_idx]

        # Slice the original dataframe to get the block data
        block_data = month_data[start_day:end_day]
        print(f"yeilding block data for {month} {year}")
        yield block_data



def calculate_monthly_clusters(monthly_data):
    """
    Calculate clusters for the given month.
    """
    ret_df = monthly_data.pct_change().round(4).fillna(0)
    X = get_pca_features(ret_df)
    clustered_series = create_clusters(X, ret_df.columns)

    return clustered_series



def yield_monthly_data(df):
    """
    Yields each month's data from the dataframe.
    """
    for year in df.index.year.unique():
        for month in df[df.index.year == year].index.month.unique():
            monthly_data = df[(df.index.year == year) & (df.index.month == month)]
            yield year, month, monthly_data