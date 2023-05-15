import pandas as pd
import numpy as np
import trading_date
import os
from file_processing import File_process
from sklearn.linear_model import LinearRegression, HuberRegressor
from pandas import DataFrame, Series
import warnings

warnings.filterwarnings('ignore')

td = trading_date.Trading_date()
f_p = File_process()


class features_analysis:

    def get_merge_same_date_data(self, features, stock_data):
        merge_data = pd.merge(features, stock_data, left_on = ['Ticker'], right_on = ['Ticker'], how = 'inner')
        return merge_data

    def get_merge_later_T2_return(self, features, stock_data):
        '''

        in order to get the later return of stock
        '''

        merge_data = pd.merge(features, stock_data, left_on = ['Ticker'], right_on = ['Ticker'], how = 'left')
        return merge_data

    def winsor(self, feature: Series):
        if feature.dropna().shape[0] != 0:
            feature.loc[feature < np.percentile(feature.dropna(), 5)] = np.percentile(feature.dropna(), 5)
            feature.loc[feature > np.percentile(feature.dropna(), 95)] = np.percentile(feature.dropna(), 95)
        else:
            feature = feature.fillna(0)
        return feature

    def get_reg_data_neutralized_not_log(self, feature_name, merge_data, factors, winsor_or_not = True):
        '''

        :param merge_data: from get_merge_data
        :param factors: neutralized the features on this factors
        :param winsor_or_not: winsor the feature, default is True
        '''

        merge_data.dropna(inplace = True)
        merge_data['Log_TCap'] = np.log(merge_data['TCap'])
        merge_data['Log_MCap'] = np.log(merge_data['MCap'])
        merge_data['Log_Amount'] = np.log(merge_data['Amount'])
        merge_data['Turnover'] = merge_data['Amount'] / merge_data['MCap']

        # get dummy variables of industry
        if 'Industry' in factors:
            industry_dummy = pd.get_dummies(merge_data['Industry1'], prefix = 'Industry1', prefix_sep = "_")
            merge_data = pd.concat([merge_data, industry_dummy], axis = 1)
            factors.remove('Industry')
            reg_x = merge_data.loc[:, factors + factors + industry_dummy.columns.tolist()[0:-1]]
            factors.append('Industry')

        else:
            reg_x = merge_data.loc[:, factors]

        if winsor_or_not:
            reg_y = self.winsor(merge_data[feature_name])
        else:
            reg_y = merge_data[feature_name]

        self.reg_x = reg_x
        self.reg_y = reg_y

        return merge_data

    def get_reg_data_neutralized_log(self, feature_name, merge_data, factors, winsor_or_not = True):
        '''
        if the feature need to get log

        :param merge_data: from get_merge_data
        :param factors: neutralized the features on this factors
        :param winsor_or_not: winsor the feature, default is True
        '''

        merge_data.dropna(inplace = True)
        merge_data['Log_TCap'] = np.log(merge_data['TCap'])
        merge_data['Log_MCap'] = np.log(merge_data['MCap'])
        merge_data['Log_Amount'] = np.log(merge_data['Amount'])
        merge_data['Turnover'] = merge_data['Amount'] / merge_data['MCap']

        # log of the feature
        merge_data[feature_name] = np.log(merge_data[feature_name])

        if 'Industry' in factors:
            industry_dummy = pd.get_dummies(merge_data['Industry1'], prefix = 'Industry1', prefix_sep = "_")
            merge_data = pd.concat([merge_data, industry_dummy], axis = 1)
            factors.remove('Industry')
            reg_x = merge_data.loc[:, factors + factors + industry_dummy.columns.tolist()[0:-1]]
            factors.append('Industry')

        else:
            reg_x = merge_data.loc[:, factors]

        if winsor_or_not:
            reg_y = self.winsor(merge_data[feature_name])
        else:
            reg_y = merge_data[feature_name]

        self.reg_x = reg_x
        self.reg_y = reg_y

        return merge_data

    def OLS(self, f_name):
        lr = LinearRegression().fit(self.reg_x, self.reg_y)
        residual = (self.reg_y - lr.predict(self.reg_x)).to_frame()
        residual.columns = [f_name]
        return residual

    def Huber(self, f_name):
        huber = HuberRegressor(max_iter = 1000).fit(self.reg_x, self.reg_y)
        residual = (self.reg_y - huber.predict(self.reg_x)).to_frame()
        residual.columns = [f_name]
        return residual

    def calculate_IC(self, data, feature_name):
        '''

        :param data: the dataframe contains the T+2 return ['Return'] every day
        :param feature_name: the name of the feature's column
        :return: IC every day
        '''

        data['Return'] = data['Return'].fillna(0)
        data['alpha'] = data['Return'] - data['Return'].mean()
        corr = np.corrcoef(data[feature_name], data['alpha'])[0, 1]
        return corr

    def groupby_features(self, feature_return_data, feature_name, group_num):
        '''

        get groups by the feature

        :param feature_return_data: merge data
        :param feature_name: the name of the feature's column
        :param group_num: split into group_num groups
        :return: daily group alpha(every stock return minus mean(stock_return)
        '''

        feature_return_data.sort_values(by = feature_name, inplace = True)
        feature_return_data['group'] = pd.qcut(feature_return_data[feature_name], group_num,
                                               labels = range(group_num)).values
        feature_return_data['alpha'] = feature_return_data['Return'] - (feature_return_data['Return']).mean()
        return feature_return_data

    def get_group_alpha(self, group_data):
        '''

        get alpha_return of every group

        :param group_data: data with group
        :return: daily group alpha(every stock return minus mean(stock_return)
        '''

        group_return = (group_data.groupby('group').apply(lambda x: x['alpha'].mean())).to_frame()
        group_return.columns = ['alpha']
        return group_return

    def get_group_nav(self, data):
        '''

        :param data: the concat data of all dates
        :return: the nav of n groups
        '''

        # the alpha and return is measured in bps
        alpha_nav = data.groupby('group').apply(lambda x: (x['alpha'] / 10000 + 1).cumprod()).stack().unstack(level = 0)
        return alpha_nav

    def get_equal_weight(self, data):
        '''

        for every group, add the equal investment ratio
        '''

        equal_weight_each_group = (data.groupby(by = ['group']).apply(lambda x: 1 / len(x))).to_frame()
        equal_weight_each_group.columns = ['weight']
        concat_data = pd.merge(data, equal_weight_each_group, left_on = ['group'], right_index = True)
        return concat_data

    def get_turnover_every_group(self, data1, data2):
        '''

        get daily turnover for every group
        '''

        w_data = data1.groupby('group').apply(lambda x: pd.merge(x.loc[:, ['Ticker', 'weight']],
                               data2[data2['group'] == x.name].loc[:, ['Ticker', 'weight']],
                               how = 'outer',left_on = ['Ticker'], right_on = ['Ticker']))
        w_data = (w_data.droplevel(level = 1)).fillna(0)
        # binary
        turnover = (w_data.groupby('group').apply(lambda x: (abs(x['weight_x'] - x['weight_y'])).sum())).to_frame()
        turnover.columns = ['turnover']
        return turnover

    def get_alpha_IR_groupby_year(self, corr_all_stock, trading_days_n = 252):
        '''
        the latest year may contain only a little data, so calculate it with its last year together.

        :param corr_all_stock: index is date, corr of alpha and the feature value every day

        '''
        latest_year = corr_all_stock.index.year.unique()[-1]
        alpha_IR = corr_all_stock[corr_all_stock.index.year < latest_year - 1].groupby(
            corr_all_stock[corr_all_stock.index.year < latest_year - 1].index.year).apply(
            lambda x: x['corr'].mean() / x['corr'].std() * np.sqrt(trading_days_n)).to_frame()
        alpha_IR.index = alpha_IR.index.astype('str')
        alpha_IR_latest = corr_all_stock[corr_all_stock.index.year >= latest_year - 1]['corr'].mean() / \
                          corr_all_stock[corr_all_stock.index.year >= latest_year - 1]['corr'].std() * np.sqrt(
            trading_days_n)
        alpha_IR = pd.concat([alpha_IR, pd.DataFrame(
            index = [str(latest_year - 1) + " till " + str(corr_all_stock.index[-1].date())], data = alpha_IR_latest,
            columns = [0])])
        alpha_IR.columns = ['alpha_IR']

        return alpha_IR

    def get_alpha_IC_evaluation_for_one_part(self, corr_all_stock_part):
        eval = pd.DataFrame(index = [str(corr_all_stock_part.index[0].year)],
                            columns = ["alpha_IC_" + x for x in ["mean", "std", "min", "max", "negative_value_ratio"]])
        eval["alpha_IC_mean"] = corr_all_stock_part['corr'].mean()
        eval["alpha_IC_std"] = corr_all_stock_part['corr'].std()
        eval["alpha_IC_min"] = corr_all_stock_part['corr'].min()
        eval["alpha_IC_max"] = corr_all_stock_part['corr'].max()
        eval["alpha_IC_negative_value_ratio"] = len(corr_all_stock_part[corr_all_stock_part['corr'] < 0]) / len(
            corr_all_stock_part['corr'])
        return eval

    def get_alpha_IC_evaluation_groupby_year(self, corr_all_stock):
        '''
        the latest year may contain only a little data, so calculate it with its last year together.

        :param corr_all_stock: index is date, corr of alpha and the feature value every day

        '''
        latest_year = corr_all_stock.index.year.unique()[-1]
        history_part1 = corr_all_stock[corr_all_stock.index.year < latest_year - 1]
        history_part2 = corr_all_stock[corr_all_stock.index.year >= latest_year - 1]
        alpha_IC_eval1 = history_part1.groupby(history_part1.index.year).apply(
            lambda x: self.get_alpha_IC_evaluation_for_one_part(x)).droplevel(0)
        alpha_IC_eval2 = self.get_alpha_IC_evaluation_for_one_part(history_part2)
        alpha_IC_eval2.index = [alpha_IC_eval2.index[0] + " till " + str(corr_all_stock.index[-1].date())]
        alpha_IC_eval = pd.concat([alpha_IC_eval1, alpha_IC_eval2])
        return alpha_IC_eval


