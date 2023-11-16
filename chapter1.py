import pandas as pd
import numpy as np
from enum import Enum
from scipy.stats import norm
import matplotlib
import xlrd

matplotlib.use("TkAgg")

DEFAULT_DATA_FORMAT = "%Y-%m-%d"

# Utility function to read CSV files and convert the date column to datetime index
def pd_readcsv(filename: str, date_format=DEFAULT_DATA_FORMAT, date_index_name: str = "index") -> pd.DataFrame:
    ans = pd.read_csv(filename)
    ans.index = pd.to_datetime(ans[date_index_name], format=date_format).values
    del ans[date_index_name]
    ans.index.name = None
    return ans

# Utility function to read Excel files and convert the date column to datetime index
def read_excel(filename: str, date_format=DEFAULT_DATA_FORMAT, date_index_name: str = "index") -> pd.DataFrame:
    ans = pd.read_excel(filename, sheet_name="Accounting")
    ans.index = pd.to_datetime(ans[date_index_name], format=date_format).values
    del ans[date_index_name]
    ans.index.name = None
    return ans

# Constants for various time units
BUSINESS_DAYS_IN_YEAR = 256
WEEKS_PER_YEAR = 52.25
MONTHS_PER_YEAR = 12
SECONDS_PER_YEAR = 365.25 * 24 * 60 * 60

# Enum to define different time frequencies
Frequency = Enum("Frequency", "Natural Year Month Week BDay")
NATURAL = Frequency.Natural
YEAR = Frequency.Year
MONTH = Frequency.Month
WEEK = Frequency.Week

# Mapping of periods in a year for different frequencies
PERIODS_PER_YEAR = {
    MONTH: MONTHS_PER_YEAR,
    WEEK: WEEKS_PER_YEAR,
    YEAR: 1
}

# Returns the number of periods per year based on the provided frequency
def periods_per_year(at_frequency: Frequency):
    if at_frequency == NATURAL:
        return BUSINESS_DAYS_IN_YEAR
    else:
        return PERIODS_PER_YEAR[at_frequency]

# Calculates the number of years in the given data
def years_in_data(some_data: pd.Series) -> float:
    datediff = some_data.index[-1] - some_data.index[0]
    seconds_in_data = datediff.total_seconds()
    return seconds_in_data / SECONDS_PER_YEAR

# Removes zeros and demean the data
def demeaned_remove_zeros(x):
    x = x.copy()
    x[x == 0] = np.nan
    return x - x.mean()

# Constants for quantile calculations
LOWER_QUANT_PERCENTILE_EXTREME = 0.01
LOWER_QUANT_PERCENTILE_STD = 0.3
LOWER_NORMAL_DISTR_RATIO = norm.ppf(LOWER_QUANT_PERCENTILE_EXTREME) / norm.ppf(LOWER_QUANT_PERCENTILE_STD)

UPPER_QUANT_PERCENTILE_EXTREME = 0.99
UPPER_QUANT_PERCENTILE_STD = 0.7
UPPER_NORMAL_DISTR_RATIO = norm.ppf(UPPER_QUANT_PERCENTILE_EXTREME) / norm.ppf(UPPER_QUANT_PERCENTILE_STD)

# Calculate the quantile ratio for the lower side
def calculate_quant_ratio_lower(x):
    x_dm = demeaned_remove_zeros(x)
    raw_ratio = x_dm.quantile(LOWER_QUANT_PERCENTILE_EXTREME) / x_dm.quantile(LOWER_QUANT_PERCENTILE_STD)
    return raw_ratio / LOWER_NORMAL_DISTR_RATIO

# Calculate the quantile ratio for the upper side
def calculate_quant_ratio_upper(x):
    x_dm = demeaned_remove_zeros(x)
    raw_ratio = x_dm.quantile(UPPER_QUANT_PERCENTILE_EXTREME) / x_dm.quantile(UPPER_QUANT_PERCENTILE_STD)
    return raw_ratio / UPPER_NORMAL_DISTR_RATIO

# Calculate drawdown from the percentage returns
def calculate_drawdown(perc_return):
    cum_perc_return = perc_return.cumsum()
    max_cum_sum_perc_return = cum_perc_return.rolling(len(perc_return) + 1, min_periods=1).max()
    return max_cum_sum_perc_return - cum_perc_return

