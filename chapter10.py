import matplotlib
import numpy as np

matplotlib.use("TkAgg")

import pandas as pd
from chapter1 import pd_readcsv, BUSINESS_DAYS_IN_YEAR
from chapter3 import standardDeviation
from chapter4 import (
    create_fx_series_given_adjusted_prices_dict,
    calculate_variable_standard_deviation_for_risk_targeting_from_dict,
    calculate_position_series_given_variable_risk_for_dict,
)

from chapter5 import calculate_perc_returns_for_dict_with_costs

def apply_buffering_to_position_dict(
    position_contracts_dict: dict, average_position_contracts_dict: dict
) -> dict:

    instrument_list = list(position_contracts_dict.keys())
    buffered_position_dict = dict(
        [
            (
                instrument_code,
                apply_buffering_to_positions(
                    position_contracts=position_contracts_dict[instrument_code],
                    average_position_contracts=average_position_contracts_dict[
                        instrument_code
                    ],
                ),
            )
            for instrument_code in instrument_list
        ]
    )

    return buffered_position_dict

def apply_buffering_to_positions(
    position_contracts: pd.Series,
    average_position_contracts: pd.Series,
    buffer_size: float = 0.10,
) -> pd.Series:

    buffer = average_position_contracts.abs() * buffer_size
    upper_buffer = position_contracts + buffer
    lower_buffer = position_contracts - buffer

    buffered_position = apply_buffer(
        optimal_position=position_contracts,
        upper_buffer=upper_buffer,
        lower_buffer=lower_buffer,
    )

    return buffered_position


def apply_buffer(
    optimal_position: pd.Series, upper_buffer: pd.Series, lower_buffer: pd.Series
) -> pd.Series:

    upper_buffer = upper_buffer.ffill().round()
    lower_buffer = lower_buffer.ffill().round()
    use_optimal_position = optimal_position.ffill()

    current_position = use_optimal_position.iloc[0]
    if np.isnan(current_position):
        current_position = 0.0

    buffered_position_list = [current_position]

    for idx in range(len(optimal_position.index))[1:]:
        current_position = apply_buffer_single_period(
            last_position=current_position,
            top_pos=upper_buffer.iloc[idx],
            bot_pos=lower_buffer.iloc[idx],
        )

        buffered_position_list.append(current_position)

    buffered_position = pd.Series(buffered_position_list, index=optimal_position.index)

    return buffered_position


def apply_buffer_single_period(last_position: int, top_pos: float, bot_pos: float):

    if last_position > top_pos:
        return top_pos
    elif last_position < bot_pos:
        return bot_pos
    else:
        return last_position




INSTRUMENT_LIST = ["sp500", "gas"]

# Get the carry data for the SP500 and Gas
def get_data_dict_with_carry(instrument_list: list = None):
    if instrument_list is None:
        instrument_list = INSTRUMENT_LIST

    all_data = dict(
        [
            (instrument_code, pd_readcsv("%s.csv" % instrument_code))
            for instrument_code in instrument_list
        ]
    )

    adjusted_prices = dict(
        [
            (instrument_code, data_for_instrument.adjusted)
            for instrument_code, data_for_instrument in all_data.items()
        ]
    )

    current_prices = dict(
        [
            (instrument_code, data_for_instrument.underlying)
            for instrument_code, data_for_instrument in all_data.items()
        ]
    )

    carry_data = dict(
        [
            (instrument_code, pd_readcsv("%s_carry.csv" % instrument_code))
            for instrument_code in instrument_list
        ]
    )

    return adjusted_prices, current_prices, carry_data


def calculate_position_dict_with_multiple_carry_forecast_applied(
    adjusted_prices_dict: dict,
    std_dev_dict: dict,
    average_position_contracts_dict: dict,
    carry_prices_dict: dict,
    carry_spans: list,
) -> dict:

    list_of_instruments = list(adjusted_prices_dict.keys())
    position_dict_with_carry = dict(
        [
            (
                instrument_code,
                calculate_position_with_multiple_carry_forecast_applied(
                    average_position=average_position_contracts_dict[instrument_code],
                    stdev_ann_perc=std_dev_dict[instrument_code],
                    carry_price=carry_prices_dict[instrument_code],
                    carry_spans=carry_spans,
                ),
            )
            for instrument_code in list_of_instruments
        ]
    )

    return position_dict_with_carry


def calculate_position_with_multiple_carry_forecast_applied(
    average_position: pd.Series,
    stdev_ann_perc: standardDeviation,
    carry_price: pd.DataFrame,
    carry_spans: list,
) -> pd.Series:

    forecast = calculate_combined_carry_forecast(
        stdev_ann_perc=stdev_ann_perc,
        carry_price=carry_price,
        carry_spans=carry_spans,
    )

    return forecast * average_position / 10


