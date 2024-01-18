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
    for table_name in table_names:
        table_query = f"SELECT * FROM [{table_name}_Data]"
        dataframes[table_name] = pd.read_sql(table_query, engine)

    # Convert date column to datetime
    for table_name in table_names:
        dataframes[table_name]['Date'] = pd.to_datetime(dataframes[table_name]['Date'])

    # Set index to date column
    for table_name in table_names:
        dataframes[table_name].set_index('Date', inplace=True)
        assert dataframes[table_name].index.name == 'Date'

    # Get all adjusted close prices in each dataframe
    adjusted_prices = {}
    for table_name in table_names:
        adjusted_prices[table_name] = dataframes[table_name]['Close']

    # Get all unadjusted close prices in each dataframe
    current_prices = {}
    for table_name in table_names:
        current_prices[table_name] = dataframes[table_name]['Unadj_Close']
    
    return adjusted_prices, current_prices

def get_carry_data():
    # Server and database information - *update driver as needed*
    driver = 'ODBC Driver 18 for SQL Server'
    server = 'algo.database.windows.net'
    username = 'dbmaster'
    password = 'Password1'

    # *Change database to NG_Carver_Data_Carry as needed*
    database = 'NG_Carver_Data_Carry'

    # Connection string for SQL Server Authentication - do not change
    params = urllib.parse.quote_plus(fr'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

    # Retrieve a list of all table names in the database - do not change
    table_names_query = "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_catalog='" + database + "'"
    table_names = pd.read_sql(table_names_query, engine)['table_name'].tolist()

    # Dictionary to store each table's DataFrame
    carry_data = {}

    # Loop through all table names, pulling data from each one
    for table_name in table_names:
        table_query = f"SELECT * FROM [{table_name}]"
        carry_data[table_name] = pd.read_sql(table_query, engine)

    # Convert date column to datetime
    for table_name in table_names:
        carry_data[table_name]['Date'] = pd.to_datetime(carry_data[table_name]['Date'])

    # Set index to date column
    for table_name in table_names:
        carry_data[table_name].set_index('Date', inplace=True)
        assert carry_data[table_name].index.name == 'Date'

    return carry_data


def main():
    instrument_list = ['CL', 'ES', 'GC', 'HG', 'HO', 'NG', 'RB', 'SI']
    adjusted_prices, current_prices = get_data(instrument_list)
    carry_prices = get_carry_data(instrument_list)
    print(adjusted_prices['CL'].tail())


if __name__ == '__main__':
    main()