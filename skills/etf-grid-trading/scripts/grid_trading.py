#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "numpy", "pandas", "akshare", "tushare", "requests"
# ]
# ///
"""
ETF Grid Trading Parameter Optimization Script

This script calculates optimal grid trading parameters based on historical market data.
It analyzes volatility and suggests appropriate grid spacing and number of grids.

Data Sources:
- NetEase Finance (free, no auth required)
- AKShare (open-source, Chinese market data)
- TuShare (requires token)
"""

# Standard library
import argparse
import json
import math
import sys
from datetime import datetime, timedelta
from typing import Tuple, Optional

# Third-party
import numpy as np
import pandas as pd
import requests


class DataFetcher:
    """Base class for data fetchers."""

    def get_historical_data(self, symbol: str, days: int) -> pd.DataFrame:
        """Fetch historical price data for given symbol and time period."""
        raise NotImplementedError


class NetEaseFetcher(DataFetcher):
    """Fetch data from NetEase Finance API."""

    def get_historical_data(self, symbol: str, days: int) -> pd.DataFrame:
        """Fetch historical data from NetEase Finance API."""
        try:
            _symbol = self._convert_symbol(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            return self._get_history_data(_symbol, days, start_date, end_date)
        except Exception as e:
            print(f"NetEaseFetcher error: {e}")
            return pd.DataFrame()

    def _convert_symbol(self, symbol: str) -> str:
        """Convert symbol to NetEase format (e.g., 000001.SZ -> sz000001)"""
        if symbol.endswith(".SZ"):
            return f"sz{symbol.replace('.SZ', '')}"
        elif symbol.endswith(".SH"):
            return f"sh{symbol.replace('.SH', '')}"
        else:
            if symbol.startswith("6"):
                return f"sh{symbol}"
            elif symbol.startswith("0") or symbol.startswith("3"):
                return f"sz{symbol}"
            return symbol

    def _get_history_data(
        self, symbol: str, days: int, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame:
        """Get historical data from NetEase Finance API"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://money.163.com/",
        }

        stock_code = symbol[2:]
        netease_stock_url = f"http://quotes.money.163.com/service/chddata.html?code={stock_code}&start={start_date.strftime('%Y%m%d')}&end={end_date.strftime('%Y%m%d')}&fields=TCLOSE;HIGH;LOW;TOPEN;VOTURNOVER"

        try:
            response = requests.get(netease_stock_url, headers=headers)
            response.encoding = "gbk"

            lines = response.text.strip().split("\n")[1:]

            if len(lines) <= 1:
                return pd.DataFrame()

            data_list = []
            for line in lines:
                if line.strip():
                    parts = line.split(",")
                    if len(parts) >= 11:
                        date_str = parts[0].strip()
                        try:
                            open_price = (
                                float(parts[3]) if parts[3] not in ("", "None") else 0
                            )
                            high_price = (
                                float(parts[4]) if parts[4] not in ("", "None") else 0
                            )
                            low_price = (
                                float(parts[5]) if parts[5] not in ("", "None") else 0
                            )
                            close_price = (
                                float(parts[6]) if parts[6] not in ("", "None") else 0
                            )
                            volume = (
                                float(parts[10]) if parts[10] not in ("", "None") else 0
                            )

                            if close_price == 0:
                                continue

                            data_list.append(
                                {
                                    "trade_date": date_str,
                                    "open": open_price,
                                    "high": high_price,
                                    "low": low_price,
                                    "close": close_price,
                                    "vol": volume,
                                }
                            )
                        except ValueError:
                            continue

            if data_list:
                df = pd.DataFrame(data_list)
                df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.strftime(
                    "%Y-%m-%d"
                )
                return df.sort_values("trade_date").reset_index(drop=True)

        except Exception as e:
            print(f"Compatible API error: {e}")

        return pd.DataFrame()


class AKShareFetcher(DataFetcher):
    """Fetch data from AKShare."""

    def __init__(self):
        try:
            import akshare as ak

            self.ak = ak
        except ImportError:
            raise ImportError(
                "AKShare is not available. Please install akshare or use NetEase instead."
            )

    def get_historical_data(self, symbol: str, days: int) -> pd.DataFrame:
        """Fetch historical data from AKShare."""
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days + 30)).strftime("%Y%m%d")

        try:
            if symbol.endswith(".SZ") or symbol.endswith(".SH"):
                stock_code = symbol.replace(".SZ", "").replace(".SH", "")
                exchange = "sz" if symbol.endswith(".SZ") else "sh"
                full_symbol = f"{exchange}{stock_code}"
            else:
                full_symbol = symbol

            df = self.ak.stock_zh_a_hist(
                symbol=full_symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq",
            )

            if df is not None and len(df) > 0:
                df = df.rename(
                    columns={
                        "日期": "trade_date",
                        "开盘": "open",
                        "最高": "high",
                        "最低": "low",
                        "收盘": "close",
                        "成交量": "vol",
                    }
                )
                df["trade_date"] = df["trade_date"].astype(str)
                return df[["trade_date", "open", "high", "low", "close", "vol"]]
        except Exception as e:
            print(f"AKShare error: {e}")

        return pd.DataFrame()


class TushareFetcher(DataFetcher):
    """Fetch data from TuShare (requires token)."""

    def __init__(self, token: Optional[str] = None):
        try:
            import tushare as ts

            self.ts = ts
            if token:
                ts.set_token(token)
        except ImportError:
            raise ImportError(
                "TuShare is not available. Please install tushare or use another source."
            )

    def get_historical_data(self, symbol: str, days: int) -> pd.DataFrame:
        """Fetch historical data from TuShare."""
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days + 30)).strftime("%Y%m%d")

        try:
            df = self.ts.pro_bar(
                ts_code=symbol,
                adj="qfq",
                start_date=start_date,
                end_date=end_date,
                freq="D",
            )
            if df is not None and len(df) > 0:
                df = df.sort_values("trade_date")
                return df[["trade_date", "open", "high", "low", "close", "vol"]]
        except Exception as e:
            print(f"Tushare error: {e}")

        return pd.DataFrame()


def calculate_historical_volatility(df: pd.DataFrame, window: int = 20) -> float:
    """
    Calculate historical volatility based on close prices.

    Args:
        df: DataFrame with 'close' column
        window: Rolling window size for volatility calculation

    Returns:
        Annualized historical volatility as a decimal
    """
    if len(df) < window:
        window = len(df)

    df = df.copy()
    df["log_returns"] = np.log(df["close"] / df["close"].shift(1))
    df = df.dropna()

    if len(df) == 0:
        return 0.0

    rolling_vol = df["log_returns"].rolling(window=window).std()
    avg_vol = rolling_vol.dropna().mean()
    annualized_vol = avg_vol * np.sqrt(252)

    return float(annualized_vol) if not np.isnan(annualized_vol) else 0.0


def optimize_grid_parameters(
    current_price: float, volatility: float, days: int
) -> Tuple[float, int]:
    """
    Optimize grid trading parameters based on historical volatility.

    Args:
        current_price: Current market price of the asset
        volatility: Annualized historical volatility (as decimal)
        days: Analysis period in days

    Returns:
        Tuple of (grid_size, number_of_grids)
    """
    period_volatility = volatility * math.sqrt(days / 252)
    base_grid_pct = max(0.01, min(0.1, period_volatility * 0.5))
    grid_size = current_price * base_grid_pct
    expected_range = current_price * period_volatility * 2
    num_grids = max(5, min(20, int(expected_range / grid_size)))

    return round(grid_size, 2), num_grids


def fetch_data(
    symbol: str, days: int, source: str, token: Optional[str] = None
) -> pd.DataFrame:
    """Fetch historical data based on source selection."""
    if source == "tushare":
        fetcher = TushareFetcher(token)
    elif source == "netease":
        fetcher = NetEaseFetcher()
    else:
        try:
            fetcher = AKShareFetcher()
        except ImportError:
            print("AKShare not available, falling back to NetEase")
            fetcher = NetEaseFetcher()

    return fetcher.get_historical_data(symbol, days)


def format_output(
    symbol: str,
    current_price: float,
    volatility: float,
    days: int,
    grid_size: float,
    num_grids: int,
    output_format: str,
) -> None:
    """Format and print results."""
    price_range_low = current_price - (num_grids // 2) * grid_size
    price_range_high = current_price + (num_grids // 2) * grid_size

    if output_format == "json":
        result = {
            "symbol": symbol,
            "current_price": current_price,
            "volatility": volatility,
            "analysis_days": days,
            "grid_size": grid_size,
            "number_of_grids": num_grids,
            "price_range": [price_range_low, price_range_high],
        }
        print(json.dumps(result, indent=2))
    elif output_format == "csv":
        print(f"symbol,current_price,volatility,days,grid_size,num_grids")
        print(f"{symbol},{current_price},{volatility},{days},{grid_size},{num_grids}")
    else:
        print(f"Grid Trading Parameters for {symbol}:")
        print(f"  Current Price: ${current_price:.2f}")
        print(f"  Historical Volatility: {volatility:.2%}")
        print(f"  Analysis Period: {days} days")
        print(f"  Recommended Grid Size: ${grid_size:.2f}")
        print(f"  Number of Grids: {num_grids}")
        print(
            f"  Suggested Price Range: ${price_range_low:.2f} - ${price_range_high:.2f}"
        )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Grid trading parameter inference system."
    )
    parser.add_argument(
        "-s", "--symbol", required=True, help="Stock/ETF symbol (e.g., 000001.SZ)"
    )
    parser.add_argument(
        "-d",
        "--days",
        type=int,
        default=90,
        help="Analysis period in days (default: 90)",
    )
    parser.add_argument(
        "-src",
        "--source",
        choices=["tushare", "akshare", "netease"],
        default="netease",
        help="Data source (default: netease)",
    )
    parser.add_argument(
        "-o",
        "--output",
        choices=["json", "csv", "text"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument("-t", "--token", help="TuShare API token (optional)")

    args = parser.parse_args()

    df = fetch_data(args.symbol, args.days, args.source, args.token)
    if df.empty:
        print(f"Error: No data found for {args.symbol}", file=sys.stderr)
        sys.exit(1)

    current_price = float(df["close"].iloc[-1])
    volatility = calculate_historical_volatility(df, window=min(20, len(df)))
    grid_size, num_grids = optimize_grid_parameters(
        current_price, volatility, args.days
    )

    format_output(
        args.symbol,
        current_price,
        volatility,
        args.days,
        grid_size,
        num_grids,
        args.output,
    )


if __name__ == "__main__":
    main()
