import streamlit as st
import pandas as pd
import sys
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add modules to path
sys.path.append(os.path.dirname(__file__))

from modules.data_loader import load_vnindex_data, load_price_volume_data
from modules.indicators import calculate_all_indicators

# Page config
st.set_page_config(
    page_title="Market Breadth Analysis",
    page_icon="📊",
    layout="wide"
)



# Load data - no cache, always reload when app restarts
def load_data():
    df_vnindex = load_vnindex_data()
    df_stocks = load_price_volume_data()
    return df_vnindex, df_stocks

def compute_indicators(df_vnindex, df_stocks):
    return calculate_all_indicators(df_vnindex, df_stocks)

# Load and calculate
with st.spinner("Loading data..."):
    df_vnindex, df_stocks = load_data()

with st.spinner("Calculating indicators..."):
    df_result = compute_indicators(df_vnindex, df_stocks)

# Filters
st.sidebar.header("Filters")

# Start Date
start_date = st.sidebar.date_input(
    "Start Date",
    value=df_result['Trading Date'].min().date(),
    min_value=df_result['Trading Date'].min().date(),
    max_value=df_result['Trading Date'].max().date()
)

# End Date
end_date = st.sidebar.date_input(
    "End Date",
    value=df_result['Trading Date'].max().date(),
    min_value=df_result['Trading Date'].min().date(),
    max_value=df_result['Trading Date'].max().date()
)

# Filter data
df_filtered = df_result[
    (df_result['Trading Date'].dt.date >= start_date) &
    (df_result['Trading Date'].dt.date <= end_date)
]

# Display data table
st.header("Market Breadth Indicators")

# Define display columns in specific order
display_columns = [
    'Trading Date',
    'VnIndex',
    'VnIndex_RSI_21',
    'VnIndex_RSI_70',
    'Breadth_Above_MA50',
    'MFI_15D_RSI_21',
    'AD_15D_RSI_21',
    'NHNL_15D_RSI_21',
    # Remaining columns
    'MFI_15D_Sum',
    'AD_15D_Sum',
    'NHNL_15D_Sum',
    'Breadth_20D_Avg',
    'MFI_Up_Value',
    'MFI_Down_Value',
    'MFI_20D_Avg',
    'AD_Advances',
    'AD_Declines',
    'AD_Net',
    'AD_20D_Avg',
    'NHNL_New_Highs',
    'NHNL_New_Lows',
    'NHNL_Net',
    'NHNL_20D_Avg'
]

# Filter only columns that exist in df_filtered
display_columns = [col for col in display_columns if col in df_filtered.columns]

# Prepare display columns
display_df = df_filtered[display_columns].copy()

# Build column name mapping
column_mapping = {
    'Trading Date': 'Date',
    'VnIndex': 'VnIndex',
    'VnIndex_RSI_21': 'VNI RSI21',
    'VnIndex_RSI_70': 'VNI RSI70',
    'Breadth_Above_MA50': 'Breadth - % > MA50',
    'MFI_15D_RSI_21': 'MFI RSI',
    'AD_15D_RSI_21': 'A/D RSI',
    'NHNL_15D_RSI_21': 'NHNL RSI',
    'MFI_15D_Sum': 'MFI',
    'AD_15D_Sum': 'AD',
    'NHNL_15D_Sum': 'NHNL',
    'Breadth_20D_Avg': '20D Avg Breadth',
    'MFI_Up_Value': 'MFI: Up Value',
    'MFI_Down_Value': 'MFI: Down Value',
    'MFI_20D_Avg': '20D Avg MFI',
    'AD_Advances': 'A/D: Advances',
    'AD_Declines': 'A/D: Declines',
    'AD_Net': 'A/D: Net (A-B)',
    'AD_20D_Avg': '20D Avg A/D',
    'NHNL_New_Highs': 'NHNL: New Highs',
    'NHNL_New_Lows': 'NHNL: New Lows',
    'NHNL_Net': 'NHNL: Net (A-B)',
    'NHNL_20D_Avg': '20D Avg NHNL'
}

# Rename columns for display
display_df = display_df.rename(columns=column_mapping)

# Format date
display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d')

# Format MFI columns in billions (only if columns exist)
if 'MFI: Up Value' in display_df.columns:
    display_df['MFI: Up Value'] = display_df['MFI: Up Value'].apply(lambda x: f"{x/1000000000:,.2f}" if pd.notna(x) else "")
if 'MFI: Down Value' in display_df.columns:
    display_df['MFI: Down Value'] = display_df['MFI: Down Value'].apply(lambda x: f"{x/1000000000:,.2f}" if pd.notna(x) else "")
if 'MFI' in display_df.columns:
    display_df['MFI'] = display_df['MFI'].apply(lambda x: f"{x/1000000000:,.2f}" if pd.notna(x) else "")
