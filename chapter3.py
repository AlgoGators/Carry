import matplotlib
from copy import copy
import pandas as pd
from chapter1 import (
    pd_readcsv,
    BUSINESS_DAYS_IN_YEAR,
    calculate_perc_returns,
    calculate_stats,
    MONTH,
)
from chapter2 import calculate_minimum_capital

matplotlib.use("TkAgg")

# Function to calculate a variable standard deviation based on adjusted and current prices.
# This function helps in dynamically adapting to market conditions.
def calculate_variable_standard_deviation_for_risk_targeting(
    adjusted_price: pd.Series,
    current_price: pd.Series,
    use_perc_returns: bool = True,
    annualise_stdev: bool = True,
) -> pd.Series:
    # Calculate daily returns using either percentage-based returns or price returns.
    if use_perc_returns:
        daily_returns = calculate_percentage_returns(
            adjusted_price=adjusted_price, current_price=current_price
        )
    else:
        daily_returns = calculate_daily_returns(adjusted_price=adjusted_price)

    # Compute an Exponential Weighted Moving Standard Deviation over 32 days.
    # This allows more weight to be given to recent observations.
    daily_exp_std_dev = daily_returns.ewm(span=32).std()

    # Decide if the standard deviation should be annualized or not.
    if annualise_stdev:
        annualisation_factor = BUSINESS_DAYS_IN_YEAR ** 0.5
    else:
        annualisation_factor = 1

    annualised_std_dev = daily_exp_std_dev * annualisation_factor

    # Combine the annualized standard deviation with a 10-year rolling average to smooth out
    # extreme values and get a long-term view of the volatility.
    ten_year_vol = annualised_std_dev.rolling(
        BUSINESS_DAYS_IN_YEAR * 10, min_periods=1
    ).mean()
    weighted_vol = 0.3 * ten_year_vol + 0.7 * annualised_std_dev

    return weighted_vol

# Calculate daily percentage returns.
def calculate_percentage_returns(
    adjusted_price: pd.Series, current_price: pd.Series
) -> pd.Series:
    daily_price_changes = calculate_daily_returns(adjusted_price)
    percentage_changes = daily_price_changes / current_price.shift(1)

    return percentage_changes

# Function to calculate the daily returns.
def calculate_daily_returns(adjusted_price: pd.Series) -> pd.Series:
    return adjusted_price.diff()

# Class to represent the standard deviation.
# This is the core of the risk measurement for this strategy.
class standardDeviation(pd.Series):
    def __init__(
        self,
        adjusted_price: pd.Series,
        current_price: pd.Series,
        use_perc_returns: bool = True,
        annualise_stdev: bool = True,
    ):
        # Calculate the standard deviation for the given parameters.
        stdev = calculate_variable_standard_deviation_for_risk_targeting(
            adjusted_price=adjusted_price,
            current_price=current_price,
            annualise_stdev=annualise_stdev,
            use_perc_returns=use_perc_returns,
        )
        super().__init__(stdev)

        # Store the input parameters as private properties.
        self._use_perc_returns = use_perc_returns
        self._annualised = annualise_stdev
        self._current_price = current_price

    # Compute the daily risk in price terms. This is used for risk management and position sizing.
    def daily_risk_price_terms(self):
        stdev = copy(self)
        if self.annualised:
            stdev = stdev / (BUSINESS_DAYS_IN_YEAR ** 0.5)

        if self.use_perc_returns:
            stdev = stdev * self.current_price

        return stdev

    # Compute the annual risk in price terms.
    def annual_risk_price_terms(self):
        stdev = copy(self)
        if not self.annualised:
            stdev = stdev * (BUSINESS_DAYS_IN_YEAR ** 0.5)

        if self.use_perc_returns:
            stdev = stdev * self.current_price

        return stdev

    # Properties to access private variables.
    @property
    def annualised(self) -> bool:
        return self._annualised

    @property
    def use_perc_returns(self) -> bool:
        return self._use_perc_returns

    @property
    def current_price(self) -> pd.Series:
        return self._current_price

# Calculate the number of contracts to hold based on the risk target and instrument risk.
def calculate_position_series_given_variable_risk(
    capital: float,
    risk_target_tau: float,
    fx: pd.Series,
    multiplier: float,
    instrument_risk: standardDeviation,
) -> pd.Series:
    daily_risk_price_terms = instrument_risk.daily_risk_price_terms()

    # Position is derived from the risk target, capital, instrument risk, and other parameters.
    return (
        capital
        * risk_target_tau
        / (multiplier * fx * daily_risk_price_terms * (BUSINESS_DAYS_IN_YEAR ** 0.5))
    )

# Function to calculate the annualized turnover based on position changes.
def calculate_turnover(position, average_position):
    daily_trades = position.diff()
    as_proportion_of_average = daily_trades.abs() / average_position.shift(1)
    average_daily = as_proportion_of_average.mean()
    annualised_turnover = average_daily * BUSINESS_DAYS_IN_YEAR

    return annualised_turnover

# Main logic to bring all the functions and classes together.
if __name__ == "__main__":
    # Read the data for S&P 500 and drop missing values.
    data = pd_readcsv("sp500.csv")
    data = data.dropna()

    adjusted_price = data.adjusted
    current_price = data.underlying
    multiplier = 5
    risk_target_tau = 0.2
    fx_series = pd.Series(1, index=data.index)  # FX rate for USD / USD.

    capital = 100000

    # Instantiate the standard deviation class with given parameters.
    instrument_risk = standardDeviation(
        adjusted_price=adjusted_price,
        current_price=current_price,
        use_perc_returns=True,
        annualise_stdev=True,
    )

    # Compute the number of contracts to hold for each day.
    position_contracts_held = calculate_position_series_given_variable_risk(
        capital=capital,
        fx=fx_series,
        instrument_risk=instrument_risk,
        risk_target_tau=risk_target_tau,
        multiplier=multiplier,
    )

    perc_return = calculate_perc_returns(
        position_contracts_held=position_contracts_held,
        adjusted_price=adjusted_price,
        fx_series=fx_series,
        capital_required=capital,
        multiplier=multiplier,
    )

    # Compute statistics for the returns.
    stats_dict = calculate_stats(perc_return)
    stats_dict2 = calculate_stats(perc_return, MONTH)

    # Convert statistics to dataframes for easier display.
    stats_df = pd.DataFrame(list(stats_dict.items()), columns=['Identifier', 'Value'])
    stats_df2 = pd.DataFrame(list(stats_dict2.items()), columns=['Identifier', 'Value'])

    # Print the results.
    print(stats_df, "\n")
    print(stats_df2, "\n")

    # Calculate and print the minimum capital required.
    print("Minimum Capital: $",round(
        calculate_minimum_capital(
            multiplier=multiplier,
            risk_target=risk_target_tau,
            fx=1,
            instrument_risk_ann_perc=instrument_risk.daily_risk_price_terms().iloc[-1],
            price=current_price.iloc[-1],
        ),2), sep="")

    # Calculate and print the annualized turnover.
    print("Turnover: ",round(
        calculate_turnover(
            position_contracts_held, average_position=position_contracts_held
        ),3)
    )