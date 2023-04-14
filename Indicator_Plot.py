import matplotlib.pyplot as plt
import pandas as pd
import os
from Features_analysis import features_analysis
import multiprocessing
from Use_func_and_store_outcome import Get_outcome
from File_processing import makedir, File_process
import numpy as np
import warnings

warnings.filterwarnings('ignore')

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
        #TrueRV = [x / 10000 for x in data_all_list]
        plt.hist(x = data_all_list, bins = 100,)
        plt.title(feature_name)
        plt.savefig(feature_plot_path + feature_name + ".png")
        plt.show()


for feature_name in ['RV', 'RSkew', 'Rkurtosis']:
    feature_path = feature_analysis_path + feature_name + r"/"
    Feature_plot().history_distribution(feature_name, feature_path, feature_plot_path)
