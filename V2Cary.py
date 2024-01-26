import pandas as pd
from enum import Enum
from sqlalchemy import create_engine
import urllib

try:
    from .chapter4 import (
        create_fx_series_given_adjusted_prices_dict,
        calculate_variable_standard_deviation_for_risk_targeting_from_dict,
        calculate_position_series_given_variable_risk_for_dict,
    )

    from .chapter5 import calculate_perc_returns_for_dict_with_costs
    from .chapter10 import calculate_position_dict_with_multiple_carry_forecast_applied
    from .getMultplierDict import getMultiplierDict
    from .forecaster import calculate_capped_forecast
    from .V1Carry import calc_idm
    from . import get_carry_SQL_functions as sql
except ImportError:
    from chapter4 import (
        create_fx_series_given_adjusted_prices_dict,
        calculate_variable_standard_deviation_for_risk_targeting_from_dict,
        calculate_position_series_given_variable_risk_for_dict,
    )

    from chapter5 import calculate_perc_returns_for_dict_with_costs
    from chapter10 import calculate_position_dict_with_multiple_carry_forecast_applied
    from forecaster import calculate_capped_forecast
    from V1Carry import calc_idm
    import get_carry_SQL_functions as sql




def carry_forecast(capital: int, risk_target_tau: float, weights: dict, multipliers: dict, instr_list: list, carry_spans: list) -> tuple[dict, dict]:
   
    adjusted_prices_dict, current_prices_dict = sql.get_data(instr_list)

    carry_prices_dict = sql.get_carry_data(instr_list)

    fx_series_dict = create_fx_series_given_adjusted_prices_dict(adjusted_prices_dict)

    idm = calc_idm(instr_list)

    instrument_weights = weights

    # Initialize cost_per_contract_dict with the value 0.875 for all instruments
    cost_per_contract_dict = {instrument: 0.875 for instrument in instr_list}

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

    # ZS doesn't work
    INSTRUMENT_LIST = ['FCE', '6C', '6S', 'CT', 'LRC', 'FDAX', '6E', '6B', 'GF', 'HE', '6J', 'KC', 'KE', 'LE', 'RTY', '6A', 'WBS','ES', 'GC', 'HG', 'NQ', 'RB', '6M', 'YM', '6N', 'PL', 'SB', 'SI', 'FSMI', 'UB', 'VX', 'LSU', 'SCN', 'ZW', 'ZC', 'ZL', 'ZM', 'ZN', 'ZR']

    even_weights = 1 / len(INSTRUMENT_LIST)

    carry_spans = [5,20,60,120]
    
    # dict of equal weight for each instrument in the list
    weights = {}
    for instrument in INSTRUMENT_LIST:
        weights[instrument] = even_weights

    multipliers = getMultiplierDict()
    risk_target_tau = 0.2

    capital = 50000000
    
    perc_return_dict, positions, capped_forecast = carry_forecast(capital, risk_target_tau, weights, multipliers, INSTRUMENT_LIST, carry_spans)
    

    print(positions['GC'].tail())

if __name__ == '__main__':
    main()