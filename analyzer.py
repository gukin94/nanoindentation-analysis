import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def averaged_curve(data, selected_curves):
    df_merged = pd.DataFrame()  # Creating empty DataFrame to concat selected curves

    soon_merged_array_pd = []
    soon_merged_array_hardness = []

    for i in range(len(selected_curves)):
        x_name = f"X_{selected_curves[i]}_Pd_[nm]"
        y_name = f"Y_{selected_curves[i]}_Hardness (H)_[MPa]"
        soon_merged_array_pd.append(data[x_name])
        soon_merged_array_hardness.append(data[y_name])

    df_merged['Pd'] = pd.concat(soon_merged_array_pd)
    df_merged['Hardness'] = pd.concat(soon_merged_array_hardness)

    df_merged.sort_values(by=['Pd'], axis=0, inplace=True)
    df_merged.reset_index(level=None, drop=True, inplace=True, col_level=0, col_fill='')

    x = df_merged['Pd']
    y = df_merged['Hardness']

    i = 0
    lim = len(x)
    window_size = 20

    # Initialize an empty list to store moving averages
    moving_avgX = []
    moving_avgY = []
    moving_stdY = []

    # Loop through the array t o
    # consider every window of size 3
    while i < lim - window_size + 1:
        # Calculate the average of current window
        window_avg = round(np.sum(y[i:i + window_size]) / window_size, 2)  # i, i+1, ... i+window_size-1
        window_std = round(np.std(y[i:i + window_size]))

        # Store the average of current
        # window in moving average list
        moving_avgY.append(window_avg)
        moving_stdY.append(window_std)
        moving_avgX.append(x[i] + window_size / 2)

        # Shift window to right by one position
        i += 1

    return pd.DataFrame({'x': moving_avgX, 'mean': moving_avgY, 'std': moving_stdY})
