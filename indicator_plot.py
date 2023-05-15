import matplotlib.pyplot as plt
import pandas as pd
import os
from features_analysis import features_analysis
from trading_date import Trading_date
import multiprocessing
from use_func_and_store_outcome import Get_outcome
from file_processing import makedir, File_process
import numpy as np
import warnings
import datetime

warnings.filterwarnings('ignore')
td = Trading_date()
'''
indicator calculated from bar data.
'''

f_p = File_process()
f_a = features_analysis()
feature_analysis_path = r"E:/研究生课程代码/algorithm trading/High_Frequent_factor/"
global_analysis_path = makedir(feature_analysis_path + "Analysis/")
# outcome image path
outcome_image_path = makedir(global_analysis_path + r"Image/")
# feature plot path
feature_plot_path = makedir(outcome_image_path + r"feature_plot/")


# file = os.listdir(feature_path)[0]
class Feature_plot:

    def history_distribution(self, feature_name, feature_path, feature_plot_path):
        data_all_list = []
        for file in os.listdir(feature_path):
            fseries = pd.read_csv(feature_path + file, usecols = [1]).iloc[:, 0]
            feature = f_a.winsor(fseries)
            data_list = feature.values.reshape(-1, ).tolist()
            data_all_list = data_all_list + data_list
        plt.hist(x = data_all_list, bins = 100, )
        plt.title(feature_name)
        plt.savefig(feature_plot_path + feature_name + ".png")
        plt.show()

    def get_percentage_change(self, feature_name, feature_path, feature_plot_path):
        percentage_list = [10, 25, 50, 75, 90]
        start_date = f_p.get_name_date(os.listdir(feature_path)[0])
        end_date = f_p.get_name_date(os.listdir(feature_path)[-1])
        percentage_df = pd.DataFrame(index = td.get_date_list_between_two_dates(start_date, end_date),
                                     columns = [str(x) for x in percentage_list])
        for file in os.listdir(feature_path):
            date = f_p.get_name_date(file)
            fseries = pd.read_csv(feature_path + file, usecols = [1]).iloc[:, 0]
            for per in percentage_list:
                percentage_df.loc[date, str(per)] = np.percentile(fseries, per)

        percentage_df.index = pd.to_datetime(percentage_df.index)
        percentage_df.plot()
        plt.legend(percentage_df.columns)
        plt.title(feature_name+": Cross-Sectional Percentiles")
        plt.savefig(feature_plot_path + feature_name + "percentage.png")


for feature_name in ['RV', 'RSkew', 'Rkurtosis']:
    feature_path = feature_analysis_path + feature_name + r"/"
    Feature_plot().history_distribution(feature_name, feature_path, feature_plot_path)
    Feature_plot().get_percentage_change(feature_name, feature_path, feature_plot_path)
