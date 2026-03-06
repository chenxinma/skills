# Valid ETF and Stock Symbols for Testing

## Popular Chinese ETFs
- 510050.SH (上证50ETF) - Shanghai 50 ETF
- 510300.SH (沪深300ETF) - CSI 300 ETF  
- 510500.SH (中证500ETF) - CSI 500 ETF
- 512100.SH (中证1000ETF) - CSI 1000 ETF
- 512690.SH (酒ETF) - Beverage & Alcoholic Drinks ETF
- 513090.SH (券商ETF) - Securities Companies ETF
- 512010.SH (医药ETF) - Healthcare/Generic Medicine ETF
- 512880.SH (证券ETF) - Securities Industry ETF
- 513100.SH (纳指ETF) - NASDAQ Index ETF
- 159919.SZ (300ETF) - ChiNext 300 ETF

## Popular Chinese Stocks
- 000001.SZ (平安银行) - Ping An Bank  
- 000858.SZ (五粮液) - Wuliangye
- 600036.SH (招商银行) - China Merchants Bank
- 600519.SH (贵州茅台) - Kweichow Moutai
- 000002.SZ (万科A) - Vanke A
- 601398.SH (工商银行) - ICBC
- 600030.SH (中信证券) - CITIC Construction Investment
- 300750.SZ (宁德时代) - Contemporary Amperex Tech
- 002594.SZ (比亚迪) - BYD Company
- 601166.SH (兴业银行) - Industrial Bank

## Analysis Period Recommendations
- Short-term (20-60 days): For high-volatility, momentum-driven symbols
- Medium-term (60-180 days): Balanced volatility for most equity instruments
- Long-term (180+ days): For lower-volatility blue-chip stocks and broad market ETFs

## Sample Commands
```
# Calculate parameters for Shanghai 50 ETF
uv run python -m etf_quant.cli.main --symbol 510050.SH --days 90 --source akshare

# Calculate parameters for Moutai (short-term volatility focus)
uv run python -m etf_quant.cli.main --symbol 600519.SH --days 30 --output json --source netease

# Calculate parameters for NASDAQ ETF (long-term horizon)
uv run python -m etf_quant.cli.main --symbol 513100.SH --days 180 --source akshare --output csv

# Full analysis for BYD stock
uv run python -m etf_quant.cli.main --symbol 300750.SZ --days 120 --source tushare
```