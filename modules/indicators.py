import pandas as pd
import numpy as np
import pandas_ta as pta

def calculate_rsi(prices, period=21):
    """Calculate RSI indicator using Wilder's method (EMA smoothing)

    This uses pandas_ta library which implements the standard Wilder's RSI:
    - First average: Simple Moving Average (SMA)
    - Subsequent values: Exponential smoothing with alpha = 1/period

    Args:
        prices: pandas Series of prices
        period: RSI period (default 21)

    Returns:
        pandas Series of RSI values

    Note: RSI calculation requires at least (period * 2) data points for proper warmup.
    Values before this will be NaN.
    """
    # Ensure consistent behavior across environments by requiring proper warmup period
    # This prevents inconsistent results between localhost and Streamlit Cloud
    if len(prices) < period * 2:
        return pd.Series([np.nan] * len(prices), index=prices.index)

    return pta.rsi(prices, length=period)

def calculate_breadth_above_ma50(df_stocks):
    """Calculate percentage of stocks above their 50-day MA - Optimized"""
    # Calculate MA50 for each stock
    df_stocks = df_stocks.sort_values(['TICKER', 'Trading Date'])
    df_stocks['MA50'] = df_stocks.groupby('TICKER')['Daily Closing Price'].transform(lambda x: x.rolling(50).mean())

    # Filter only stocks with valid MA50
    df_valid = df_stocks[df_stocks['MA50'].notna()].copy()

    # Mark stocks above MA50
    df_valid['Above_MA50'] = (df_valid['Daily Closing Price'] > df_valid['MA50']).astype(int)

    # Group by date and calculate percentage
    df_breadth = df_valid.groupby('Trading Date').agg({
        'Above_MA50': 'sum',
        'TICKER': 'count'
    }).reset_index()

    df_breadth.columns = ['Trading Date', 'Count_Above', 'Total_Count']
    df_breadth['Breadth_Above_MA50'] = (df_breadth['Count_Above'] / df_breadth['Total_Count']) * 100

    return df_breadth[['Trading Date', 'Breadth_Above_MA50']]

def calculate_money_flow_index(df_stocks):
    """Calculate Money Flow Index based on daily price changes - Optimized"""
    # Calculate daily price change for each stock
    df_stocks = df_stocks.sort_values(['TICKER', 'Trading Date']).copy()
    df_stocks['Price_Change_Pct'] = df_stocks.groupby('TICKER')['Daily Closing Price'].pct_change() * 100

    # Fill NaN in Matching Value with 0
    df_stocks['Matching Value'] = df_stocks['Matching Value'].fillna(0)

    # Create Up/Down value columns
    df_stocks['Up_Value'] = np.where(df_stocks['Price_Change_Pct'] > 1, df_stocks['Matching Value'], 0)
    df_stocks['Down_Value'] = np.where(df_stocks['Price_Change_Pct'] < -1, df_stocks['Matching Value'], 0)

    # Group by date and sum
    df_mfi = df_stocks.groupby('Trading Date').agg({
        'Up_Value': 'sum',
        'Down_Value': 'sum'
    }).reset_index()

    df_mfi.columns = ['Trading Date', 'MFI_Up_Value', 'MFI_Down_Value']
    df_mfi['MFI_Net'] = df_mfi['MFI_Up_Value'] - df_mfi['MFI_Down_Value']

    # Rolling sum 15 days
    df_mfi = df_mfi.sort_values('Trading Date')
    df_mfi['MFI_15D_Sum'] = df_mfi['MFI_Net'].rolling(window=15).sum()

    return df_mfi

def calculate_advance_decline(df_stocks):
    """Calculate Advance/Decline indicator - Optimized"""
    # Calculate daily price change for each stock
    df_stocks = df_stocks.sort_values(['TICKER', 'Trading Date']).copy()
    df_stocks['Price_Change_Pct'] = df_stocks.groupby('TICKER')['Daily Closing Price'].pct_change() * 100

    # Create Advance/Decline flags
    df_stocks['Is_Advance'] = (df_stocks['Price_Change_Pct'] > 1).astype(int)
    df_stocks['Is_Decline'] = (df_stocks['Price_Change_Pct'] < -1).astype(int)

    # Group by date and count
    df_ad = df_stocks.groupby('Trading Date').agg({
        'Is_Advance': 'sum',
        'Is_Decline': 'sum'
    }).reset_index()

    df_ad.columns = ['Trading Date', 'AD_Advances', 'AD_Declines']
    df_ad['AD_Net'] = df_ad['AD_Advances'] - df_ad['AD_Declines']

    # Rolling sum 15 days of net A-D
    df_ad = df_ad.sort_values('Trading Date')
    df_ad['AD_15D_Sum'] = df_ad['AD_Net'].rolling(window=15).sum()

    return df_ad

