import pandas as pd
from sqlalchemy import create_engine
import urllib

from chapter1 import calculate_stats
from chapter1 import BUSINESS_DAYS_IN_YEAR
from chapter3 import standardDeviation
from chapter4 import (
    create_fx_series_given_adjusted_prices_dict,
    calculate_variable_standard_deviation_for_risk_targeting_from_dict,
    calculate_position_series_given_variable_risk_for_dict,
)

from chapter5 import calculate_perc_returns_for_dict_with_costs
from chapter10 import calculate_position_dict_with_multiple_carry_forecast_applied
from GetMultpliers import getMultiplierDict
from forecaster import calculate_capped_forecast
from Carry import calc_idm
import get_SQL_functions as sql




def carry_forecast(capital: int, risk_target_tau: float, weights: dict, multipliers: dict, instr_list: list, carry_spans: list) -> tuple[dict, dict]:
   
    adjusted_prices_dict, current_prices_dict = sql.get_data(instr_list)

    carry_prices_dict = sql.get_carry_data(instr_list)

    fx_series_dict = create_fx_series_given_adjusted_prices_dict(adjusted_prices_dict)

    idm = calc_idm(instr_list)

    instrument_weights = weights

    for instrument in instr_list:
        cost_per_contract_dict = dict(instrument=0.875)

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
        calculate_position_dict_with_multiple_carry_forecast_applied(
            adjusted_prices_dict=adjusted_prices_dict,
            carry_prices_dict=carry_prices_dict,
            std_dev_dict=std_dev_dict,
            average_position_contracts_dict=average_position_contracts_dict,
            carry_spans=carry_spans,
        )
    )


    perc_return_dict = calculate_perc_returns_for_dict_with_costs(
        position_contracts_dict=position_contracts_dict,
        fx_series=fx_series_dict,
        multipliers=multipliers,
        capital=capital,
        adjusted_prices=adjusted_prices_dict,
        cost_per_contract_dict=cost_per_contract_dict,
        std_dev_dict=std_dev_dict,
    )

    capped_forecast_dict = calculate_capped_forecast(
        adjusted_prices_dict, 
        std_dev_dict, 
        carry_prices_dict, 
        carry_spans,
        )
    
    return perc_return_dict, position_contracts_dict, capped_forecast_dict


# List of all instruments in the portfolio
def main():

    INSTRUMENT_LIST = ['CL', 'ES', 'GC', 'NG']

    even_weights = 1 / len(INSTRUMENT_LIST)

    carry_spans = [5,20,60,120]
    
    # dict of equal weight for each instrument in the list
    weights = {}
    for instrument in INSTRUMENT_LIST:
        weights[instrument] = even_weights

    multipliers = getMultiplierDict()
    risk_target_tau = 0.2

    capital = 100000
    
    perc_return, positions, capped_forecast = carry_forecast(capital, risk_target_tau, weights, multipliers, INSTRUMENT_LIST, carry_spans)

    print(positions['ES'].tail())

if __name__ == '__main__':
    main()