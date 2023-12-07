from chapter1 import pd_readcsv
from chapter1 import calculate_stats
from chapter1 import pd_readcsv, BUSINESS_DAYS_IN_YEAR
from chapter3 import standardDeviation
from chapter4 import (
    create_fx_series_given_adjusted_prices_dict,
    calculate_variable_standard_deviation_for_risk_targeting_from_dict,
    calculate_position_series_given_variable_risk_for_dict,
)

from chapter5 import calculate_perc_returns_for_dict_with_costs
from chapter8 import apply_buffering_to_position_dict
from chapter10 import calculate_position_dict_with_multiple_carry_forecast_applied
#from GetMultipliers import getMultiplierDict
print("Hello world")


INSTRUMENT_LIST = ['sp500', 'gas']

## Get underlying price, adjusted price, and carry price
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

##print(get_data_dict_with_carry(['sp500']))
##print(get_data_dict_with_carry(['gas']))

def calc_idm(instrument_list: list) -> float:

    # if the lenght of the instrument list lands in a certain bracket, return a certain value
    # this is not a true idm, but a rough approx.
    # TRUE IDM = 1 / sqrt(w.rho.wT)
    n = len(instrument_list)

    if n == 1:
        return 1.0
    elif n == 2:
        return 1.20
    elif n == 3:
        return 1.48
    elif n == 4:
        return 1.56
    elif n == 5:
        return 1.70
    elif n == 6:
        return 1.90
    elif n == 7:
        return 2.10
    elif n >= 8 and n <= 14:
        return 2.20
    elif n >= 15 and n <= 24:
        return 2.30
    elif n >= 25 and n <= 30:
        return 2.40
    elif n > 30:
        return 2.50

    # if we reached here, something went wrong
    raise ValueError("Instrument Diversity Multiplier not found")   

##print(calc_idm(['sp500', 'gas']))



def carry_forecast(capital: int, risk_target_tau: float, weights: dict, multipliers: dict, instr_list: list, carry_spans: list) -> tuple[dict, dict]:
   
    adjusted_prices_dict, current_prices_dict, carry_prices_dict = get_data_dict_with_carry(instr_list)

    fx_series_dict = create_fx_series_given_adjusted_prices_dict(adjusted_prices_dict)

    
    idm = calc_idm(instr_list)
    
    instrument_weights = weights
    
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
    
    return perc_return_dict, buffered_position_dict



capital = 500000

risk_target_tau = 0.2

even_weights = 1 / len(INSTRUMENT_LIST)
weights = dict(sp500=even_weights, gas=even_weights)

multipliers = dict(sp500=5, gas=10000)

carry_spans = [5,20,60,120]

##multipliers = getMultiplierDict()


print(carry_forecast(capital, risk_target_tau, weights, multipliers, INSTRUMENT_LIST, carry_spans))
##perc, fc = carry_forecast(capital, risk_target_tau, weights, multipliers, INSTRUMENT_LIST, carry_spans)
##print(calculate_stats(perc))
