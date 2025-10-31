import requests
import pandas as pd
from datetime import datetime
import json

# API endpoint
url = "https://api-gateway-sandbox2.dragoncapital.com.vn/iris-sandbox/api/financialGainAnalyzer/win-rate"

# Headers (including Authorization Bearer token from the screenshot)
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJQUzI1NiIsImtpZCI6IkI2bjJCNjZERTlGMU1jMjE0QTVEOEQ5MTY4NxM4RjdGMjAyIiwidHwljoYXQrand0ln0eyJpc3MiOi0odHRwczovcL21pYS9c2VydnliZXMtaWRtbnBtdHRc2FuZG1veDluZHJhZ29uY2FwaXRhbCIsImNvbSIsInZuIiwidWRtNzYyMdI1QTZGZIxveD1uZHJhZ29uY2FwaXRhbCIsImNvbSIsInZuIiwiYXVkIjpbImh0dHBzOi8vYXBpLWdhdGV3YXktc2FuZGJveDIuZHJhZ29uY2FwaXRhbCIsImNvbSIsInZuIl0sImV4cCI6MTczMDA5NTYyOCwibmJmIjoxNzMwMDkzODI4LCJpYXQiOjE3MzAwOTM4MjgsImp0aSI6IjdlMzI3OTZhLWJiZGMtNDI3My1hY2Q4LWRjODJmZGI3ZjE3ZCIsImNsaWVudF9pZCI6ImlkbXAuZ2hmdGQtR2l0ZSI6Ik2MTUzNjAwMCIsImNsaWVudF9uYW1lIjoiVklQIiwic2NvcGUiOlsiQXBwbGljYXRpb25BY2Nlc3MiXSwiYW1yIjpbImN1c3RvbSJdfQ.eyJhbGciOiJQUzI1NiIsImtpZCI6IkI2bjJCNjZERTlGMU1qMjE0QTVEOEQ5TVY4NxM4RjdGMjAyIn0.eyJzdWIiOiI1ZjEzNGI5OS1hOTk1LWRhZjktOGM0ZS1hY2Q4LWRjODJmZGI3ZjE3ZCIsImNsaWVudF9pZCI6ImlkbXAuZ2hmdGQtR2l0ZSI6Ik2MTUzNjAwMCIsImNsaWVudF9uYW1lIjoiVklQIiwic2NvcGUiOlsiQXBwbGljYXRpb25BY2Nlc3MiXSwiYW1yIjpbImN1c3RvbSJdfQ.Q2FwaXRhbCIsImNvbSIsInZuIl0sImV4cCI6MTczMDA5NTYyOCwibmJmIjoxNzMwMDkzODI4LCJpYXQiOjE3MzAwOTM4MjgsImp0aSI6IjdlMzI3OTZhLWJiZGMtNDI3My1hY2Q4LWRjODJmZGI3ZjE3ZCIsImNsaWVudF9pZCI6ImlkbXAuZ2hmdGQtR2l0ZSI6Ik2MTUzNjAwMCIsImNsaWVudF9uYW1lIjoiVklQIiwic2NvcGUiOlsiQXBwbGljYXRpb25BY2Nlc3MiXSwiYW1yIjpbImN1c3RvbSJdfQ.ODM0ZTBkMjJmNyIsImF1ZGhfdGltZSI6Ik2MTUzNjAwMCIsImlkbXAuYnJvd2Jlcl9pZCI6IjZKbmJhcmVnTG5UqTGUqKEFNSVlpIwdcHJlZmVycmVkX3VzZXJuYW1lIjoiZGFuZ3Z1Iiwic3ViIjoiZGFuZ3Z1IiwiYXV0aF90aW1lIjoxNzMwMDkzODI4LCJpZHAiOiJsb2NhbCIsInVzZXJfaWQiOiIxNzY0OCIsInVzZXJfbmFtZSI6IkRhbmcgVnUgKERDR00pIiwidXNlcl9lbWFpbCI6ImRhbmd2dUBkcmFnb25jYXBpdGFsLmNvbS52biIsInVzZXJfcGhvbmUiOiIiLCJzaWQiOiI1MGJiNWM0ZC0zNjA5LTQ1MmEtYTIzZC04ODc5ZTE5YWQ2MDMiLCJpYXQiOjE3MzAwOTM4MjgsInNjb3BlIjpbIm9wZW5pZCIsInByb2ZpbGUiLCJJcmlzU2FuZGJveDIiLCJvZmZsaW5lX2FjY2VzcyJdLCJhbXIiOlsicHdkIl19.WRlbnRpdHktc2FuZGJveDIuZHJhZ29uY2FwaXRhbCIsImNvbSIsInZuIiwidXNlcl9pZCI6IjE3NjQ4IiwidXNlcl9uYW1lIjoiRGFuZyBWdSAoRENHTSkiLCJ1c2VyX2VtYWlsIjoiZGFuZ3Z1QGRyYWdvbmNhcGl0YWwuY29tLnZuIiwidXNlcl9waG9uZSI6IiIsInNpZCI6IjUwYmI1YzRkLTM2MDktNDUyYS1hMjNkLTg4NzllMTlhZDYwMyIsImlhdCI6MTczMDA5MzgyOCwic2NvcGUiOlsib3BlbmlkIiwicHJvZmlsZSIsIklyaXNTYW5kYm94MiIsIm9mZmxpbmVfYWNjZXNzIl0sImFtciI6WyJwd2QiXX0.hZ29uQ2FwaXRhbCIsImNvbSIsInZuIl0sImV4cCI6MTczMDA5NTYyOCwibmJmIjoxNzMwMDkzODI4LCJpYXQiOjE3MzAwOTM4MjgsImp0aSI6IjdlMzI3OTZhLWJiZGMtNDI3My1hY2Q4LWRjODJmZGI3ZjE3ZCIsImNsaWVudF9pZCI6ImlkbXAuZ2hmdGQtR2l0ZSI6Ik2MTUzNjAwMCIsImNsaWVudF9uYW1lIjoiVklQIiwic2NvcGUiOlsiQXBwbGljYXRpb25BY2Nlc3MiXSwiYW1yIjpbImN1c3RvbSJdfQ.QiVuUzFLJnNKlwabUKiVnZGFubmdZdSIsInN1YiI6ImRhbmd2dSIsImF1dGhfdGltZSI6MTczMDA5MzgyOCwiaWRwIjoibG9jYWwiLCJ1c2VyX2lkIjoiMTc2NDgiLCJ1c2VyX25hbWUiOiJEYW5nIFZ1IChEQ0dNKSIsInVzZXJfZW1haWwiOiJkYW5ndnVAZHJhZ29uY2FwaXRhbC5jb20udm4iLCJ1c2VyX3Bob25lIjoiIiwic2lkIjoiNTBiYjVjNGQtMzYwOS00NTJhLWEyM2QtODg3OWUxOWFkNjAzIiwiaWF0IjoxNzMwMDkzODI4LCJzY29wZSI6WyJvcGVuaWQiLCJwcm9maWxlIiwiSXJpc1NhbmRib3gyIiwib2ZmbGluZV9hY2Nlc3MiXSwiYW1yIjpbInB3ZCJdfQ.T3R1bWItcGFjZjM2NDktNDI3My1hY2Q4LWRjODJmZGI3ZjE3ZCIsImNsaWVudF9pZCI6ImlkbXAuZ2hmdGQtR2l0ZSI6Ik2MTUzNjAwMCIsImNsaWVudF9uYW1lIjoiVklQIiwic2NvcGUiOlsiQXBwbGljYXRpb25BY2Nlc3MiXSwiYW1yIjpbImN1c3RvbSJdfQ.4ucZfuZGIveClsinN1YiI6IjdlNjAyNWMmRnTiJOTMtNDk2YS04ZDg4LWNhM0ZODM0ZTBkMjJmNyIsImF1ZGhfdGltZSI6Ik2MTUzNjAwMCIsImlkbXAuYnJvd2Jlcl9pZCI6IjZKbmJhcmVnTG5UqTGUqKEFNSVlpIwdcHJlZmVycmVkX3VzZXJuYW1lIjoiZGFuZ3Z1Iiwic3ViIjoiZGFuZ3Z1IiwiYXV0aF90aW1lIjoxNzMwMDkzODI4LCJpZHAiOiJsb2NhbCIsInVzZXJfaWQiOiIxNzY0OCIsInVzZXJfbmFtZSI6IkRhbmcgVnUgKERDR00pIiwidXNlcl9lbWFpbCI6ImRhbmd2dUBkcmFnb25jYXBpdGFsLmNvbS52biIsInVzZXJfcGhvbmUiOiIiLCJzaWQiOiI1MGJiNWM0ZC0zNjA5LTQ1MmEtYTIzZC04ODc5ZTE5YWQ2MDMiLCJpYXQiOjE3MzAwOTM4MjgsInNjb3BlIjpbIm9wZW5pZCIsInByb2ZpbGUiLCJJcmlzU2FuZGJveDIiLCJvZmZsaW5lX2FjY2VzcyJdLCJhbXIiOlsicHdkIl19"
}

