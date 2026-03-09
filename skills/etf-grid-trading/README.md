# ETF Grid Trading Skill - Summary

## Overview
This skill enables users to calculate optimized grid trading parameters for stocks and ETFs using historical market data and volatility analysis.

## Files Included
### Core Skill Definition
- `SKILL.md`: Main skill definition with usage instructions and data source information

### Scripts
- `scripts/grid_trading.py`: Self-contained grid trading parameter optimizer (no external etf-quant dependency)

### Reference Materials
- `references/strategy_guide.md`: Detailed explanation of grid trading methodology and interpretation guidance
- `references/sample_symbols.md`: Valid ETF/stock symbols with examples

## How to Use

```bash
# Basic usage with NetEase (default, no auth required)
python skills/etf-grid-trading/scripts/grid_trading.py --symbol 510050.SH --days 90

# With JSON output
python skills/etf-grid-trading/scripts/grid_trading.py --symbol 000001.SZ --days 60 --output json

# With AKShare (requires akshare package)
python skills/etf-grid-trading/scripts/grid_trading.py --symbol 510300.SH --days 180 --source akshare
```

## Dependencies
```bash
pip install numpy pandas requests
# Optional: for additional data sources
pip install akshare tushare
```