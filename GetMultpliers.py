import pandas as pd

def getMultiplierDict(multipliers_file : str= "multipliers.csv", multiplier_column : str = "multiplier"):
    # Read in the multiplier data
    df = pd.read_csv(multipliers_file, index_col=0)
    # Convert the dataframe to a dictionary
    m_series = df[multiplier_column].astype(int)

    multiplierDict = m_series.to_dict()
    # Return the dictionary
    return multiplierDict

if __name__ == "__main__":
    print(getMultiplierDict())
