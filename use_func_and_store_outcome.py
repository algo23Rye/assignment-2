import os

import pandas as pd
import trading_date
import file_processing

td = Trading_date.Trading_date()
f_p = File_processing.File_process()


class Get_outcome:

    @staticmethod
    def split_list(list, n):
        '''

        split file list to do multiprocessing

        :param list: list to be split
        :param n: split to n parts
        :return: a list containts n lists
        '''
        list_split = []
        num = int(len(list) / n) + 1
        for i in range(n):
            a_list = list[i * num:min((i + 1) * num, len(list) + 1)]
            if len(a_list) != 0:
                list_split.append(a_list)

        return list_split

    @staticmethod
    def help_for_one_dir_one_function(data_path, data_filelist, index_col_name, store_path, store_name_end, function):
        for data_name in data_filelist:
            date = data_name.split(".")[0]
            store_name = date + "." + store_name_end
            data = pd.read_csv(data_path + data_name, index_col=index_col_name)
            outcome = function(data)
            outcome.to_csv(store_path + store_name)

    @staticmethod
    def help_for_one_dir_functions(data_path, data_filelist, index_col_name, store_path_list, store_name_end,
                                   function_list, index_label_store):
        '''

        for same structure of functions,such as different method

        '''

        for data_name in data_filelist:
            data = pd.read_csv(data_path + data_name, index_col=index_col_name)
            date = data_name.split(".")[0]
            store_name = date + "." + store_name_end
            for i in range(0, len(function_list)):
                outcome = function_list[i]()
                outcome.to_csv(store_path_list[i] + store_name, index_label=(index_label_store))

    @staticmethod
    def help_for_clean_stock(data_path, data_filelist, store_path, store_name_end, function, data_use_cols):
        for data_name in data_filelist:
            date = f_p.get_name_date(data_name)
            store_name = date + "." + store_name_end
            data = pd.read_csv(data_path + data_name, usecols=data_use_cols)
            outcome = function(data)
            outcome.to_csv(store_path + store_name, encoding='gbk')

    @staticmethod
    def help_for_merge_same_date_data(data_path1, data_filelist1, data_path2, data_name_end_2, store_path,
                                      store_name_end, function, data1_use_cols=None, data2_use_cols=None):
        '''

        merge the data1 and data 2

        :param data_path1: data1 path
        :param data_filelist1: the file in the data_path1
        :param data_path2: data2 path
        :param data_name_end_2: the filename of data2 exclude the date
        :param store_path:
        :param store_name_end:
        :param function:
        '''

        for data_name1 in data_filelist1:
            # get the date
            date = f_p.get_name_date(data_name1)
            # the name for store data
            store_name = date + "." + store_name_end
            # the name for data2 at the same date
            data_name2 = date + "." + data_name_end_2
            data1 = pd.read_csv(data_path1 + data_name1, usecols=data1_use_cols, encoding='gbk')
            data2 = pd.read_csv(data_path2 + data_name2, usecols=data2_use_cols, encoding='gbk')
            outcome = function(data1, data2)
            outcome.to_csv(store_path + store_name)

    @staticmethod
    def help_for_merge_n_days_later_data(data_path1, data_filelist1, data_path2, data_name_end_2,
                                         store_path, store_name_end, function, n, last_date, data1_use_cols=None,
                                         data2_use_cols=None):

        '''
        :param n:n days later
        :param last_date: the latest date
        :return:
        '''
        for data_name1 in data_filelist1:
            date = str(td.get_n_days_later_td(int(f_p.get_name_date(data_name1)), n))
            if date <= last_date:
                store_name = date + "." + store_name_end
                data_name2 = date + "." + data_name_end_2
                data1 = pd.read_csv(data_path1 + data_name1, usecols=data1_use_cols, encoding='gbk')
                data2 = pd.read_csv(data_path2 + data_name2, usecols=data2_use_cols,encoding='gbk',encoding_errors="ignore")
                outcome = function(data1, data2)
                outcome.to_csv(store_path + store_name)