if '20D Avg MFI' in display_df.columns:
    display_df['20D Avg MFI'] = display_df['20D Avg MFI'].apply(lambda x: f"{x/1000000000:,.2f}" if pd.notna(x) else "")

# Sort by date descending
display_df = display_df.sort_values('Date', ascending=False)

# Build column config dynamically
column_config = {
    'Date': st.column_config.TextColumn('Date'),
    'VnIndex': st.column_config.NumberColumn('VnIndex', format="%.2f"),
    'VNI RSI21': st.column_config.NumberColumn('VNI RSI21', format="%.2f"),
    'VNI RSI70': st.column_config.NumberColumn('VNI RSI70', format="%.2f"),
    'Breadth - % > MA50': st.column_config.NumberColumn('Breadth - % > MA50', format="%.2f%%"),
    'MFI RSI': st.column_config.NumberColumn('MFI RSI', format="%.2f"),
    'A/D RSI': st.column_config.NumberColumn('A/D RSI', format="%.2f"),
    'NHNL RSI': st.column_config.NumberColumn('NHNL RSI', format="%.2f"),
    'MFI': st.column_config.TextColumn('MFI'),
    'AD': st.column_config.NumberColumn('AD', format="%d"),
    'NHNL': st.column_config.NumberColumn('NHNL', format="%d"),
    '20D Avg Breadth': st.column_config.NumberColumn('20D Avg Breadth', format="%.2f%%"),
    'MFI: Up Value': st.column_config.TextColumn('MFI: Up Value'),
    'MFI: Down Value': st.column_config.TextColumn('MFI: Down Value'),
    '20D Avg MFI': st.column_config.TextColumn('20D Avg MFI'),
    'A/D: Advances': st.column_config.NumberColumn('A/D: Advances', format="%d"),
    'A/D: Declines': st.column_config.NumberColumn('A/D: Declines', format="%d"),
    'A/D: Net (A-B)': st.column_config.NumberColumn('A/D: Net (A-B)', format="%d"),
    '20D Avg A/D': st.column_config.NumberColumn('20D Avg A/D', format="%.2f"),
    'NHNL: New Highs': st.column_config.NumberColumn('NHNL: New Highs', format="%d"),
    'NHNL: New Lows': st.column_config.NumberColumn('NHNL: New Lows', format="%d"),
    'NHNL: Net (A-B)': st.column_config.NumberColumn('NHNL: Net (A-B)', format="%d"),
    '20D Avg NHNL': st.column_config.NumberColumn('20D Avg NHNL', format="%.2f"),
}

# Display table with NumberColumn for right alignment and formatting
st.dataframe(
    display_df,
    use_container_width=True,
    height=600,
    column_config=column_config
)

# Download button - sort by date descending
df_export = df_filtered.sort_values('Trading Date', ascending=False)
csv = df_export.to_csv(index=False)
st.download_button(
    label="📥 Download Full Data as CSV",
    data=csv,
    file_name="market_breadth_analysis.csv",
    mime="text/csv"
)

# Charts Section
st.header("Technical Charts")

# Prepare data for charts (use filtered data)
chart_data = df_filtered.sort_values('Trading Date')

# Chart 1: VnIndex and VnIndex RSI
st.subheader("VnIndex & RSI")
fig1 = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.6, 0.4]
)

fig1.add_trace(
    go.Scatter(x=chart_data['Trading Date'], y=chart_data['VnIndex'],
               name='VnIndex', line=dict(color='blue', width=2)),
    row=1, col=1
)

fig1.add_trace(
    go.Scatter(x=chart_data['Trading Date'], y=chart_data['VnIndex_RSI_21'],
               name='VnIndex RSI', line=dict(color='purple', width=2)),
    row=2, col=1
)

# Add RSI reference lines
fig1.add_hline(y=70, line_dash="dot", line_color="red", line_width=1, row=2, col=1)
fig1.add_hline(y=30, line_dash="dot", line_color="green", line_width=1, row=2, col=1)

fig1.update_xaxes(title_text="Date", row=2, col=1)
fig1.update_yaxes(title_text="VnIndex", row=1, col=1)
fig1.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
fig1.update_layout(height=600, showlegend=False)

st.plotly_chart(fig1, use_container_width=True)

# Chart 2: VnIndex and Breadth % Above MA50
st.subheader("VnIndex & Breadth % > MA50")
fig_breadth = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.6, 0.4]
)

fig_breadth.add_trace(
    go.Scatter(x=chart_data['Trading Date'], y=chart_data['VnIndex'],
               name='VnIndex', line=dict(color='blue', width=2)),
    row=1, col=1
)

fig_breadth.add_trace(
    go.Scatter(x=chart_data['Trading Date'], y=chart_data['Breadth_Above_MA50'],
               name='Breadth % > MA50', line=dict(color='teal', width=2)),
    row=2, col=1
)

