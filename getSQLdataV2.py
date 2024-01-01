import pandas as pd
from sqlalchemy import create_engine
import urllib

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



def get_data_dict_with_carry(instrument_list: list = None):
    if instrument_list is None:
        instrument_list = INSTRUMENT_LIST

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

    # Connection string for SQL Server Authentication - do not change
    params2 = urllib.parse.quote_plus(fr'DRIVER={driver};SERVER={server};DATABASE={database2};UID={username};PWD={password}')
    engine2 = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params2)


    # Initialize dictionaries to store data
    adjusted_prices = {}
    current_prices = {}
    carry_data = {}

    for instrument_code in instrument_list:
        # Fetch adjusted prices
        adjusted_query = f"SELECT Date, [Close] FROM [{instrument_code}]"
        adjusted_prices[instrument_code] = pd.read_sql(adjusted_query, engine1)

        # Fetch current prices (unadjusted)
        current_query = f"SELECT Date, [Unadj_Close] FROM [{instrument_code}]"
        current_prices[instrument_code] = pd.read_sql(current_query, engine1)

    for instrument_code in instrument_list:
        # Fetch carry data
        carry_query = f"SELECT * FROM [{instrument_code}_Carry]"
        carry_data[instrument_code] = pd.read_sql(carry_query, engine2)

    return adjusted_prices, current_prices, carry_data

    # Retrieve a list of all table names in the database - do not change




INSTRUMENT_LIST = pd.read_sql(table_names_query, engine1)['table_name'].tolist()
print(INSTRUMENT_LIST)


# Example usage
adjusted_prices_dict, current_prices_dict, carry_data_dict = get_data_dict_with_carry(INSTRUMENT_LIST)
print(carry_data_dict)