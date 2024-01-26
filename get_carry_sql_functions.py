import pandas as pd 
from sqlalchemy import create_engine
import urllib

DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DUSTIN_DATE_FORMAT = "%m/%d/%Y"

def get_data(instrument_list: list):
    # get all tables from database
    driver = "ODBC Driver 18 for SQL Server"
    server = "algo.database.windows.net"
    username = "dbmaster"
    password = "Password1"

    database = "NG_Carver_Data"

    # Connection string for SQL Server Authentication - do not change
    params = urllib.parse.quote_plus(fr'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

    # Retrieve a list of all table names in the database - do not change
    try:
        table_names_query = "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_catalog='" + database + "'"
        table_names = pd.read_sql(table_names_query, engine)['table_name'].tolist()
    except:
        print("Error: Unable to retrieve table names from database.")
        return

    # Dictionary to store each table's DataFrame
    dataframes = {}

    usable_list = []
    # Remove instrument from list table_names if it is not in instrument_list
    for table_name in table_names:
        # remove _Data from table name temporarily
        name = table_name[:-5]
        if name in instrument_list:
            usable_list.append(name)
            

    # Remove sysdiagrams from table_names
    table_names.remove('sysdiagrams')

    # Remove _Data from table names
    for i in range(len(table_names)):
        table_names[i] = table_names[i][:-5]

    # Print the tables that will be pulled
    print(sorted(usable_list))

    # Loop through all table names, pulling data from each one
    for name in usable_list:
        table_query = f"SELECT * FROM [{name}_Data]"
        dataframes[name] = pd.read_sql(table_query, engine)

    # Convert date column to datetime
    for name in usable_list:
        dataframes[name]['Date'] = pd.to_datetime(dataframes[name]['Date'])

    # Set index to date column
    for name in usable_list:
        dataframes[name].set_index('Date', inplace=True)
        assert dataframes[name].index.name == 'Date'

    # Get all adjusted close prices in each dataframe
    adjusted_prices = {}
    for name in usable_list:
        adjusted_prices[name] = dataframes[name]['Close']

    # Get all unadjusted close prices in each dataframe
    current_prices = {}
    for table_name in usable_list:
        current_prices[table_name] = dataframes[table_name]['Unadj_Close']
    
    return adjusted_prices, current_prices

def get_carry_data(instrument_list: list):
    # get all tables from database
    driver = "ODBC Driver 18 for SQL Server"
    server = "algo.database.windows.net"
    username = "dbmaster"
    password = "Password1"

    database = "NG_Carver_Data_Carry"

    # Connection string for SQL Server Authentication - do not change
    params = urllib.parse.quote_plus(fr'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

    # Retrieve a list of all table names in the database - do not change
    try:
        table_names_query = "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_catalog='" + database + "'"
        table_names = pd.read_sql(table_names_query, engine)['table_name'].tolist()
    except:
        print("Error: Unable to retrieve table names from database.")
        return

    # Dictionary to store each table's DataFrame
    carry_data = {}

    usable_list = []
    # Remove instrument from list table_names if it is not in instrument_list
    for table_name in table_names:
        # remove _Data from table name temporarily
        name = table_name[:-11]
        if name in instrument_list:
            usable_list.append(name)
            

    # Remove _Data from table names
    for i in range(len(table_names)):
        table_names[i] = table_names[i][:-11]

    # Print the tables that will be pulled
    print(sorted(usable_list))

    # Loop through all table names, pulling data from each one
    for name in usable_list:
        table_query = f"SELECT * FROM [{name}_Data_Carry]"
        carry_data[name] = pd.read_sql(table_query, engine)

    # Convert date column to datetime
    for name in usable_list:
        carry_data[name]['Date'] = pd.to_datetime(carry_data[name]['Date'])

    # Set index to date column
    for name in usable_list:
        carry_data[name].set_index('Date', inplace=True)
        assert carry_data[name].index.name == 'Date'

    # SET ALL COL NAMES TO CAPS
    for name in usable_list:
        carry_data[name].columns = carry_data[name].columns.str.upper()
    return carry_data

def main():
    instrument_list = ['CL', 'ES', 'GC', 'HG', 'HO', 'NG', 'RB', 'SI']
    adjusted_prices, current_prices = get_data(instrument_list)
    carry_prices = get_carry_data(instrument_list)
    for instrument in instrument_list:
        print(adjusted_prices[instrument].tail())
        print(carry_prices[instrument].tail())

if __name__ == '__main__':
    main()