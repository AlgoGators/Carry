import pandas as pd
from sqlalchemy import create_engine
import urllib


## Get underlying price, adjusted price, and carry price
def get_data_dict_with_carry():
    

        # Server and database information - *update driver as needed*
    driver = 'ODBC Driver 18 for SQL Server'
    server = 'algo.database.windows.net'
    username = 'dbmaster'
    password = 'Password1'

    # *Change database to NG_Carver_Data_Carry as needed*
    database = 'NG_Carver_Data'
    database2 = 'NG_Carver_Data_Carry'

    # Connection string for SQL Server Authentication - do not change
    params = urllib.parse.quote_plus(fr'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

    # Retrieve a list of all table names in the database - do not change
    table_names_query = "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_catalog='" + database + "'"
    table_names = pd.read_sql(table_names_query, engine)['table_name'].tolist()

    table_names_query2 =  "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_catalog='" + database + "'"
    table_names = pd.read_sql(table_names_query2, engine)['table_name'].tolist()



    
    all_data = {}

    
    for table_name in table_names:
        table_query = f"SELECT * FROM [{table_name}]"
        all_data[table_name] = pd.read_sql(table_query, engine)


    #adjusted_prices = dict(
       # [
            #(instrument_code, data_for_instrument.adjusted)
            #for instrument_code, data_for_instrument in all_data.items()
      #  ]
   # )

    adjusted_prices = {}

    
    for table_name in table_names:
        table_query = f"SELECT [Close] FROM [{table_name}]"
        adjusted_prices[table_name] = pd.read_sql(table_query, engine)



   # current_prices = dict(
       # [
          #  (instrument_code, data_for_instrument.underlying)
           # for instrument_code, data_for_instrument in all_data.items()
      #  ]
  #  )



    current_prices = {}

    
    for table_name in table_names:
        table_query = f"SELECT [Unadj_Close] FROM [{table_name}]"
        current_prices[table_name] = pd.read_sql(table_query, engine)



   # carry_data = dict(
      #  [
         #   (instrument_code, pd_readcsv("%s_carry.csv" % instrument_code))
          #  for instrument_code in instrument_list
      #  ]
 #   )


    return adjusted_prices, current_prices


adjusted_prices_dict, current_prices_dict = get_data_dict_with_carry()
print(adjusted_prices_dict)