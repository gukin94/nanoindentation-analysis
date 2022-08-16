import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
from scipy.optimize import curve_fit


HARDNESS_TIME_FILE_PATH = "./example_file/HT_V_300mN.TXT"
STIFFNESS_FILE_PATH = './example_file/HT_V_300mN_data.TXT'

START_STEP_SIZE = 100
LIMIT_STEP_SIZE = 1000

hardness_time_data = pd.read_csv(HARDNESS_TIME_FILE_PATH, sep='\t')
stiffness_data = pd.read_csv(STIFFNESS_FILE_PATH, sep='\t', encoding='cp1252')


def create_data_manager():
    case_names = get_exp_case(hardness_time_data)
    data_manager = {name: {"raw_data": None,
                           "s_value": None,
                           "yield_point": None,
                           "er_value": None,
                           "creep_data": {}} for name in case_names}

    # raw data
    raw_data_insert(data_manager, case_names)
    s_value_insert(stiffness_data, data_manager, case_names)
    er_value_insert(stiffness_data, data_manager, case_names)
    creep_data_insert(data_manager, case_names)

    # fitting
    compute_creep_fitting(data_manager, case_names)

    #  calculation based on the function
    area_insert(data_manager, case_names)
    hardness_insert(data_manager, case_names)
    strain_rate_insert(data_manager, case_names)
    compute_log(data_manager, case_names)

    return data_manager


def creep_curve_function(t, a, b, k):  # t = time and a, b, k = fitting constants.
    h = a * (t ** b) + k * t
    return h


def compute_creep_fitting(data_manager, case_names):
    for case in case_names:
        x = data_manager[case]['creep_data']['creep_time']
        yn = data_manager[case]['creep_data']['creep_displacement']
        popt, pcov = curve_fit(creep_curve_function, x, yn)

        a = popt[0]
        b = popt[1]
        k = popt[2]

        fitted_h = [creep_curve_function(t, a, b, k) for t in x]
        data_manager[case]['creep_data']['fitted_creep_displacement'] = fitted_h


def compute_log(data_manager, case_names):
    for case in case_names:
        strain_rate_array = data_manager[case]['creep_data']['strain_rate']
        hardness_array = data_manager[case]['creep_data']['hardness']

        log_strain_rate_array = []
        log_hardness_array = []
        for i in range(len(strain_rate_array)):
            log_strain_rate = math.log(strain_rate_array[i])
            log_hardness = math.log(hardness_array[i])

            log_strain_rate_array.append(log_strain_rate)
            log_hardness_array.append(log_hardness)

        data_manager[case]['creep_data']['log_strain_rate'] = log_strain_rate_array
        data_manager[case]['creep_data']['log_hardness'] = log_hardness_array


def creep_data_insert(data_manager, case_names):
    for case in case_names:
        case_df = data_manager[case]['raw_data']

        creep_idx = find_creep_start_end_idx(case_df)
        creep_start_idx = creep_idx[0]
        creep_end_idx = creep_idx[1]

        t_0 = data_manager[case]['raw_data']['Time'][creep_start_idx]
        h_0 = data_manager[case]['raw_data']['Pd'][creep_start_idx]
        f_0 = data_manager[case]['raw_data']['Fn'][creep_start_idx]

        h = data_manager[case]['raw_data']['Pd'][creep_start_idx:creep_end_idx]
        t = data_manager[case]['raw_data']['Time'][creep_start_idx:creep_end_idx]
        f = data_manager[case]['raw_data']['Fn'][creep_start_idx:creep_end_idx]

        h_series = h - h_0  # normalizing
        t_series = t - t_0  # normalizing
        f_series = f

        displacement_list = h_series.tolist()
        time_list = t_series.tolist()
        load_list = f_series.tolist()

        data_manager[case]['creep_data']['creep_displacement_start'] = h_0.tolist()
        data_manager[case]['creep_data']['creep_time_start'] = t_0.tolist()

        data_manager[case]['creep_data']['creep_displacement'] = displacement_list
        data_manager[case]['creep_data']['creep_time'] = time_list
        data_manager[case]['creep_data']['creep_load'] = load_list


