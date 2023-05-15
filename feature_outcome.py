import pandas as pd
import numpy as np
import trading_date
import os
from file_processing import File_process, makedir
from features_analysis import features_analysis
from use_func_and_store_outcome import Get_outcome

td = trading_date.Trading_date()
f_p = File_process()
fa = features_analysis()


class Get_feature_outcome:
    '''

    for one daily feature(if having neutralized,then it is the residual else raw feature data
    '''

    def __init__(self, f_name, global_path, absolute_daily_feature_path, neutral_merge_path, group_data_path,
                 group_alpha_path,absolute_stock_clean_data_path, absolute_raw_stock_data_path,
                 turnover_path, corr_path, feature_return_path, reg_method):

        '''
        daily data directory

        :param f_name: feature name
        :param global_path:
        :param absolute_daily_feature_path: feature daily data
        :param neutral_merge_path: merge feature data and other used to neutralized feature
        :param group_data_path: group data groupby  features
        :param group_alpha_path: alpha calculated by every group
        :param absolute_stock_clean_data_path: stock data after selecting
        :param absolute_raw_stock_data_path: for raw stock data to merge the T+2 Return
        :param turnover_path: the turnover of every group every day
        :param corr_path: IC of the features every day
        :param feature_return_path: feature data merge T+2 return
        :param reg_method: method use to neutralized feature. eg:OLS or Huber or ...
        '''

        self.f_name = f_name
        self.daily_feature_path = absolute_daily_feature_path
        self.global_method_path = makedir(global_path + r"/" + reg_method + r"/")
        # all the absolute paths of outcome
        self.neutral_merge_path = makedir(self.global_method_path + neutral_merge_path)
        self.group_data_path = makedir(self.global_method_path + group_data_path)
        self.group_alpha_path = makedir(self.global_method_path + group_alpha_path)
        self.stock_clean_data_path = absolute_stock_clean_data_path
        self.absolute_raw_stock_path = absolute_raw_stock_data_path
        self.turnover_path = makedir(self.global_method_path + turnover_path)
        self.corr_path = makedir(self.global_method_path + corr_path)
        self.feature_return_path = makedir(self.global_method_path + feature_return_path)

    def merge_data_for_neutralized(self, n_day_later = 0, stock_use_cols = None,
                                   start_date = '20100101', end_date = '20240101'):

        '''

        merge the features and same_day data
        '''

        merge_data_name = "merge_data.csv"
        data1_list = f_p.get_filelist_between_dates(os.listdir(self.daily_feature_path), start_date, end_date)
        data2_list = f_p.get_filelist_between_dates(os.listdir(self.stock_clean_data_path), start_date, end_date)

        stock_name_end = f_p.get_file_name_end(data2_list[0])
        last_date = min(f_p.get_name_date(data1_list[-1]), f_p.get_name_date(data2_list[-1]))
        Get_outcome.help_for_merge_n_days_later_data(self.daily_feature_path, data1_list, self.stock_clean_data_path,
                                                     stock_name_end, self.neutral_merge_path, merge_data_name,
                                                     fa.get_merge_same_date_data, n_day_later,
                                                     last_date, data2_use_cols = stock_use_cols)

    def neutralized_feature_OLS(self, feature_column_name, factors, log_or_not = False, residual_path = r"residual/",
                                start_date = '20100101', end_date = '20240101', winsor_or_not = True):

        '''

        :param feature_column_name: the column name of y in the regression
        :param factors: for neutralized
        :param residual_path:
        :param start_date:
        :param end_date:
        :param winsor_or_not: winsor the feature, default is True
        :return:
        '''

        merge_data_list = f_p.get_filelist_between_dates(os.listdir(self.neutral_merge_path),start_date,end_date)
        reg_residual_path = makedir(self.global_method_path + residual_path)
        for file in merge_data_list:
            if file.endswith(".csv"):
                date = f_p.get_name_date(file)
                f_a_reg = features_analysis()
                merge_data = pd.read_csv(self.neutral_merge_path + file, index_col = 'Ticker')
                if log_or_not:
                    f_a_reg.get_reg_data_neutralized_log(feature_column_name, merge_data, factors = factors,
                                                         winsor_or_not = winsor_or_not)
                else:

                    f_a_reg.get_reg_data_neutralized_not_log(feature_column_name, merge_data, factors = factors,
                                                             winsor_or_not = winsor_or_not)

                res = f_a_reg.OLS(self.f_name + "_" + "residual")
                res.to_csv(reg_residual_path + date + ".residual.csv", index_label = ('Ticker'))

        self.residual_path = reg_residual_path

    def neutralized_feature_Huber(self, feature_column_name, factors, log_or_not = False,
                                  residual_path = r"residual/", start_date = '20100101',
                                  end_date = '20240101', winsor_or_not = True):

        merge_data_list = f_p.get_filelist_between_dates(os.listdir(self.neutral_merge_path), start_date, end_date)

        reg_residual_path = makedir(self.global_method_path + residual_path)
        for file in merge_data_list:
            if file.endswith(".csv"):
                date = f_p.get_name_date(file)
                f_a_reg = features_analysis()
                merge_data = pd.read_csv(self.neutral_merge_path + file, index_col = 'Ticker')
                if log_or_not:
                    f_a_reg.get_reg_data_neutralized_log(feature_column_name, merge_data, factors = factors,
                                                         winsor_or_not = winsor_or_not)
                else:
                    f_a_reg.get_reg_data_neutralized_not_log(feature_column_name, merge_data, factors = factors,
                                                             winsor_or_not = winsor_or_not)

                res = f_a_reg.Huber(self.f_name + "_" + "residual")

                res.to_csv(reg_residual_path + date + ".residual.csv", index_label = ('Ticker'))

        self.residual_path = reg_residual_path

    def merge_fea_later_return(self, n_day_later = 2, start_date = '20100101', end_date = '20240101'):
        '''

        merge the features and T+2 return
        '''

        stock_use_cols = ['Ticker', 'Return']
        merge_data_name = "merge_data.csv"
        data1_list = f_p.get_filelist_between_dates(os.listdir(self.residual_path), start_date, end_date)
        data2_list = f_p.get_filelist_between_dates(os.listdir(self.absolute_raw_stock_path), start_date, end_date)
        stock_name_end = f_p.get_file_name_end(data2_list[0])
        last_date = min(f_p.get_name_date(data1_list[-1]), f_p.get_name_date(data2_list[-1]))
        Get_outcome.help_for_merge_n_days_later_data(self.residual_path, data1_list, self.absolute_raw_stock_path,
            stock_name_end, self.feature_return_path, merge_data_name, fa.get_merge_later_T2_return, n_day_later,
            last_date,data2_use_cols = stock_use_cols)


    def get_IC_daily(self, start_date = '20100101', end_date = '20240101'):
        '''

        get IC of all dates
        '''

        corr_all = pd.DataFrame()
        name_list = f_p.get_filelist_between_dates(os.listdir(self.feature_return_path), start_date, end_date)
        feature_return_name_end = f_p.get_file_name_end(name_list[0])
        for name_t in name_list:
            if name_t.endswith(".csv"):
                date = f_p.get_name_date(name_t)
                data = pd.read_csv(self.feature_return_path + date + "." + feature_return_name_end,
                                   index_col = 0)
                # if n days later return is nan, then make it 0
                data['Return'].fillna(0, inplace = True)
                corr = fa.calculate_IC(data, self.f_name + "_residual")
                c = pd.DataFrame(index = [date], columns = ['corr'], data = corr)
                corr_all = pd.concat([corr_all, c])

        corr_all.to_csv(self.corr_path + self.f_name + "_residual.corr.csv")
        return corr_all

    def get_group_data(self, group_num = 10, start_date = '20100101', end_date = '20240101'):
        '''

        get the group data
        '''

        name_list = f_p.get_filelist_between_dates(os.listdir(self.feature_return_path), start_date, end_date)

        for name_t in name_list:
            if name_t.endswith(".csv"):
                date = f_p.get_name_date(name_t)
                data = pd.read_csv(self.feature_return_path + name_t, index_col = 0)
                group = fa.groupby_features(data, self.f_name + "_residual", group_num)
                group['Date'] = date
                group_a = fa.get_group_alpha(group)
                group_a['Date'] = date
                group.to_csv(self.group_data_path + date + "." + self.f_name + "_residual.group.csv")
                group_a.to_csv(self.group_alpha_path + date + "." + self.f_name + "_residual.alpha.csv",
                               index_label = ('group'))

    def concat_group_alpha_data(self, start_date = '20100101', end_date = '20240101'):

        # concat all the group return
        group_list = f_p.get_filelist_between_dates(os.listdir(self.group_alpha_path),start_date,end_date)
        all_group_alpha_data = pd.DataFrame()
        for group in group_list:
            if group.endswith(".csv"):
                data = pd.read_csv(self.group_alpha_path + group, index_col = ['Date'])
                all_group_alpha_data = pd.concat([all_group_alpha_data, data])

        all_group_alpha_data.to_csv(self.global_method_path + self.f_name + ".all_group_alpha.csv")
        return all_group_alpha_data

    def get_group_alpha_nav(self, all_group_alpha_data):
        '''

        get group_alpha_nav
        :param all_group_alpha_data
        '''

        alpha_nav = all_group_alpha_data.groupby('group').apply(
            lambda x: (x['alpha'] / 10000 + 1).cumprod()).stack().unstack(
            level = 0)
        alpha_nav.to_csv(self.global_method_path + "group_alpha_nav" + ".csv")
        return alpha_nav

    @staticmethod
    def get_evaluation_alpha_IC_IR(corr_all_stock, trading_days_n = 252):
        '''
        the latest year may contain only a little data, so calculate it with its last year together.

        :param corr_all_stock: index is date, corr of alpha and the feature value every day
        '''

        IR_e = fa.get_alpha_IR_groupby_year(corr_all_stock, trading_days_n)
        IC_e = fa.get_alpha_IC_evaluation_groupby_year(corr_all_stock)
        evaluation_all = pd.concat([IR_e, IC_e], axis = 1)
        return evaluation_all
