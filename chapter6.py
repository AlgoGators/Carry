import matplotlib

matplotlib.use("TkAgg")

from copy import copy
from scipy.stats import linregress
import pandas as pd

try:
    from .chapter1 import calculate_stats, MONTH, BUSINESS_DAYS_IN_YEAR
    from .chapter3 import standardDeviation
    from .chapter4 import (
        get_data_dict,
        calculate_variable_standard_deviation_for_risk_targeting_from_dict,
        calculate_position_series_given_variable_risk_for_dict,
        create_fx_series_given_adjusted_prices_dict,
        aggregate_returns,
    )
except ImportError:
    from chapter1 import calculate_stats, MONTH, BUSINESS_DAYS_IN_YEAR
    from chapter3 import standardDeviation
    from chapter4 import (
        get_data_dict,
        calculate_variable_standard_deviation_for_risk_targeting_from_dict,
        calculate_position_series_given_variable_risk_for_dict,
        create_fx_series_given_adjusted_prices_dict,
        aggregate_returns,
    )

def calculate_position_dict_with_trend_filter_applied(adjusted_prices_dict: dict,
                                                      average_position_contracts_dict: dict) -> dict:
    list_of_instruments = list(adjusted_prices_dict.keys())
    position_dict_with_trend_filter = dict(
        [
            (
                instrument_code,
                calculate_position_with_trend_filter_applied(
                    adjusted_prices_dict[instrument_code],
                    average_position_contracts_dict[instrument_code],
                ),
            )
            for instrument_code in list_of_instruments
        ]
    )
    return position_dict_with_trend_filter

# Function to apply a trend filter to a specific instrument's positions.
# It zeroes out any positions during bearish trends (indicated by negative EWMAC values).
def calculate_position_with_trend_filter_applied(adjusted_price: pd.Series, average_position: pd.Series) -> pd.Series:
    # Copy the positions to ensure original data isn't mutated.
    filtered_position = copy(average_position)
    ewmac_values = ewmac(adjusted_price)
    bearish = ewmac_values < 0
    filtered_position[bearish] = 0
    return filtered_position

# EWMAC (Exponentially Weighted Moving Average Crossover) function.
# The difference between fast and slow exponential moving averages (EMAs).
# Positive values indicate bullish trends, while negative values indicate bearish trends.
def ewmac(adjusted_price: pd.Series, fast_span=16, slow_span=64) -> pd.Series:
    slow_ewma = adjusted_price.ewm(span=slow_span, min_periods=2).mean()
    fast_ewma = adjusted_price.ewm(span=fast_span, min_periods=2).mean()
    return fast_ewma - slow_ewma

# Calculate percentage returns for each instrument in the dictionary after considering costs.
# Returns include costs like contract costs and adjust for currency effects.
def calculate_perc_returns_for_dict_with_costs(position_contracts_dict: dict, adjusted_prices: dict, multipliers: dict,
                                               fx_series: dict, capital: float, cost_per_contract_dict: dict,
                                               std_dev_dict: dict) -> dict:
    perc_returns_dict = dict(
        [
            (
                instrument_code,
                calculate_perc_returns_with_costs(
                    position_contracts_held=position_contracts_dict[instrument_code],
                    adjusted_price=adjusted_prices[instrument_code],
                    multiplier=multipliers[instrument_code],
                    fx_series=fx_series[instrument_code],
                    capital_required=capital,
                    cost_per_contract=cost_per_contract_dict[instrument_code],
                    stdev_series=std_dev_dict[instrument_code],
                ),
            )
            for instrument_code in position_contracts_dict.keys()
        ]
    )
    return perc_returns_dict

# Function to calculate the percentage returns of a single instrument after adjusting for costs
# and foreign exchange rates.
def calculate_perc_returns_with_costs(position_contracts_held: pd.Series, adjusted_price: pd.Series,
                                      fx_series: pd.Series, stdev_series: standardDeviation, multiplier: float,
                                      capital_required: float, cost_per_contract: float) -> pd.Series:
    # Calculate the return based on the change in price and positions held from the previous day.
    precost_return_price_points = (adjusted_price - adjusted_price.shift(1)) * position_contracts_held.shift(1)

    # Convert price returns to monetary returns using the contract multiplier.
    precost_return_instrument_currency = precost_return_price_points * multiplier

    # Calculate the costs deflated by the instrument's volatility.
    historic_costs = calculate_costs_deflated_for_vol(stddev_series=stdev_series, cost_per_contract=cost_per_contract,
                                                      position_contracts_held=position_contracts_held)

    # Align the dates of cost data with the returns data.
    historic_costs_aligned = historic_costs.reindex(precost_return_instrument_currency.index, method="ffill")

    # Subtract the cost from the return to get the net return in the instrument's currency.
    return_instrument_currency = (precost_return_instrument_currency - historic_costs_aligned)

    # Align the dates of the foreign exchange data with the returns data.
    fx_series_aligned = fx_series.reindex(return_instrument_currency.index, method="ffill")

    # Convert the return to the base currency using the foreign exchange rate.
    return_base_currency = return_instrument_currency * fx_series_aligned

    # Convert the monetary return to a percentage of the total capital.
    perc_return = return_base_currency / capital_required
    return perc_return