fig_breadth.update_xaxes(title_text="Date", row=2, col=1)
fig_breadth.update_yaxes(title_text="VnIndex", row=1, col=1)
fig_breadth.update_yaxes(title_text="Breadth %", row=2, col=1)
fig_breadth.update_layout(height=600, showlegend=False)

st.plotly_chart(fig_breadth, use_container_width=True)

# Chart 3: MFI and MFI RSI
st.subheader("MFI & RSI")
fig2 = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.6, 0.4]
)

fig2.add_trace(
    go.Scatter(x=chart_data['Trading Date'], y=chart_data['MFI_15D_Sum'],
               name='MFI', line=dict(color='green', width=2)),
    row=1, col=1
)

if 'MFI_15D_RSI_21' in chart_data.columns:
    fig2.add_trace(
        go.Scatter(x=chart_data['Trading Date'], y=chart_data['MFI_15D_RSI_21'],
                   name='MFI RSI', line=dict(color='purple', width=2)),
        row=2, col=1
    )

    # Add RSI reference lines
    fig2.add_hline(y=70, line_dash="dot", line_color="red", line_width=1, row=2, col=1)
    fig2.add_hline(y=30, line_dash="dot", line_color="green", line_width=1, row=2, col=1)

fig2.update_xaxes(title_text="Date", row=2, col=1)
fig2.update_yaxes(title_text="MFI", row=1, col=1)
fig2.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
fig2.update_layout(height=600, showlegend=False)

st.plotly_chart(fig2, use_container_width=True)

# Chart 4: A/D and A/D RSI
st.subheader("Advance/Decline & RSI")
fig3 = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.6, 0.4]
)

fig3.add_trace(
    go.Scatter(x=chart_data['Trading Date'], y=chart_data['AD_15D_Sum'],
               name='A/D', line=dict(color='orange', width=2)),
    row=1, col=1
)

if 'AD_15D_RSI_21' in chart_data.columns:
    fig3.add_trace(
        go.Scatter(x=chart_data['Trading Date'], y=chart_data['AD_15D_RSI_21'],
                   name='A/D RSI', line=dict(color='purple', width=2)),
        row=2, col=1
    )

    # Add RSI reference lines
    fig3.add_hline(y=70, line_dash="dot", line_color="red", line_width=1, row=2, col=1)
    fig3.add_hline(y=30, line_dash="dot", line_color="green", line_width=1, row=2, col=1)

fig3.update_xaxes(title_text="Date", row=2, col=1)
fig3.update_yaxes(title_text="A/D", row=1, col=1)
fig3.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
fig3.update_layout(height=600, showlegend=False)

st.plotly_chart(fig3, use_container_width=True)

# Chart 5: NHNL and NHNL RSI
st.subheader("New High/New Low & RSI")
fig4 = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.6, 0.4]
)

fig4.add_trace(
    go.Scatter(x=chart_data['Trading Date'], y=chart_data['NHNL_15D_Sum'],
               name='NHNL', line=dict(color='red', width=2)),
    row=1, col=1
)

if 'NHNL_15D_RSI_21' in chart_data.columns:
    fig4.add_trace(
        go.Scatter(x=chart_data['Trading Date'], y=chart_data['NHNL_15D_RSI_21'],
                   name='NHNL RSI', line=dict(color='purple', width=2)),
        row=2, col=1
    )

    # Add RSI reference lines
    fig4.add_hline(y=70, line_dash="dot", line_color="red", line_width=1, row=2, col=1)
    fig4.add_hline(y=30, line_dash="dot", line_color="green", line_width=1, row=2, col=1)

fig4.update_xaxes(title_text="Date", row=2, col=1)
fig4.update_yaxes(title_text="NHNL", row=1, col=1)
fig4.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
fig4.update_layout(height=600, showlegend=False)

st.plotly_chart(fig4, use_container_width=True)

# Info
st.sidebar.header("About")
st.sidebar.info("""
**Indicators:**
- **VnIndex RSI (21D)**: 21-day Relative Strength Index
- **Breadth % Above MA50**: % of stocks trading above their 50-day MA
- **Money Flow Index**: Net value of stocks with >1% / <-1% change, 15-day rolling sum
- **Advance/Decline**: Net count of stocks with >1% / <-1% change, 15-day rolling sum
- **New High/New Low**: Net count of stocks at 20-day high vs 20-day low, 15-day rolling sum
- **20D Averages**: 20-day moving averages of respective indicators
""")

st.sidebar.info(f"""
**Data Info:**
- Total Records: {len(df_result)}
- Date Range: {df_result['Trading Date'].min().strftime('%Y-%m-%d')} to {df_result['Trading Date'].max().strftime('%Y-%m-%d')}
- Number of Stocks: {df_stocks['TICKER'].nunique()}
""")
