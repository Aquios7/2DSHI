import numpy as np
import pandas as pd
import csv
import os
from tkinter.filedialog import askdirectory

def replace_nans_in_file(file, save_to, replace_value=float(0)):
    r_sample_csv_file = pd.read_csv(file, header=None)
    values_r_sample = r_sample_csv_file.values
    if not is_dtype_object(values_r_sample):
        where_are_NaNs = np.isnan(values_r_sample)
        values_r_sample[where_are_NaNs] = replace_value
    #adj_file = save_to[:-4] + "_noNANs" + save_to[-4:]
    with open(save_to, "w+", newline='') as my_csv:
        csvWriter = csv.writer(my_csv, delimiter=',')
        csvWriter.writerows(values_r_sample.tolist())

# checks for dtype
def is_dtype_object(lst):
    arr = np.array(lst)
    return arr.dtype == object
