import pandas as pd
from sqlalchemy import create_engine
import urllib

DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DUSTIN_DATE_FORMAT = "%m/%d/%Y"

def pd_read_sql(
    ins_code: str,
    engine,
        date_format=DEFAULT_DATE_FORMAT,
        date_index_name: str="index",
) -> pd.DataFrame:

    ans = pd.read_sql(f"select * from {ins_code}", engine)
    ans.index = pd.to_datetime(ans[date_index_name], format=date_format).values

    del ans[date_index_name]

    ans.index.name = None

    return ans

def get_data_dict_sql_no_carry(instr_list: list):
    driver = "ODBC Driver 18 for SQL Server"
    server = "algo.database.windows.net"
    username = "dbmaster"
    password = "Password1"
    database1 = "NG_Carver_Data"
    database2 = "NG_Carver_Data_Carry"

    params = urllib.parse.quote_plus(
        fr"DRIVER={driver};SERVER={server};DATABASE={database1};UID={username};PWD={password}"
    )
    engine1 = create_engine(
        "mssql+pyodbc:///?odbc_connect=%s" % params, pool_size=10, max_overflow=-1
    )

    # Connection to carry database
    params2 = urllib.parse.quote_plus(
        fr"DRIVER={driver};SERVER={server};DATABASE={database2};UID={username};PWD={password}"
    )
    engine2 = create_engine(
        "mssql+pyodbc:///?odbc_connect=%s" % params2, pool_size=10, max_overflow=-1
    )

    all_data = dict(
        [
            (instrument_code, pd_read_sql(f"SELECT * FROM [{instrument_code}]", engine1))
            for instrument_code in instr_list
        ]
    )

    all_data_carry = dict(
        [
            (instrument_code, pd_read_sql(f"SELECT * FROM [{instrument_code}]", engine2))
            for instrument_code in instr_list
        ]
    )

    adjusted_prices = dict(
        [
            (instrument_code, data_for_instrument.Close)
            for instrument_code, data_for_instrument in all_data.items()
        ]
    )

    current_prices = dict(
        [
            (instrument_code, data_for_instrument.Unadj_Close)
            for instrument_code, data_for_instrument in all_data.items()
        ]
    )
    return adjusted_prices, current_prices, 

def get_data_dict_sql_carry(instr_list: list):
    driver = "ODBC Driver 18 for SQL Server"
    server = "algo.database.windows.net"
    username = "dbmaster"
    password = "Password1"
    database1 = "NG_Carver_Data"
    database2 = "NG_Carver_Data_Carry"

    params = urllib.parse.quote_plus(
        fr"DRIVER={driver};SERVER={server};DATABASE={database1};UID={username};PWD={password}"
    )
    engine1 = create_engine(
        "mssql+pyodbc:///?odbc_connect=%s" % params, pool_size=10, max_overflow=-1
    )

    # Connection to carry database
    params2 = urllib.parse.quote_plus(
        fr"DRIVER={driver};SERVER={server};DATABASE={database2};UID={username};PWD={password}"
    )
    engine2 = create_engine(
        "mssql+pyodbc:///?odbc_connect=%s" % params2, pool_size=10, max_overflow=-1
    )

    all_data = dict(
        [
            (instrument_code, pd_read_sql(f"SELECT * FROM [{instrument_code}]", engine1))
            for instrument_code in instr_list
        ]
    )

    carry_data = dict(
        [
            (instrument_code, pd_read_sql(f"SELECT * FROM [{instrument_code}]", engine2))
            for instrument_code in instr_list
        ]
    )

    adjusted_prices = dict(
        [
            (instrument_code, data_for_instrument.Close)
            for instrument_code, data_for_instrument in all_data.items()
        ]
    )

    current_prices = dict(
        [
            (instrument_code, data_for_instrument.Unadj_Close)
            for instrument_code, data_for_instrument in all_data.items()
        ]
    )

    return adjusted_prices, current_prices, carry_data