def calculate_combined_carry_forecast(
    stdev_ann_perc: standardDeviation,
    carry_price: pd.DataFrame,
    carry_spans: list,
) -> pd.Series:

    all_forecasts_as_list = [
        calculate_forecast_for_carry(
            stdev_ann_perc=stdev_ann_perc,
            carry_price=carry_price,
            span=span,
        )
        for span in carry_spans
    ]

    ### NOTE: This assumes we are equally weighted across spans
    ### eg all forecast weights the same, equally weighted
    all_forecasts_as_df = pd.concat(all_forecasts_as_list, axis=1)
    average_forecast = all_forecasts_as_df.mean(axis=1)

    ## apply an FDM
    rule_count = len(carry_spans)
    FDM_DICT = {1: 1.0, 2: 1.02, 3: 1.03, 4: 1.04}
    fdm = FDM_DICT[rule_count]

    scaled_forecast = average_forecast * fdm
    capped_forecast = scaled_forecast.clip(-20, 20)

    return capped_forecast


def calculate_forecast_for_carry(
    stdev_ann_perc: standardDeviation, carry_price: pd.DataFrame, span: int
):

    smooth_carry = calculate_smoothed_carry(
        stdev_ann_perc=stdev_ann_perc, carry_price=carry_price, span=span
    )
    scaled_carry = smooth_carry * 30
    capped_carry = scaled_carry.clip(-20, 20)

    return capped_carry


def calculate_smoothed_carry(
    stdev_ann_perc: standardDeviation, carry_price: pd.DataFrame, span: int
):

    risk_adj_carry = calculate_vol_adjusted_carry(
        stdev_ann_perc=stdev_ann_perc, carry_price=carry_price
    )

    smooth_carry = risk_adj_carry.ewm(span).mean()

    return smooth_carry


def calculate_vol_adjusted_carry(
    stdev_ann_perc: standardDeviation, carry_price: pd.DataFrame
) -> pd.Series:

    ann_carry = calculate_annualised_carry(carry_price)
    ann_price_vol = stdev_ann_perc.annual_risk_price_terms()

    risk_adj_carry = ann_carry.ffill() / ann_price_vol.ffill()

    return risk_adj_carry


def calculate_annualised_carry(
    carry_price: pd.DataFrame,
):

    ## will be reversed if price_contract > carry_contract
    raw_carry = carry_price.PRICE - carry_price.CARRY
    contract_diff = _total_year_frac_from_contract_series(
        carry_price.CARRY_CONTRACT
    ) - _total_year_frac_from_contract_series(carry_price.PRICE_CONTRACT)

    ann_carry = raw_carry / contract_diff

    return ann_carry


def _total_year_frac_from_contract_series(x):
    years = _year_from_contract_series(x)
    month_frac = _month_as_year_frac_from_contract_series(x)

    return years + month_frac


def _year_from_contract_series(x):
    return x.floordiv(10000)


def _month_as_year_frac_from_contract_series(x):
    return _month_from_contract_series(x) / 12.0


def _month_from_contract_series(x):
    return x.mod(10000) / 100.0


if __name__ == "__main__":
    ## Get the files from:
    # https://gitfront.io/r/user-4000052/iTvUZwEUN2Ta/AFTS-CODE/blob/sp500.csv
    # https://gitfront.io/r/user-4000052/iTvUZwEUN2Ta/AFTS-CODE/blob/sp500_carry.csv
    # https://gitfront.io/r/user-4000052/iTvUZwEUN2Ta/AFTS-CODE/blob/gas_carry.csv
    # https://gitfront.io/r/user-4000052/iTvUZwEUN2Ta/AFTS-CODE/blob/gas.csv
    (
        adjusted_prices_dict,
        current_prices_dict,
        carry_prices_dict,
    ) = get_data_dict_with_carry()

    multipliers = dict(sp500=5, gas=10000)
    risk_target_tau = 0.2
    fx_series_dict = create_fx_series_given_adjusted_prices_dict(adjusted_prices_dict)

    capital = 2000000

    idm = 1.5
    instrument_weights = dict(sp500=0.5, gas=0.5)
    cost_per_contract_dict = dict(sp500=0.875, gas=15.3)

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

    carry_spans = [5, 20, 60, 120]
    position_contracts_dict = (
        calculate_position_dict_with_multiple_carry_forecast_applied(
            adjusted_prices_dict=adjusted_prices_dict,
            carry_prices_dict=carry_prices_dict,
            std_dev_dict=std_dev_dict,
            average_position_contracts_dict=average_position_contracts_dict,
            carry_spans=carry_spans,
        )
    )

    buffered_position_dict = apply_buffering_to_position_dict(
        position_contracts_dict=position_contracts_dict,
        average_position_contracts_dict=average_position_contracts_dict,
    )

    perc_return_dict = calculate_perc_returns_for_dict_with_costs(
        position_contracts_dict=buffered_position_dict,
        fx_series=fx_series_dict,
        multipliers=multipliers,
        capital=capital,
        adjusted_prices=adjusted_prices_dict,
        cost_per_contract_dict=cost_per_contract_dict,
        std_dev_dict=std_dev_dict,
    )