def calculate_new_high_new_low(df_stocks):
    """Calculate New High New Low indicator - Optimized"""
    # Sort data
    df_stocks = df_stocks.sort_values(['TICKER', 'Trading Date']).copy()

    # Calculate 20-day rolling high and low for each stock
    df_stocks['Rolling_20D_High'] = df_stocks.groupby('TICKER')['Daily Closing Price'].transform(
        lambda x: x.rolling(window=20).max()
    )
    df_stocks['Rolling_20D_Low'] = df_stocks.groupby('TICKER')['Daily Closing Price'].transform(
        lambda x: x.rolling(window=20).min()
    )

    # Check if current price equals the 20-day high or low
    df_stocks['Is_New_High'] = (df_stocks['Daily Closing Price'] == df_stocks['Rolling_20D_High']).astype(int)
    df_stocks['Is_New_Low'] = (df_stocks['Daily Closing Price'] == df_stocks['Rolling_20D_Low']).astype(int)

    # Group by date and count
    df_nhnl = df_stocks.groupby('Trading Date').agg({
        'Is_New_High': 'sum',
        'Is_New_Low': 'sum'
    }).reset_index()

    df_nhnl.columns = ['Trading Date', 'NHNL_New_Highs', 'NHNL_New_Lows']
    df_nhnl['NHNL_Net'] = df_nhnl['NHNL_New_Highs'] - df_nhnl['NHNL_New_Lows']

    # Rolling sum 15 days of net NHNL
    df_nhnl = df_nhnl.sort_values('Trading Date')
    df_nhnl['NHNL_15D_Sum'] = df_nhnl['NHNL_Net'].rolling(window=15).sum()

    return df_nhnl

def calculate_all_indicators(df_vnindex, df_stocks):
    """Calculate all indicators and merge into one dataframe"""

    # Prepare VNINDEX data
    df_result = df_vnindex[['Ngày', 'Giá đóng cửa', '% Thay đổi']].copy()
    df_result.columns = ['Trading Date', 'VnIndex', 'VnIndex_Change_Pct']
    df_result = df_result.sort_values('Trading Date')

    # Calculate RSI for VNINDEX
    df_result['VnIndex_RSI_21'] = calculate_rsi(df_result['VnIndex'], period=21)
    df_result['VnIndex_RSI_70'] = calculate_rsi(df_result['VnIndex'], period=70)

    # Calculate Breadth
    df_breadth = calculate_breadth_above_ma50(df_stocks)
    df_result = df_result.merge(df_breadth, on='Trading Date', how='left')

    # 20D Average of Breadth
    df_result['Breadth_20D_Avg'] = df_result['Breadth_Above_MA50'].rolling(window=20).mean()

    # Calculate Money Flow Index
    df_mfi = calculate_money_flow_index(df_stocks)
    df_result = df_result.merge(df_mfi, on='Trading Date', how='left')

    # 20D Average of MFI
    df_result['MFI_20D_Avg'] = df_result['MFI_15D_Sum'].rolling(window=20).mean()

    # Calculate Advance/Decline
    df_ad = calculate_advance_decline(df_stocks)
    df_result = df_result.merge(df_ad, on='Trading Date', how='left')

    # 20D Average of A-D
    df_result['AD_20D_Avg'] = df_result['AD_15D_Sum'].rolling(window=20).mean()

    # Calculate New High New Low
    df_nhnl = calculate_new_high_new_low(df_stocks)
    df_result = df_result.merge(df_nhnl, on='Trading Date', how='left')

    # 20D Average of NHNL
    df_result['NHNL_20D_Avg'] = df_result['NHNL_15D_Sum'].rolling(window=20).mean()

    # Calculate RSI 21 for breadth indicators
    df_result['MFI_15D_RSI_21'] = calculate_rsi(df_result['MFI_15D_Sum'], period=21)
    df_result['AD_15D_RSI_21'] = calculate_rsi(df_result['AD_15D_Sum'], period=21)
    df_result['NHNL_15D_RSI_21'] = calculate_rsi(df_result['NHNL_15D_Sum'], period=21)

    return df_result
