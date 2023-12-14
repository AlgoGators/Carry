# Carry

The purpose of this repository is to:

1. Provide a visual representation of Carver's Carry Strategy.
2. Redefine Carver's existing Carry python code.


The CarryUpdated.py file consists of the Carry strategy and its functions. This file brings in functions from chapters 1 - 10. It creates a csv file ('out.csv') that contains the average position size we should hold in each asset.

The forecaster.py file creates a dataframe of capped forecasts and prints them out to 'forecasts.csv.' Printing these capped forecasts are important because it gives us reasoning for our position sizing in 'out.csv.'
