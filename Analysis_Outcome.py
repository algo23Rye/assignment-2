import pandas as pd
import matplotlib.pyplot as plt
from feature_outcome import *

plt.switch_backend('agg')

feature_analysis_path = makedir(r"E:/研究生课程代码/algorithm trading/High_Frequent_factor/")
global_analysis_path = makedir(feature_analysis_path + "Analysis/")
absolute_raw_stock_path = r"E:/Quant Practice/Raw Data/StockUniverse/"

neutral_merge_path = r"neutral_merge_data/"
# group data groupby by features
group_data_path = r"group_data/"
# alpha calculated by every group
group_alpha_path = r"group_return_alpha/"
# the turnover of every group every day
turnover_path = r"turnover/"
# stock date after selecting
absolute_stock_clean_path = 'E:/Quant Practice/Data/stock_clean/'
# IC of the features every day
corr_path = r"corr/"
# feature data merge T+2 return
feature_return_path = "resi_return/"
# the alpha before and after minus the cost
alpha_compare_path = r"group_alpha_compare/"
# outcome image path
outcome_image_path = makedir(global_analysis_path + r"Image/")
# alpha_nav plot path
alpha_nav_plot_path = makedir(outcome_image_path + r"alpha_nav/")

startdate = "20160104"


def get_outcome(reg_method):
    for feature_name in os.listdir(feature_analysis_path):
        if feature_name not in ['Analysis']:
            factors = ['Log_TCap', 'Industry']
            factor_global_path = makedir(global_analysis_path + feature_name + r"/")
            absolute_daily_feature_path = feature_analysis_path + feature_name + r"/"
            feature_name_end = os.listdir(absolute_daily_feature_path)[0]
            group_num = 5

            ma_f = Get_feature_outcome(feature_name, factor_global_path, absolute_daily_feature_path,
                                       neutral_merge_path,
                                       group_data_path, group_alpha_path, absolute_stock_clean_path,
                                       absolute_raw_stock_path, turnover_path, corr_path, feature_return_path,
                                       reg_method = reg_method)

            ma_f.merge_data_for_neutralized(start_date = startdate)
            feature_column_name1 = pd.read_csv(absolute_daily_feature_path + feature_name_end).columns[1]
            ma_f.neutralized_feature_OLS(feature_column_name1, factors, log_or_not = False, start_date = startdate)
            ma_f.merge_fea_later_return()
            ma_f.get_IC_daily()
            ma_f.get_group_data(group_num)
            all_group_data_alpha = ma_f.concat_group_alpha_data()
            group_alpha_nav = ma_f.get_group_alpha_nav(all_group_data_alpha)
            group_alpha_nav.index = pd.to_datetime(group_alpha_nav.index.astype('str'))
            group_alpha_nav.plot()
            plt.title(feature_name + ": " + ",".join(factors))
            plt.savefig(alpha_nav_plot_path + feature_name + "_" + reg_method + "_" + "_".join(factors) + ".png")

for reg_method in ["OLS", "Huber"]:
    get_outcome(reg_method)


# because Rkurtosis performs well, so get its IR IC evaluation, "Huber"
corr_all_stock = pd.read_csv(
    r'E:\研究生课程代码\algorithm trading\High_Frequent_factor\Analysis\Rkurtosis\Huber\corr\Rkurtosis_residual.corr.csv',
    parse_dates = True, index_col = 0)

Get_feature_outcome.get_evaluation_alpha_IC_IR(corr_all_stock).to_csv(makedir("./Rkurtosis_eval/") + "eval.csv")
