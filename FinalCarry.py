import pandas as pd
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
from chapter10 import calculate_position_dict_with_multiple_carry_forecast_applied
from GetMultpliers import getMultiplierDict
from forecaster import calculate_capped_forecast
from getSQLdataV2 import get_data_dict_with_carry
from Carry import calc_idm
from sqlalchemy import create_engine
import urllib




def carry_forecast(capital: int, risk_target_tau: float, weights: dict, multipliers: dict, instr_list: list, carry_spans: list) -> tuple[dict, dict]:
   
    adjusted_prices_dict, current_prices_dict, carry_prices_dict = get_data_dict_with_carry(instr_list)

    fx_series_dict = create_fx_series_given_adjusted_prices_dict(adjusted_prices_dict)

    idm = calc_idm(instr_list)
    
    instrument_weights = weights
    
    cost_per_contract_dict = {instrument: 1 for instrument in INSTRUMENT_LIST}

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


# Server and database information - *update driver as needed*
driver = 'ODBC Driver 18 for SQL Server'
server = 'algo.database.windows.net'
username = 'dbmaster'
password = 'Password1'
database1 = 'NG_Carver_Data'
database2 = 'NG_Carver_Data_Carry'

# Connection string for SQL Server Authentication - do not change
params = urllib.parse.quote_plus(fr'DRIVER={driver};SERVER={server};DATABASE={database1};UID={username};PWD={password}')
engine1 = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
table_names_query = "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_catalog='" + database1 + "'"
table_names = pd.read_sql(table_names_query, engine1)['table_name'].tolist()

# Connection string for SQL Server Authentication - do not change
params2 = urllib.parse.quote_plus(fr'DRIVER={driver};SERVER={server};DATABASE={database2};UID={username};PWD={password}')
engine2 = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params2)
table_names_query2 = "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_catalog='" + database2 + "'"
table_names2 = pd.read_sql(table_names_query, engine2)['table_name'].tolist()

# Inputs
INSTRUMENT_LIST = pd.read_sql(table_names_query, engine1)['table_name'].tolist()
INSTRUMENT_LIST = pd.read_sql(table_names_query, engine1)['table_name'].str.rstrip('_Data').tolist()


capital = 500000

risk_target_tau = 0.2

even_weights = 1 / len(INSTRUMENT_LIST)
weights = {instrument: even_weights for instrument in INSTRUMENT_LIST}

multipliers = getMultiplierDict()

carry_spans = [5,20,60,120]




#print(carry_forecast(capital, risk_target_tau, weights, multipliers, INSTRUMENT_LIST, carry_spans))
perc, buff_pos, capped_forecast = carry_forecast(capital, risk_target_tau, weights, multipliers, INSTRUMENT_LIST, carry_spans)

#positions = pd.DataFrame.from_dict(buff_pos)
#positions.to_csv("FinalcarryPositions.csv")

#returns = pd.DataFrame.from_dict(perc)
#returns.to_csv("carryReturns.csv")

#capped_fc = pd.DataFrame.from_dict(capped_forecast)
#capped_fc.to_csv("carryCappedForecasts.csv")