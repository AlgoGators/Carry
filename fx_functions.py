import pandas as pd

def create_fx_series_given_adjusted_prices_dict(adjusted_prices_dict: dict) -> dict:
    fx_series_dict = dict(
        [
            (
                instrument_code,
                create_fx_series_given_adjusted_prices(
                    instrument_code, adjusted_prices
                ),
            )
            for instrument_code, adjusted_prices in adjusted_prices_dict.items()
        ]
    )
    return fx_series_dict

def create_fx_series_given_adjusted_prices(
    instrument_code: str, adjusted_prices: pd.Series
) -> pd.Series:

    currency_for_instrument = fx_dict.get(instrument_code, "usd")
    if currency_for_instrument == "usd":
        return pd.Series(1, index=adjusted_prices.index)  ## FX rate, 1 for USD / USD

    fx_prices = get_fx_prices(currency_for_instrument)
    fx_prices_aligned = fx_prices.reindex(adjusted_prices.index).ffill()

    return fx_prices_aligned

fx_dict = dict(eurostx="eur")

def get_fx_prices(currency: str) -> pd.Series:
    prices_as_df = pd_readcsv("%s_fx.csv" % currency)
    return prices_as_df.squeeze()

