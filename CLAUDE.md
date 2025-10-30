# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Market Breadth Analysis Dashboard - Streamlit app để phân tích độ rộng thị trường VNINDEX với các chỉ số kỹ thuật.

## Run Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py

# Run on specific port
streamlit run app.py --server.port=8502
```

## Data Sources

- **VNINDEX data**: TCBS API (https://apipubaws.tcbs.com.vn) - từ 2022-10-31 đến hiện tại
- **Stock data**: Google Drive - 4 files CSV (393 stocks, filter còn 200 stocks theo danh sách cố định)

## Architecture

### Module Structure

1. **modules/data_loader.py**: Load dữ liệu
   - `load_vnindex_data()`: Load VNINDEX data từ TCBS API
     - Date range: 2022-10-31 đến hiện tại (match với stock data)
     - Manual filter vì TCBS API ignore `to_ts` parameter
   - `load_price_volume_data()`: Load 200 stocks từ 4 Google Drive CSV files
   - Calculate Matching Value = close * volume

2. **modules/indicators.py**: Tính toán các chỉ số kỹ thuật
   - `calculate_rsi()`: RSI với period tùy chỉnh - dùng **Wilder's EMA method** (chuẩn quốc tế) thông qua `pandas_ta.rsi()`
     - First average: Simple Moving Average (SMA)
     - Subsequent values: Exponential smoothing với alpha = 1/period
     - Cho kết quả chính xác khớp với TradingView, Bloomberg, MetaTrader
     - Hỗ trợ cả RSI 21 ngày và RSI 70 ngày
   - `calculate_breadth_above_ma50()`: % cổ phiếu có giá > MA50 (chỉ đếm stocks có MA50 hợp lệ, bỏ qua stocks chưa đủ 50 ngày)
   - `calculate_money_flow_index()`: Money Flow Index dựa trên daily price change
   - `calculate_advance_decline()`: Advance/Decline indicator
   - `calculate_new_high_new_low()`: New High/New Low indicator
   - `calculate_all_indicators()`: Tính tất cả chỉ số, bao gồm VNI RSI21, VNI RSI70, và RSI cho MFI/AD/NHNL

3. **app.py**: Main Streamlit application
   - Uses `@st.cache_data` để cache data loading và calculations
   - Displays dataframe với formatting (không có metrics summary)
   - Có 2 date filters riêng biệt trong sidebar: **Start Date** và **End Date**
   - Download CSV feature
   - 4 interactive charts (Plotly) với subplots: VnIndex, MFI, A/D, NHNL - mỗi chart có indicator và RSI của nó

### Key Calculation Logic

**Daily Price Change**: `(Price hôm nay - Price hôm qua) / Price hôm qua * 100%`

**Money Flow Index**:
- Nếu stock có daily price change > +1% → cộng trading value
- Nếu stock có daily price change < -1% → trừ trading value
- Rolling sum 15 ngày

**Advance/Decline**:
- A = số stock có daily price change > +1%
- B = số stock có daily price change < -1%
- C = A - B
- Rolling sum C của 15 ngày

**New High/New Low**:
- A = số stock có giá cao nhất trong 20 ngày giao dịch gần nhất
- B = số stock có giá thấp nhất trong 20 ngày giao dịch gần nhất
- C = A - B
- Rolling sum C của 15 ngày

**Breadth**: Đếm % stocks có current price > MA50 của chính nó
- Chỉ tính stocks có MA50 hợp lệ (đủ 50 ngày dữ liệu)
- Stocks chưa đủ 50 ngày bị loại khỏi cả tử số và mẫu số
- Filter: `df_stocks[df_stocks['MA50'].notna()]` trước khi tính %

## Known Issues

### TCBS API Limitations
- **Issue**: TCBS API parameter `to_ts` bị ignore, luôn trả về data đến hiện tại
- **Impact**: Nếu request từ 2024-01-01 đến 2024-01-31, API vẫn trả về data đến hiện tại
- **Solution**: Manual filter sau khi nhận data: `df[(df['tradingDate'] >= start) & (df['tradingDate'] <= end)]`

### Data Source Differences
- **TCBS vs VCI**: Có 3 ngày giá close khác nhau (2024-11-25, 2025-04-03, 2025-07-29)
- **Impact**: RSI tính từ TCBS và VCI lệch ~0.05 điểm (ví dụ: 60.62 vs 60.57)
- **Current**: Dùng TCBS vì ổn định trên Streamlit Cloud, vnstock/VCI gặp lỗi khi deploy

**RSI for Breadth Indicators** (Wilder's method):
- Áp dụng công thức RSI 21 ngày lên MFI_15D_Sum → MFI_15D_RSI_21
- Áp dụng công thức RSI 21 ngày lên AD_15D_Sum → AD_15D_RSI_21
- Áp dụng công thức RSI 21 ngày lên NHNL_15D_Sum → NHNL_15D_RSI_21
- Dùng `pandas_ta.rsi()` với Wilder's EMA smoothing (chuẩn quốc tế, KHÔNG dùng SMA)

### Performance Optimization

Các hàm tính toán trong `indicators.py` đã được tối ưu:
- Dùng `groupby().transform()` thay vì loop qua từng stock
- Dùng `np.where()` cho conditional operations
- Dùng vectorized operations thay vì apply từng row
- Tốc độ: ~0.16s cho 204k rows stock data

### Display Formatting

**Dataframe**:
- Column order: Date → VnIndex → VNI RSI21 → VNI RSI70 → Breadth - % > MA50 → MFI RSI → A/D RSI → NHNL RSI → các cột còn lại (MFI, AD, NHNL, 20D averages, chi tiết advances/declines)
- MFI columns hiển thị theo đơn vị tỷ (chia cho 1,000,000,000)
- Column names:
  - VnIndex_RSI_21 → "VNI RSI21"
  - VnIndex_RSI_70 → "VNI RSI70"
  - Breadth_Above_MA50 → "Breadth - % > MA50"
  - MFI_15D_RSI_21 → "MFI RSI"
  - AD_15D_RSI_21 → "A/D RSI"
  - NHNL_15D_RSI_21 → "NHNL RSI"
  - MFI_15D_Sum → "MFI"
  - AD_15D_Sum → "AD"
  - NHNL_15D_Sum → "NHNL"
- Dùng `st.column_config.NumberColumn` để format số với 2 số thập phân cho RSI, %, Avg values
- Số nguyên cho count values (A/D, NHNL)
- Dataframe hiển thị sắp xếp theo Date giảm dần (mới nhất trước)
- CSV export cũng sắp xếp theo Date giảm dần

**Charts** (Plotly subplots):
- 4 charts: VnIndex & RSI, MFI & RSI, A/D & RSI, NHNL & RSI
- Mỗi chart có 2 subplots xếp dọc, shared X-axis (chỉ hiển thị Date ở subplot dưới)
- RSI subplot có reference lines ở mức 30 và 70 (dotted lines)
- Không có subplot titles