def strain_rate_insert(data_manager, case_names):
    for case in case_names:
        # case_df = data_manager[case]['raw_data']
        case_sqrt_area = data_manager[case]['creep_data']['sqrt_area_[m]']  # get list
        case_hardness = data_manager[case]['creep_data']['hardness']

        # creep_idx = find_creep_start_end_idx(case_df)
        # creep_start_idx = creep_idx[0]
        # creep_end_idx = creep_idx[1]

        # time_array = case_df['Time']
        time_array = data_manager[case]['creep_data']['creep_time']
        length_df = len(time_array)
        strain_rate_array = []

        step_size = START_STEP_SIZE

        for i in range(length_df - step_size):  # creep_end_idx-1 b.c. need to calc gradient.
            strain_rate = strain_rate_calc(case_sqrt_area[i], case_sqrt_area[i + step_size]
                                           , time_array[i], time_array[i + step_size])
            strain_rate_array.append(strain_rate)

        data_manager[case]['creep_data']['strain_rate'] = strain_rate_array


def strain_rate_calc(sqrt_area_1, sqrt_area_2, time_1, time_2):
    sqrt_area_grad = (sqrt_area_2 - sqrt_area_1)
    time_grad = (time_2 - time_1)
    strain_rate = (1 / sqrt_area_1) * (sqrt_area_grad / time_grad)

    return strain_rate


def hardness_insert(data_manager, case_names):
    for case in case_names:
        case_area = data_manager[case]['creep_data']['area_[mm^2]']  # get list
        fn_array = data_manager[case]['creep_data']['creep_load']
        length_df = len(fn_array)
        hardness_array = []
        j = 0
        for i in range(length_df):
            hardness = hardness_calc(fn_array[i], case_area[i])
            hardness_array.append(hardness)

        data_manager[case]['creep_data']['hardness'] = hardness_array


def area_insert(data_manager, case_names):
    for case in case_names:

        pd_series = data_manager[case]['creep_data']['fitted_creep_displacement']
        fn_series = data_manager[case]['creep_data']['creep_load']
        time_series = data_manager[case]['creep_data']['creep_time']
        case_stiffness = data_manager[case]['s_value']

        pd_0 = data_manager[case]['creep_data']['creep_displacement_start']

        length_df = len(pd_series)

        area_array = []
        sqrt_area_array = []
        time_array = []
        for i in range(length_df):
            area = area_calc(pd_series[i] + pd_0, fn_series[i], case_stiffness)
            time = time_series[i]
            sqrt_area = sqrt_area_calc(area)

            time_array.append(time)
            area_array.append(area)
            sqrt_area_array.append(sqrt_area)

        data_manager[case]['creep_data']['area_[mm^2]'] = area_array
        data_manager[case]['creep_data']['sqrt_area_[m]'] = sqrt_area_array
        data_manager[case]['creep_data']['time'] = time_array


def area_calc(pd, fn, stiffness):
    epsilon = 0.75
    radius = 10
    area = 2 * math.pi * radius * (pd - (epsilon * fn) / stiffness)
    return area


def hardness_calc(pd, area):
    hardness = (pd/area) * pow(10, 3)
    return hardness


def sqrt_area_calc(area):
    sqrt_area = math.sqrt(area * pow(10, -9))
    return sqrt_area


def find_creep_start_end_idx(time_fn_pd_data):
    """return array where the first element indicating creep start index and the second creep end index"""
    length_data = len(time_fn_pd_data)
    spacing = 20  # gradient spacing

    time = time_fn_pd_data['Time']
    fn = time_fn_pd_data['Fn']
    pd = time_fn_pd_data['Pd']

    for i in range(length_data - spacing):  # 0, 1, 3, ..., (max - spacing - 1)
        y1 = fn[i]
        y2 = fn[i+spacing]
        gradient_y = round((y2 - y1) * 100)

        if gradient_y == 0:
            creep_start_idx = i

            for j in range(creep_start_idx, length_data - spacing):
                y1 = fn[j]
                y2 = fn[j+spacing]
                gradient_y = round((y2 - y1) * 10)

                if gradient_y < 0:
                    creep_end_idx = j
                    break
            break

    return [creep_start_idx, creep_end_idx]


