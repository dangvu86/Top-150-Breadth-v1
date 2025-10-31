"""
Module to fetch WinRate data from Dragon Capital API
"""
import requests
import pandas as pd
from datetime import datetime

def fetch_winrate_data(bearer_token):
    """
    Fetch daily winrate data from Dragon Capital API

    Parameters:
    -----------
    bearer_token : str
        Bearer token for API authentication

    Returns:
    --------
    pd.DataFrame
        DataFrame with columns: date, winRate
    """
    url = "https://api-gateway-sandbox2.dragoncapital.com.vn/iris-sandbox/api/financialGainAnalyzer/win-rate"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {bearer_token}"
    }

    payload = {
        "type": 1,
        "duration": 0,
        "marketCaps": ["Large-Cap", "Mid-Cap"],
        "newHighDay": 120
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Convert date string to datetime
        df['date'] = pd.to_datetime(df['date'])

        # Rename columns
        df = df.rename(columns={'value': 'winRate'})

        # Sort by date ascending
        df = df.sort_values('date').reset_index(drop=True)

        return df

    except requests.exceptions.RequestException as e:
        print(f"Error fetching winrate data: {e}")
        return pd.DataFrame(columns=['date', 'winRate'])
    except Exception as e:
        print(f"Error processing winrate data: {e}")
        return pd.DataFrame(columns=['date', 'winRate'])


def fetch_breakout_data(bearer_token):
    """
    Fetch daily breakout data from Dragon Capital API

    Parameters:
    -----------
    bearer_token : str
        Bearer token for API authentication

    Returns:
    --------
    pd.DataFrame
        DataFrame with columns: date, breakOut
    """
    url = "https://api-gateway-sandbox2.dragoncapital.com.vn/iris-sandbox/api/financialGainAnalyzer/win-rate"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {bearer_token}"
    }

    payload = {
        "type": 3,
        "duration": 0,
        "marketCaps": ["Large-Cap", "Mid-Cap"],
        "newHighDay": 20
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Convert date string to datetime
        df['date'] = pd.to_datetime(df['date'])

        # Rename columns
        df = df.rename(columns={'value': 'breakOut'})

        # Sort by date ascending
        df = df.sort_values('date').reset_index(drop=True)

        return df

    except requests.exceptions.RequestException as e:
        print(f"Error fetching breakout data: {e}")
        return pd.DataFrame(columns=['date', 'breakOut'])
    except Exception as e:
        print(f"Error processing breakout data: {e}")
        return pd.DataFrame(columns=['date', 'breakOut'])


def get_winrate_summary(df):
    """
    Get summary statistics of winrate data

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with winRate column

    Returns:
    --------
    dict
        Dictionary with summary statistics
    """
    if df.empty:
        return {
            'min': 0,
            'max': 0,
            'mean': 0,
            'median': 0,
            'count': 0
        }

    return {
        'min': df['winRate'].min(),
        'max': df['winRate'].max(),
        'mean': df['winRate'].mean(),
        'median': df['winRate'].median(),
        'count': len(df)
    }
