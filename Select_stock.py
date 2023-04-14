import pandas as pd
import os
import Trading_date
import multiprocessing
from File_processing import makedir, File_process
from Use_func_and_store_outcome import Get_outcome

f_p = File_process()
td = Trading_date.Trading_date()

path = r"E:/Quant Practice/Raw Data/"
stock_data_path = path + r"/StockUniverse/"
stock_clean_path = makedir(makedir(r"E:/Quant Practice/Data/") + r"stock_clean/")


class Clean_stock_data:
    def get_all_stock_to_trade(self, stock_data):
        # select the st stock and suspendened stock

        # from 2022.08 add 'ToBeST' and 'ToBeDelisted'
        if ('ToBeST' in stock_data.columns) & ('ToBeDelisted' in stock_data.columns):
            st_stock = stock_data[
                (stock_data.IsSuspended != 0) | (stock_data.IsST != 0) | (stock_data.DelistStatus != 0) | (
                        stock_data.ToBeST != 0) | (stock_data.ToBeDelisted != 0)]

        else:
            st_stock = stock_data[
                (stock_data.IsSuspended != 0) | (stock_data.IsST != 0) | (stock_data.DelistStatus != 0)]

        de_st = stock_data.drop(index = st_stock.index, axis = 0)

        # drop if trading period less than 100
        select = de_st[de_st.apply(lambda x: td.days_bewteen_two_dates(x['StartDate'], x['Date']), axis = 1) > 100]
        select = select.reset_index(drop = True).set_index(['Date'])
        return select


date_start = '20160104'
date_end = "20240101"

data_list = pd.DataFrame(data = os.listdir(stock_data_path))
data_use = data_list[[x.split(".")[0] >= date_start and x.split(".")[0] < date_end for x in data_list.iloc[:, 0]]]
data_list_use = list(data_use.iloc[:, 0].values)

c_data = Clean_stock_data()
if __name__ == '__main__':
    c_data = Clean_stock_data()
    cpu_num = multiprocessing.cpu_count() - 4
    split = Get_outcome.split_list(data_list_use, cpu_num)
    pool = multiprocessing.Pool(processes = cpu_num)
    for filelist in split:
        train = pool.apply_async(Get_outcome.help_for_clean_stock,
                                 args = (stock_data_path, filelist, stock_clean_path, "stock_clean.csv",
                                         c_data.get_all_stock_to_trade, None))
    pool.close()
    pool.join()
