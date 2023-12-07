import pandas as pd

def getMultiplierDict():
    # Read in the multiplier data
    df = pd.read_csv("multipliers.csv", index_col=0)
    # Convert the dataframe to a dictionary
    m_series = df["multiplier"].astype(int)

    multiplierDict = m_series.to_dict()
    # Return the dictionary
    return multiplierDict

print(getMultiplierDict())