# Request payload
payload = {
    "type": 1,
    "duration": 0,
    "marketCaps": ["Large-Cap", "Mid-Cap"],
    "newHighDay": 120
}

print("Fetching daily winrate data...")
print(f"Request URL: {url}")
print(f"Request Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()

    print(f"\nResponse received! Total records: {len(data)}")

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Convert date string to datetime
    df['date'] = pd.to_datetime(df['date'])

    # Sort by date ascending
    df = df.sort_values('date')

    # Rename columns for clarity
    df = df.rename(columns={'value': 'winRate'})

    # Save to CSV
    output_file = "daily_winrate.csv"
    df.to_csv(output_file, index=False)
    print(f"\nData saved to: {output_file}")

    # Display summary
    print(f"\nDate range: {df['date'].min()} to {df['date'].max()}")
    print(f"Total days: {len(df)}")
    print(f"\nWinRate statistics:")
    print(f"  Min: {df['winRate'].min():.4f}")
    print(f"  Max: {df['winRate'].max():.4f}")
    print(f"  Mean: {df['winRate'].mean():.4f}")
    print(f"  Median: {df['winRate'].median():.4f}")

    # Display first and last 10 rows
    print(f"\nFirst 10 rows:")
    print(df.head(10).to_string(index=False))

    print(f"\nLast 10 rows:")
    print(df.tail(10).to_string(index=False))

except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Response: {e.response.text}")
except Exception as e:
    print(f"Error: {e}")
