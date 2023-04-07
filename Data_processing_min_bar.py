import pandas as pd
import os

path = r"E:/Quant Practice/Raw Data/"
bar_data_path = path + r"StockMinuteBar/"


class Data_process:
    def process(self, data):
        '''

        :param data: raw min data with index time
        :return:
        '''
        data['Ticker'] = data['code'].apply(lambda x: str(x.split(".")[0]))
        return data

