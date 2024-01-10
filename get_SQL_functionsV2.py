import pandas as pd
from sqlalchemy import create_engine
import urllib

DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DUSTIN_DATE_FORMAT = "%m/%d/%Y"

def create_database_engine(server, database, username, password, driver="ODBC Driver 18 for SQL Server"):
    params = urllib.parse.quote_plus(
        f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )
    return create_engine("mssql+pyodbc:///?odbc_connect=%s" % params, pool_size=10, max_overflow=-1)

def pd_read_sql_wrapper(ins_code, engine, date_format, date_index_name):
    ans = pd.read_sql(ins_code, engine)
    ans.index = pd.to_datetime(ans[date_index_name], format=date_format).values
    del ans[date_index_name]
    ans.index.name = None
    return ans

def get_data_dict_sql(instr_list, engine1, engine2, date_format1, date_format2):
    all_data = {
        instrument_code: pd_read_sql_wrapper(f"SELECT * FROM [{instrument_code}]", engine1, date_format1, "Date")
        for instrument_code in instr_list
    }

    carry_data = {
        instrument_code: pd_read_sql_wrapper(f"SELECT * FROM [{instrument_code}_Carry]", engine2, date_format2, "index")
        for instrument_code in instr_list
    }

    adjusted_prices = {instrument_code: data_for_instrument.Close for instrument_code, data_for_instrument in all_data.items()}
    current_prices = {instrument_code: data_for_instrument.Unadj_Close for instrument_code, data_for_instrument in all_data.items()}

    return adjusted_prices, current_prices, carry_data

# Example usage:
server = "algo.database.windows.net"
username = "dbmaster"
password = "Password1"
database1 = "NG_Carver_Data"
database2 = "NG_Carver_Data_Carry"

engine1 = create_database_engine(server, database1, username, password)
engine2 = create_database_engine(server, database2, username, password)

instrument_list = []
adjusted_prices, current_prices, carry_data = get_data_dict_sql(instrument_list, engine1, engine2, DUSTIN_DATE_FORMAT, DEFAULT_DATE_FORMAT)