import pandas as pd

def getMultiplierDict():
    # Read in the multiplier data
    df = pd.read_csv("Symbols.csv")
    df.set_index('Code',inplace=True)
    # Convert the dataframe to a dictionary
    m_series = df["Point Value"].astype(float)

    multiplierDict = m_series.to_dict()
    # Return the dictionary
    return multiplierDict