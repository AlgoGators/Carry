import pandas as pd

def getTradeableSQLDict(tradeableinstr_file : str= "instruments.csv", multiplier_column : str = "Data S"):
    # Read in the multiplier data
    df = pd.read_csv(tradeableinstr_file, index_col=0)
    # Convert the dataframe to a dictionary
    m_series = df[multiplier_column].astype(int)

    InstrDict = m_series.to_dict()
    # Return the dictionary
    return InstrDict

if __name__ == "__main__":
    print(getTradeableSQLDict())
