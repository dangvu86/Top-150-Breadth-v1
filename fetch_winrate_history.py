import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# API endpoint
url = "https://api-gateway-sandbox2.dragoncapital.com.vn/iris-sandbox/api/financialGainAnalyzer"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": "Bearer"
}

# Tham số cố định
payload_base = {
    "newHighValue": 120,
    "marketCaps": ["Large-Cap", "Mid-Cap"]
}

# Lấy dữ liệu cho nhiều duration khác nhau (từ 0 đến 20 ngày)
results = []

print("Fetching winrate data by duration...")
for duration in range(0, 21):
    payload = {
        **payload_base,
        "duration": duration
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        overview = data.get('overView', {})
        tickers_count = len(data.get('tickers', []))

        results.append({
            'duration': duration,
            'winRate': overview.get('winRate', 0),
            'avgGain': overview.get('avgGain', 0),
            'avgLoss': overview.get('avgLoss', 0),
            'tickers_count': tickers_count
        })

        print(f"Duration {duration}: WinRate={overview.get('winRate', 0):.4f}, Tickers={tickers_count}")

        # Delay để tránh rate limit
        time.sleep(0.5)

    except Exception as e:
        print(f"Error at duration {duration}: {e}")
        results.append({
            'duration': duration,
            'winRate': 0,
            'avgGain': 0,
            'avgLoss': 0,
            'tickers_count': 0
        })

# Tạo DataFrame
df = pd.DataFrame(results)

# Lưu ra CSV
output_file = "winrate_by_duration.csv"
df.to_csv(output_file, index=False)
print(f"\nData saved to file: {output_file}")
print(df.to_string())