# Calculate the historic costs for an instrument, adjusted for its volatility.
# Deflate costs in order to express them in terms of risk-adjusted units or to account for the varying risk
# across different assets or time periods.
def calculate_costs_deflated_for_vol(stddev_series: standardDeviation, cost_per_contract: float,
                                     position_contracts_held: pd.Series) -> pd.Series:
    # Round positions to whole numbers and compute the change in positions to calculate trades.
    round_position_contracts_held = position_contracts_held.round()
    position_change = (round_position_contracts_held - round_position_contracts_held.shift(1))
    abs_trades = position_change.abs()

    # Adjust the per-contract cost for volatility.
    historic_cost_per_contract = calculate_deflated_costs(stddev_series=stddev_series,
                                                          cost_per_contract=cost_per_contract)

    # Align the dates of cost data with the trades data.
    historic_cost_per_contract_aligned = historic_cost_per_contract.reindex(abs_trades.index, method="ffill")

    # Multiply the number of trades by the cost per trade to get the total cost.
    historic_costs = abs_trades * historic_cost_per_contract_aligned
    return historic_costs

# Adjust the per-contract cost based on the instrument's volatility.
def calculate_deflated_costs(stddev_series: standardDeviation, cost_per_contract: float) -> pd.Series:
    # Calculate daily price volatility.
    stdev_daily_price = stddev_series.daily_risk_price_terms()
    final_stdev = stdev_daily_price.iloc[-1]

    # Deflate the cost based on how current volatility compares to the final volatility.
    cost_deflator = stdev_daily_price / final_stdev
    historic_cost_per_contract = cost_per_contract * cost_deflator
    return historic_cost_per_contract


def calculate_position_dict_with_symmetric_trend_filter_applied(
    adjusted_prices_dict: dict,
    average_position_contracts_dict: dict,
) -> dict:

    list_of_instruments = list(adjusted_prices_dict.keys())
    position_dict_with_trend_filter = dict(
        [
            (
                instrument_code,
                calculate_position_with_symmetric_trend_filter_applied(
                    adjusted_prices_dict[instrument_code],
                    average_position_contracts_dict[instrument_code],
                ),
            )
            for instrument_code in list_of_instruments
        ]
    )

    return position_dict_with_trend_filter


def calculate_position_with_symmetric_trend_filter_applied(
    adjusted_price: pd.Series, average_position: pd.Series
) -> pd.Series:

    filtered_position = copy(average_position)
    ewmac_values = ewmac(adjusted_price)
    bearish = ewmac_values < 0
    filtered_position[bearish] = -filtered_position[bearish]

    return filtered_position


def long_only_returns(
    adjusted_prices_dict: dict,
    std_dev_dict: dict,
    average_position_contracts_dict: dict,
    fx_series_dict: dict,
    cost_per_contract_dict: dict,
    multipliers: dict,
    capital: float,
) -> pd.Series:

    perc_return_dict = calculate_perc_returns_for_dict_with_costs(
        position_contracts_dict=average_position_contracts_dict,
        fx_series=fx_series_dict,
        multipliers=multipliers,
        capital=capital,
        adjusted_prices=adjusted_prices_dict,
        cost_per_contract_dict=cost_per_contract_dict,
        std_dev_dict=std_dev_dict,
    )

    perc_return_agg = aggregate_returns(perc_return_dict)

    return perc_return_agg


if __name__ == "__main__":
    ## Get the files from:
    # https://gitfront.io/r/user-4000052/iTvUZwEUN2Ta/AFTS-CODE/blob/sp500.csv
    # and https://gitfront.io/r/user-4000052/iTvUZwEUN2Ta/AFTS-CODE/blob/US10.csv
    adjusted_prices_dict, current_prices_dict = get_data_dict()

    multipliers = dict(sp500=5, us10=1000)
    risk_target_tau = 0.2
    fx_series_dict = create_fx_series_given_adjusted_prices_dict(adjusted_prices_dict)

    capital = 1000000
    idm = 1.5
    instrument_weights = dict(sp500=0.5, us10=0.5)
    cost_per_contract_dict = dict(sp500=0.875, us10=5)

    std_dev_dict = calculate_variable_standard_deviation_for_risk_targeting_from_dict(
        adjusted_prices=adjusted_prices_dict, current_prices=current_prices_dict
    )

    average_position_contracts_dict = (
        calculate_position_series_given_variable_risk_for_dict(
            capital=capital,
            risk_target_tau=risk_target_tau,
            idm=idm,
            weights=instrument_weights,
            std_dev_dict=std_dev_dict,
            fx_series_dict=fx_series_dict,
            multipliers=multipliers,
        )
    )

    position_contracts_dict = (
        calculate_position_dict_with_symmetric_trend_filter_applied(
            adjusted_prices_dict=adjusted_prices_dict,
            average_position_contracts_dict=average_position_contracts_dict,
        )
    )

    ## note doesn't include roll costs
    perc_return_dict = calculate_perc_returns_for_dict_with_costs(
        position_contracts_dict=position_contracts_dict,
        fx_series=fx_series_dict,
        multipliers=multipliers,
        capital=capital,
        adjusted_prices=adjusted_prices_dict,
        cost_per_contract_dict=cost_per_contract_dict,
        std_dev_dict=std_dev_dict,
    )

    print(calculate_stats(perc_return_dict["sp500"]))

    perc_return_agg = aggregate_returns(perc_return_dict)
    print(calculate_stats(perc_return_agg))

    long_only = long_only_returns(
        adjusted_prices_dict=adjusted_prices_dict,
        average_position_contracts_dict=average_position_contracts_dict,
        capital=capital,
        cost_per_contract_dict=cost_per_contract_dict,
        fx_series_dict=fx_series_dict,
        multipliers=multipliers,
        std_dev_dict=std_dev_dict,
    )

    results = linregress(long_only, perc_return_agg)
    print("Beta %f" % results.slope)
    daily_alpha = results.intercept
    print("Annual alpha %.2f%%" % (100 * daily_alpha * BUSINESS_DAYS_IN_YEAR))