# Sum data at a specified frequency
def sum_at_frequency(perc_return: pd.Series, at_frequency: Frequency = NATURAL) -> pd.Series:
    if at_frequency == NATURAL:
        return perc_return
    at_frequency_str_dict = {
        YEAR: "Y",
        WEEK: "7D",
        MONTH: "1M",
    }
    at_frequency_str = at_frequency_str_dict[at_frequency]
    perc_return_at_freq = perc_return.resample(at_frequency_str).sum()
    return perc_return_at_freq

# Annualize the mean of returns given a certain frequency
def ann_mean_given_frequency(perc_return_at_freq: pd.Series, at_frequency: Frequency) -> float:
    mean_at_frequency = perc_return_at_freq.mean()
    periods_per_year_for_frequency = periods_per_year(at_frequency)
    annualised_mean = mean_at_frequency * periods_per_year_for_frequency
    return annualised_mean

# Annualize the standard deviation of returns given a certain frequency
def ann_std_given_frequency(perc_return_at_freq: pd.Series, at_frequency: Frequency) -> float:
    std_at_frequency = perc_return_at_freq.std()
    periods_per_year_for_frequency = periods_per_year(at_frequency)
    annualised_std = std_at_frequency * (periods_per_year_for_frequency ** 0.5)
    return annualised_std

# Calculate percentage returns based on various input parameters
def calculate_perc_returns(position_contracts_held: pd.Series, adjusted_price: pd.Series, fx_series: pd.Series,
                           multiplier: float, capital_required: pd.Series) -> pd.Series:
    return_price_points = (adjusted_price - adjusted_price.shift(1)) * position_contracts_held.shift(1)
    return_instrument_currency = return_price_points * multiplier
    fx_series_aligned = fx_series.reindex(return_instrument_currency.index, method="ffill")
    return_base_currency = return_instrument_currency * fx_series_aligned
    perc_return = return_base_currency / capital_required
    return perc_return

# Calculate various stats for the given percentage returns
def calculate_stats(perc_return: pd.Series, at_frequency: Frequency = NATURAL) -> dict:
    perc_return_at_freq = sum_at_frequency(perc_return, at_frequency=at_frequency)
    ann_mean = ann_mean_given_frequency(perc_return_at_freq, at_frequency=at_frequency)
    ann_std = ann_std_given_frequency(perc_return_at_freq, at_frequency=at_frequency)
    sharpe_ratio = ann_mean / ann_std
    skew_at_freq = perc_return_at_freq.skew()
    drawdowns = calculate_drawdown(perc_return_at_freq)
    avg_drawdown = drawdowns.mean()
    max_drawdown = drawdowns.max()
    quant_ratio_lower = calculate_quant_ratio_lower(perc_return_at_freq)
    quant_ratio_upper = calculate_quant_ratio_upper(perc_return_at_freq)
    return dict(
        ann_mean=ann_mean,
        ann_std=ann_std,
        sharpe_ratio=sharpe_ratio,
        skew=skew_at_freq,
        avg_drawdown=avg_drawdown,
        max_drawdown=max_drawdown,
        quant_ratio_lower=quant_ratio_lower,
        quant_ratio_upper=quant_ratio_upper
    )


if __name__ == '__main__':
    # Read data from CSV file
    data = pd_readcsv('sp500.csv')
    data = data.dropna()

    # Extract necessary columns for computation
    adjusted_price = data['adjusted']
    current_price = data['underlying']
    multiplier = 5
    fx_series = pd.Series(1, index=data.index)  # FX rate, 1 for USD / USD
    position_contracts_held = pd.Series(1, index=data.index)  # Applies to only strategy 1

    # Determine capital required
    capital_required = multiplier * current_price  # Applies to only strategy 1

    # Calculate percentage returns
    perc_return = calculate_perc_returns(
        position_contracts_held=position_contracts_held,
        adjusted_price=adjusted_price,
        fx_series=fx_series,
        capital_required=capital_required,
        multiplier=multiplier
    )

    # Calculate stats and print
    stats_dict = calculate_stats(perc_return, at_frequency=MONTH)

    stats_df = pd.DataFrame(list(stats_dict.items()), columns=['Identifier', 'Value'])
    print(stats_df)
