import pandas as pd

try:
    from . import get_carry_sql_functions as sql
    from .fx_functions import create_fx_series_given_adjusted_prices_dict
    from .risk_functions import calculate_variable_standard_deviation_for_risk_targeting_from_dict
    from .risk_functions import calculate_position_series_given_variable_risk_for_dict
    from .carry_functions import calculate_position_dict_with_multiple_carry_forecast_applied, apply_buffering_to_position_dict, calculate_perc_returns_for_dict_with_costs
    from .getMultiplierDict import getMultiplierDict
except ImportError:
    import get_carry_sql_functions as sql
    from fx_functions import create_fx_series_given_adjusted_prices_dict
    from risk_functions import calculate_variable_standard_deviation_for_risk_targeting_from_dict
    from risk_functions import calculate_position_series_given_variable_risk_for_dict
    from carry_functions import calculate_position_dict_with_multiple_carry_forecast_applied, apply_buffering_to_position_dict, calculate_perc_returns_for_dict_with_costs, calculate_capped_forecast
    from getMultiplierDict import getMultiplierDict

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

def carry_forecast(instr_list: list, weights: dict, capital: int, risk_target_tau: float, multipliers: dict, carry_spans: list) :
   
    adjusted_prices_dict, current_prices_dict = sql.get_data(instr_list)

    carry_prices_dict = sql.get_carry_data(instr_list)

    fx_series_dict = create_fx_series_given_adjusted_prices_dict(adjusted_prices_dict)

    idm = calc_idm(instr_list)

    instrument_weights = weights

    # cost per contract is set to $3 both ways so $6 total
    # Initialize cost_per_contract_dict with the value 3 for all instruments
    cost_per_contract_dict = {instrument: 6 for instrument in instr_list}

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
    
    return [buffered_position_dict, position_contracts_dict]

# List of all instruments in the portfolio
def main():

    instruments = ['CL', 'ES', 'GC', 'HG', 'HO', 'NG', 'RB', 'SI']
    symbols = pd.read_csv('Symbols.csv')
    all_instruments = symbols['Code'].to_list()

    even_weights = 1 / len(all_instruments)

    
    # dict of equal weight for each instrument in the list
    weights = {}
    for code in all_instruments:
        weights[code] = even_weights

    multipliers = getMultiplierDict()
    risk_target_tau = 0.2

    carry_spans = [5,20,60,120]

    capital = 400000

    buffered_pos, pos = carry_forecast((all_instruments, weights, capital, risk_target_tau, multipliers, carry_spans)

    for code in sorted(pos.keys()):
        print(code)
        print(pos[code].tail())
    print(len(pos))

if __name__ == '__main__':
    main()

