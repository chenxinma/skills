# ETF Grid Trading Skill - Summary

## Overview
This skill enables users to calculate optimized grid trading parameters for stocks and ETFs using historical market data and volatility analysis.

## Files Included
etf-grid-trading-skill
### Core Skill Definition
- `SKILL.md`: Main skill definition with usage instructions, prerequisites, and data source information

### Reference Materials
- `references/strategy_guide.md`: Detailed explanation of grid trading methodology and interpretation guidance
- `references/sample_symbols.md`: Valid ETF/stock symbols with examples of how to use the tool

## How to Deploy

1. The skill is ready to use as-is in skill-enabled environments
2. The resulting `.skill` file can be distributed or imported by skill-capable agents
3. Test with `uv run python -m etf_quant.cli.main --symbol 510050.SH --days 90 --source akshare` to verify functionality