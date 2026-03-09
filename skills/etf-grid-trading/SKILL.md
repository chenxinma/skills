---
name: etf-grid-trading-optimizer
description: Calculate optimized grid trading parameters for user-specified stocks or ETFs based on historical volatility. Use when analyzing or recommending grid trading strategies for ETFs or stocks by specifying the symbol, analysis period, and data source.
---

# ETF Grid Trading Parameter Optimization

This skill helps calculate optimal grid trading parameters based on historical market data. It analyzes volatility and suggests appropriate grid spacing and number of grids for a passive investment strategy.

## What This Skill Does

Calculates key grid trading parameters based on historical market data:
- **Grid Size**: Distance between price levels
- **Number of Grids**: Total number of grids needed
- **Price Range**: Min/max price levels based on volatility
- **Historical Volatility**: Calculated from market data
- **Optimization**: Based on statistical measures

## When to Use This Skill

- When users want to implement a grid trading strategy for ETFs/stocks
- To calculate optimal grid distances based on historical volatility
- For risk assessment in volatile market conditions
- When setting up automated trading systems or alerts

## Prerequisites

- Python environment with required packages: numpy, pandas, requests
- Optional: akshare (for AKShare data source), tushare (for TuShare data source)
- Symbols must use Chinese exchange format (e.g., 000001.SZ, 510050.SH)

## Data Sources

The system supports three data sources:

### NetEase Finance (Default)
- Free and stable API
- Format: `.SH` (Shanghai) or `.SZ` (Shenzhen)
- No authentication required
- Works best for Chinese market securities

### AKShare
- High-quality open-source Chinese market data
- No authentication required
- Comprehensive historical data
- Requires `akshare` package installed

### TuShare
- Requires API token
- More comprehensive data
- Requires `tushare` package and valid token
- Higher rate limits

## Usage Pattern

1. Ask the user for the stock/ETF symbol in correct format
2. Ask for analysis period in days (default is 90)
3. Execute the grid parameter calculation
4. Interpret and explain the results
5. Provide recommendations for grid trading strategy

### Example Commands

Basic usage with default parameters (NetEase source):
```bash
python skills/etf-grid-trading/scripts/grid_trading.py --symbol 510050.SH --days 90
```

With JSON output (for further processing):
```bash
python skills/etf-grid-trading/scripts/grid_trading.py --symbol 000001.SZ --days 60 --output json --source netease
```

CSV formatted output:
```bash
python skills/etf-grid-trading/scripts/grid_trading.py --symbol 510500.SH --days 180 --output csv --source akshare
```

With TuShare (requires token):
```bash
python skills/etf-grid-trading/scripts/grid_trading.py --symbol 510050.SH --days 90 --source tushare --token YOUR_TOKEN
```

## Key Metrics Explained

- **Historical Volatility**: Statistical measure of price fluctuations
- **Grid Size**: Dollar amount between each buy/sell level
- **Number of Grids**: Total buy/sell points in the range
- **Price Range**: Expected trading range based on volatility
- **Current Price**: Latest closing price for reference

## Interpreting Results

- Higher volatility requires larger grid sizes to reduce transaction frequency
- Higher volatility may require more grids to cover wider price ranges
- Riskier assets need wider price range coverage
- Conservative trading may require adjusting grid parameters beyond recommendations

### Risk Considerations

- Never invest more than you can afford to lose
- Grid trading may amplify losses in continuously trending markets
- Adjust recommendations based on personal risk tolerance
- Monitor market conditions for major changes not captured in historical data