def s_value_insert(stiffness_df, data_dict, case_array):
    for case in case_array:
        rep = case.split("_")[-1]
        case_name = '_'.join(case.split("_")[0:-1])
        stiffness = get_stiffness(stiffness_df, case_name, int(rep))
        data_dict[case]['s_value'] = float(stiffness)


def er_value_insert(stiffness_df, data_dict, case_array):
    for case in case_array:
        rep = case.split("_")[-1]
        case_name = '_'.join(case.split("_")[0:-1])
        er = get_er(stiffness_df, case_name, int(rep))
        data_dict[case]['er_value'] = float(er)


def raw_data_insert(data_dict, case_array):
    for case in case_array:
        temp_df = get_displacement_time_dataframe(hardness_time_data, case)
        data_dict[case]['raw_data'] = temp_df


def get_exp_case(data_frame: pd.DataFrame):
    """receive pandas dataframe that contains nano-indentation creep experiment data,
    and return experiment cases as an array(list) of string"""
    columns = data_frame.columns

    temp_array = []
    for column in columns:
        split_name = column.split("_")[1:-2]  # choose only the name of the experiment cases
        combined_name = '_'.join(split_name)  # put them back together
        temp_array.append(combined_name)

    unique_array = []  # only get unique case name from experiment
    for case in temp_array:
        if (case not in unique_array) & (len(case) != 0):
            unique_array.append(case)

    return unique_array


def get_er(data_frame: pd.DataFrame, case: str, rep: int):
    """return elastic modulus based on data frame, case, and repetition"""
    er_value = data_frame['Value'][(stiffness_data['Group'] == case) &
                              (stiffness_data['Parameter'] == "Er (O&P)") &
                              (stiffness_data['Measurement'] == rep)].values[0]
    return er_value


def get_stiffness(data_frame: pd.DataFrame, case: str, rep: int):
    """return stiffness based on data frame, case, and repetition"""

    s_value = data_frame['Value'][(stiffness_data['Group'] == case) &
                              (stiffness_data['Parameter'] == "S (O&P)") &
                              (stiffness_data['Measurement'] == rep)].values[0]

    return s_value


def get_displacement_time_dataframe(data_frame, case_with_rep):
    time_column_name = f"X_{case_with_rep}_Time_[s]"
    load_column_name = f"Y_{case_with_rep}_Fn_[mN]"
    displacement_column_name = f"Y_{case_with_rep}_Pd_[nm]"

    temp_df = pd.DataFrame()
    temp_df['Time'] = data_frame[time_column_name]
    temp_df['Fn'] = data_frame[load_column_name]
    temp_df['Pd'] = data_frame[displacement_column_name]

    return temp_df


def main():
    data_manager = create_data_manager()
    plt.figure(1)
    for key, value in data_manager.items():
        x = data_manager[key]['raw_data']['Pd']
        y = data_manager[key]['raw_data']['Fn']
        plt.plot(x, y, '.')
    plt.xlabel('Depth (nm)')
    plt.ylabel('Load (mN)')

    plt.figure(2)
    for key, value in data_manager.items():
        x = data_manager[key]['creep_data']['creep_time']
        y = data_manager[key]['creep_data']['creep_displacement']
        fitted_y = data_manager[key]['creep_data']['fitted_creep_displacement']
        plt.plot(x, y, '.')
        plt.plot(x, fitted_y, 'k')
    plt.xlabel('creep_time (s)')
    plt.ylabel('creep_displacement (nm)')

    plt.figure(3)
    for key, value in data_manager.items():
        yield_point = data_manager[key]['yield_point']
        x = data_manager[key]['creep_data']['log_strain_rate']
        y = data_manager[key]['creep_data']['log_hardness']

        x_stable = x[-3000: -1]
        y_stable = y[-3000: -1]

        m, b = np.polyfit(x_stable, y_stable, 1)
        n = 1/m
        y2 = np.multiply(m, x_stable) + b
        print(f'SRS, m for {key}: {round(m,3)}')
        print(f'n for {key}: {round(n,3)}\n')

        plt.plot(x, y, 'o', label = f'{key} m: {round(m,3)}, n :{round(n,3)}')
        plt.plot(x_stable, y2, 'k')

    plt.legend()
    plt.xlabel('ln(Strain rate) (s^-1)')
    plt.ylabel('ln(Hardness) (GPa)')

    plt.show()


main()

