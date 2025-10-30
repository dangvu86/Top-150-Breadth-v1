import pandas as pd
import io
import requests
from datetime import datetime

def load_vnindex_data():
    """Load VNINDEX data from TCBS API"""
    ticker = 'VNINDEX'
    from_ts = int(pd.Timestamp('2022-10-31').timestamp())
    to_ts = int(datetime.now().timestamp())

    url = f'https://apipubaws.tcbs.com.vn/stock-insight/v1/stock/bars-long-term?ticker={ticker}&type=index&resolution=D&from={from_ts}&to={to_ts}'

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()
    records = data.get('data', [])

    if not records:
        raise ValueError("No data returned from TCBS API")

    df = pd.DataFrame(records)
    df['tradingDate'] = pd.to_datetime(df['tradingDate']).dt.tz_localize(None)

    # Filter by date range (TCBS API ignores to_ts parameter)
    df = df[(df['tradingDate'] >= '2022-10-31') & (df['tradingDate'] <= datetime.now())]

    df['pct_change'] = df['close'].pct_change() * 100

    df = df.rename(columns={
        'tradingDate': 'Ngày',
        'close': 'Giá đóng cửa',
        'pct_change': '% Thay đổi'
    })

    df = df[['Ngày', 'Giá đóng cửa', '% Thay đổi']].copy()
    df = df.sort_values('Ngày').reset_index(drop=True)

    return df

def load_price_volume_data():
    """Load stock price and volume data from 4 Google Drive files"""
    # List of 200 stocks to filter (from original dataset)
    stock_list_200 = ['AAA', 'ACB', 'ACG', 'AGG', 'AGR', 'ANV', 'APG', 'ASM', 'AST', 'BAF',
                      'BBC', 'BCG', 'BCM', 'BFC', 'BHN', 'BIC', 'BID', 'BMI', 'BMP', 'BSI',
                      'BSR', 'BVH', 'BWE', 'CHP', 'CII', 'CKG', 'CMG', 'CRE', 'CRV', 'CSV',
                      'CTD', 'CTF', 'CTG', 'CTR', 'CTS', 'DBC', 'DBD', 'DCL', 'DCM', 'DGC',
                      'DGW', 'DHC', 'DHG', 'DIG', 'DMC', 'DPG', 'DPM', 'DPR', 'DRC', 'DSC',
                      'DSE', 'DVP', 'DXG', 'DXS', 'EIB', 'ELC', 'EVF', 'EVG', 'FCN', 'FMC',
                      'FPT', 'FRT', 'FTS', 'GAS', 'GEE', 'GEG', 'GEX', 'GIL', 'GMD', 'GVR',
                      'HAG', 'HAH', 'HCM', 'HDB', 'HDC', 'HDG', 'HHS', 'HHV', 'HNA', 'HPG',
                      'HQC', 'HSG', 'HT1', 'HTG', 'HVN', 'IDI', 'IJC', 'IMP', 'KBC', 'KDC',
                      'KDH', 'KHG', 'KOS', 'KSB', 'LCG', 'LGC', 'LIX', 'LPB', 'MBB', 'MCM',
                      'MIG', 'MSB', 'MSH', 'MSN', 'MWG', 'NAB', 'NAF', 'NBB', 'NCT', 'NKG',
                      'NLG', 'NT2', 'NTC', 'NTL', 'NVL', 'OCB', 'ORS', 'PAN', 'PC1', 'PDN',
                      'PDR', 'PET', 'PGD', 'PGI', 'PGV', 'PHR', 'PLX', 'PNJ', 'POW', 'PPC',
                      'PTB', 'PVD', 'PVT', 'QCG', 'RAL', 'REE', 'SAB', 'SAM', 'SBA', 'SBT',
                      'SCR', 'SCS', 'SGN', 'SGT', 'SHB', 'SHI', 'SHP', 'SIP', 'SJS', 'SSB',
                      'SSI', 'STB', 'STG', 'STK', 'SVC', 'SZC', 'TAL', 'TBC', 'TCB', 'TCH',
                      'TCM', 'TCX', 'TDM', 'TDP', 'TLG', 'TMP', 'TMS', 'TNH', 'TPB', 'TRA',
                      'TRC', 'TTA', 'TV2', 'TVS', 'VAB', 'VCB', 'VCF', 'VCG', 'VCI', 'VDS',
                      'VFG', 'VGC', 'VHC', 'VHM', 'VIB', 'VIC', 'VIX', 'VJC', 'VND', 'VNM',
                      'VOS', 'VPB', 'VPD', 'VPI', 'VPL', 'VRE', 'VSC', 'VSH', 'VTP', 'YEG']

    # Google Drive file IDs for 4 CSV files (393 stocks total)
    file_ids = [
        '1op_GzDUtbcXOJOMkI2K-0AU9cF4m8J1S',  # 93 stocks
        '1E0BDythcdIdGrIYdbJCNB0DxPHJ-njzc',  # 100 stocks
        '1cb9Ef1IDyArlmguRZ5u63tCcxR57KEfA',  # 100 stocks
        '1XPZKnRDklQ1DOdVgncn71SLg1pfisQtV'   # 100 stocks
    ]

    # Load and combine all files
    dfs = []
    for file_id in file_ids:
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        df_temp = pd.read_csv(url)
        dfs.append(df_temp)

    # Concatenate all dataframes
    df = pd.concat(dfs, ignore_index=True)

    # Filter to keep only 200 stocks from original list
    df = df[df['symbol'].isin(stock_list_200)].copy()

    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'])

    # Calculate Matching Value = close price * volume
    df['Matching Value'] = df['close'] * df['volume']

    # Rename columns to match expected format
    df = df.rename(columns={
        'symbol': 'TICKER',
        'date': 'Trading Date',
        'close': 'Daily Closing Price',
        'volume': 'Matching Volume'
    })

    # Sort by ticker and date
    df = df.sort_values(['TICKER', 'Trading Date']).reset_index(drop=True)

    return df
