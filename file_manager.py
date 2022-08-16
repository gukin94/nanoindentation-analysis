import pandas as pd
import matplotlib.pyplot as plt


def txt_to_df(file_path):
    return pd.read_csv(file_path, sep='\t')


def return_curves_name_array(dataframe):
    columns = dataframe.columns
    curves_name_array = []
    for i in range(0, len(columns)-1, 2):
        curves_name_array.append(columns[i][2:][:-8])
    return curves_name_array




