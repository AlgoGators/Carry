import pandas as pd
from sqlalchemy import create_engine
import urllib


def main():
    # Server and database information - *update driver as needed*
    driver = 'ODBC Driver 18 for SQL Server'
    server = 'algo.database.windows.net'
    username = 'dbmaster'
    password = 'Password1'

    # *Change database to NG_Carver_Data_Carry as needed*
    database = 'NG_Carver_Data'

    # Connection string for SQL Server Authentication - do not change
    params = urllib.parse.quote_plus(fr'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

    # Retrieve a list of all table names in the database - do not change
    table_names_query = "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_catalog='" + database + "'"
    table_names = pd.read_sql(table_names_query, engine)['table_name'].tolist()

    # Dictionary to store each table's DataFrame
    dataframes = {}

    # Loop through all table names, pulling data from each one
    for table_name in table_names:
        table_query = f"SELECT * FROM [{table_name}]"
        dataframes[table_name] = pd.read_sql(table_query, engine)

    # Set print options to display all columns
    pd.set_option('display.max_columns', None)

    # Prints all table names in chosen database
    print(sorted(table_names))

    # Print the first 5 rows of ES Contract
    print(dataframes['ES_Data'].head())


if __name__ == '__main__':
    main()
