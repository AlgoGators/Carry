"""
The forecaster function takes a list of instruments and a data frame full of forecasts for each instrument.
It then addds a forecast column to each instrument's .csv file in the data folder.
"""
import pandas as pd

from chapter1 import pd_readcsv, BUSINESS_DAYS_IN_YEAR
from chapter3 import standardDeviation
from chapter4 import (
    create_fx_series_given_adjusted_prices_dict,
    calculate_variable_standard_deviation_for_risk_targeting_from_dict,
    calculate_position_series_given_variable_risk_for_dict,
)

from chapter5 import calculate_perc_returns_for_dict_with_costs
from chapter8 import apply_buffering_to_position_dict
from chapter10 import calculate_forecast_for_carry, calculate_annualised_carry, calculate_smoothed_carry,calculate_vol_adjusted_carry
from chapter10 import calculate_position_dict_with_multiple_carry_forecast_applied, calculate_combined_carry_forecast, get_data_dict_with_carry


INSTRUMENT_LIST = ['sp500', 'gas']

## Get underlying price, adjusted price, and carry price
adjusted_prices_dict, current_prices_dict, carry_prices_dict = get_data_dict_with_carry()
print(carry_prices_dict)

carry_spans = [5,20,60,120]


def calculate_capped_forecast(
    adjusted_prices_dict: dict,
    std_dev_dict: dict,
    carry_prices_dict: dict,
    carry_spans: list,
) -> dict:

    list_of_instruments = list(adjusted_prices_dict.keys())
    capped_forecast_dict = dict(
        [
            (
                instrument_code,
                calculate_combined_carry_forecast(
                    stdev_ann_perc=std_dev_dict[instrument_code],
                    carry_price=carry_prices_dict[instrument_code],
                    carry_spans=carry_spans,
                ),
            )
            for instrument_code in list_of_instruments
        ]
    )

    return capped_forecast_dict


std_dev_dict = calculate_variable_standard_deviation_for_risk_targeting_from_dict(
        adjusted_prices=adjusted_prices_dict, current_prices=current_prices_dict
    )



capped_forecasts_dict = calculate_capped_forecast(adjusted_prices_dict, std_dev_dict, carry_prices_dict, carry_spans)
print(capped_forecasts_dict)

capped_forecasts_df = pd.DataFrame(capped_forecasts_dict)
print(capped_forecasts_df)
