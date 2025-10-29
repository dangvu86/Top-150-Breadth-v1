# Market Breadth Analysis Dashboard

Streamlit app để phân tích độ rộng thị trường VNINDEX

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy app

```bash
streamlit run app.py
```

## Cấu trúc

```
├── app.py                  # Main Streamlit app
├── data/                   # Data folder
│   ├── cleaned_VNINDEX.csv
│   └── cleaned_PriceVolume.csv
├── modules/
│   ├── data_loader.py     # Load data
│   └── indicators.py      # Calculate indicators
└── requirements.txt
```

## Các chỉ số

- **VnIndex RSI (21D)**: RSI 21 ngày
- **Breadth % Above MA50**: % cổ phiếu trên MA50
- **Money Flow Index**: Giá trị ròng cổ phiếu tăng/giảm >1%, tổng 15 ngày
- **Advance/Decline**: Số lượng ròng cổ phiếu tăng/giảm >1%, tổng 15 ngày
