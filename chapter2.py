import matplotlib
import pandas as pd

try:
    from .chapter1 import pd_readcsv, BUSINESS_DAYS_IN_YEAR, calculate_perc_returns, calculate_stats, MONTH
except ImportError:
    from chapter1 import pd_readcsv, BUSINESS_DAYS_IN_YEAR, calculate_perc_returns, calculate_stats, MONTH

matplotlib.use("TkAgg")


def calculate_standard_deviation_for_risk_targeting(adjusted_price: pd.Series, current_price: pd.Series):
    """
    Calculate the annualized standard deviation of price changes for risk targeting.
    """
    # Compute daily price differences
    daily_price_changes = adjusted_price.diff()

    # Compute daily percentage changes based on previous day's price
    percentage_changes = daily_price_changes / current_price.shift(1)

    # Using only the last 30 days to get a more recent view of risk
    recent_daily_std = percentage_changes.tail(30).std()

    # Annualize the standard deviation using the number of business days in a year
    return recent_daily_std * (BUSINESS_DAYS_IN_YEAR ** .5)


def calculate_position_series_given_fixed_risk(capital: float,
                                               risk_target_tau: float,
                                               current_price: pd.Series,
                                               fx: pd.Series,
                                               multiplier: float,
                                               instrument_risk_ann_perc: float) -> pd.Series:
    """
    Calculate the position size (in contracts) for a given fixed risk target.
    """
    # Position calculation formula, derived from the concept of fixed fractional trading
    position_in_contracts = (capital * risk_target_tau) / (multiplier * current_price * fx * instrument_risk_ann_perc)

    return position_in_contracts


def calculate_minimum_capital(multiplier: float,
                              price: float,
                              fx: float,
                              instrument_risk_ann_perc: float,
                              risk_target: float,
                              contracts: int = 4):
    """
    Calculate the minimum capital required to hold a certain number of contracts for a given risk target.
    """
    # Minimum capital requirement formula for holding 'contracts' number of contracts
    minimum_capital = contracts * multiplier * price * fx * instrument_risk_ann_perc / risk_target

    return minimum_capital


if __name__ == '__main__':
    # Read the dataset for SP500
    data = pd_readcsv('sp500.csv')
    data = data.dropna()

    # Define necessary data series and constants
    adjusted_price = data.adjusted
    current_price = data.underlying
    multiplier = 5
    risk_target_tau = .2
    fx_series = pd.Series(1, index=data.index)  # FX rate, 1 for USD / USD since the asset and capital are both in USD
    capital = 100000

    # Calculate the instrument's annualized risk based on the most recent data
    instrument_risk = calculate_standard_deviation_for_risk_targeting(adjusted_price=adjusted_price,
                                                                      current_price=current_price)

    # Compute the position size in contracts based on fixed risk approach
    position_contracts_held = calculate_position_series_given_fixed_risk(
        capital=capital,
        fx=fx_series,
        instrument_risk_ann_perc=instrument_risk,
        risk_target_tau=risk_target_tau,
        multiplier=multiplier,
        current_price=current_price)

    # Calculate daily percentage returns for the strategy
    perc_return = calculate_perc_returns(
        position_contracts_held=position_contracts_held,
        adjusted_price=adjusted_price,
        fx_series=fx_series,
        capital_required=capital,
        multiplier=multiplier
    )

    # Compute stats for daily and monthly frequencies
    stats_dict = calculate_stats(perc_return)
    stats_dict2 = calculate_stats(perc_return, MONTH)

    # Convert the statistics to pandas DataFrame for a cleaner display
    stats_df = pd.DataFrame(list(stats_dict.items()), columns=['Identifier', 'Value'])
    stats_df2 = pd.DataFrame(list(stats_dict2.items()), columns=['Identifier', 'Value'])

    # Display the computed stats
    print(stats_df, "\n")
    print(stats_df2, "\n")

    # Print the minimum capital requirement for holding a default of 4 contracts
    print("Minimum Capital: $", round(calculate_minimum_capital(multiplier=multiplier,
                                                                risk_target=risk_target_tau,
                                                                fx=1,
                                                                instrument_risk_ann_perc=instrument_risk,
                                                                price=current_price.iloc[-1]), 2), sep='')
