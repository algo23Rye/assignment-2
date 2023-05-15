import pandas as pd
from data_processing_min_bar import Data_process, bar_data_path
import os
import multiprocessing
from use_func_and_store_outcome import Get_outcome
from file_processing import makedir, File_process
import numpy as np
import warnings

warnings.filterwarnings('ignore')

'''
indicator calculated from bar data.
'''

f_p = File_process()
dp = Data_process()

feature_analysis_path = makedir(r"E:/研究生课程代码/algorithm trading/High_Frequent_factor/")


class Indicator:

    def calculate_r2(self, x):
        x = x.sort_index()
        x['c_shift'] = x['close'].shift(1)
        # the first one use open price
        x['c_shift'][0] = x['open'][0]
        r2 = (np.log(x['close'] / x['c_shift'])) ** 2
        bigr2 = r2 * 10000
        return bigr2

    def get_rv(self, data):
        '''
        calculate daily realized volatility
        data: data with index time after data processing
        :return:
        '''

        r2 = (data.groupby('Ticker').apply(lambda x: self.calculate_r2(x)).stack(dropna = False)).to_frame()
        r2.columns = ['return^2']
        rv = (r2['return^2'].groupby('Ticker').sum()).to_frame()
        rv.columns = ['RV']
        return rv

    def calculate_logr(self, x):
        x = x.sort_index()
        x['c_shift'] = x['close'].shift(1)
        # the first one use open price
        x['c_shift'][0] = x['open'][0]
        r = np.log(x['close'] / x['c_shift'])
        return r

    def get_rskew(self, data):
        r = (data.groupby('Ticker').apply(lambda x: self.calculate_logr(x)).stack(dropna = False)).to_frame()
        r.columns = ['logr']
        rskew = r['logr'].groupby('Ticker').apply(
            lambda x: (((x ** 3).sum()) * np.sqrt(len(x))) / ((x ** 2).sum()) ** (3 / 2)).to_frame()

        rskew.dropna(inplace = True)
        rskew.columns = ['Rskew']
        return rskew

    def get_rkurtosis(self, data):
        r = (data.groupby('Ticker').apply(lambda x: self.calculate_logr(x)).stack(dropna = False)).to_frame()
        r.columns = ['logr']
        rkurtosis = r['logr'].groupby('Ticker').apply(
            lambda x: (((x ** 4).sum()) * len(x)) / ((x ** 2).sum()) ** 2).to_frame()

        rkurtosis.dropna(inplace = True)
        rkurtosis.columns = ['Rkurtosis']
        return rkurtosis


ind = Indicator()

feature_dict = {
    "RV": {"path": makedir(feature_analysis_path + r"RV/"),
           "function": ind.get_rv
           },
    "RSkew": {"path": makedir(feature_analysis_path + r"RSkew/"),
              "function": ind.get_rskew
              },
    "Rkurtosis": {"path": makedir(feature_analysis_path + r"Rkurtosis/"),
                  "function": ind.get_rkurtosis
                  },
}


class Calculation:
    def __init__(self, feature_name, bar_data_path, feature_analysis_path, feature_dir):
        self.feature_name = feature_name
        self.bar_data_path = bar_data_path
        self.feature_analysis_path = makedir(feature_analysis_path)
        self.feature_path = makedir(self.feature_analysis_path + feature_dir)

    def get_feature(self, function, data_list):

        for file in data_list:
            if file.endswith(".csv"):
                date = f_p.get_name_date(file)
                data1 = pd.read_csv(self.bar_data_path + file, index_col = ['time'])
                data = dp.process(data1)
                feature = function(data)
                feature.to_csv(self.feature_path + date + "." + self.feature_name + ".csv")

    @staticmethod
    def get_features(bar_data_path, data_list, feature_dict):
        for file in data_list:
            if file.endswith(".csv"):
                date = f_p.get_name_date(file)
                data1 = pd.read_csv(bar_data_path + file, index_col = ['time'])
                data = dp.process(data1)
                for feature_name in feature_dict.keys():
                    feature_dict[feature_name]["function"](data).to_csv(
                        feature_dict[feature_name]["path"] + date + "." + feature_name + ".csv")


#
start_date = '20160104'
end_date = '20240101'

if __name__ == '__main__':
    cpu_num = multiprocessing.cpu_count() - 4
    data_list = f_p.get_filelist_between_dates(os.listdir(bar_data_path), start_date, end_date)
    split = Get_outcome.split_list(data_list, cpu_num)
    pool = multiprocessing.Pool(processes = cpu_num)
    for filelist in split:
        train = pool.apply_async(Calculation.get_features,
                                 args = (bar_data_path, filelist, feature_dict))
    pool.close()
    pool.join()
