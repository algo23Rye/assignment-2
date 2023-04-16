# 研报复现作业二

作业二主要是参考了广发证券《基于日内高频数据的短周期选股因子研究：高频数据因子研究系列一》

研究中有如下不同：

1. 本次测试区间从2016年到2023年2月，使用1分钟交易数据计算因子以及清理日度频率数据得到股票池。
2. 原研报研究中考虑的是因子在月频的表现，根据个人研究兴趣，这里考虑因子的日频表现。
3. 由于数据限制，这里只考虑因子在全市场股票中的表现（每天的股票池去掉剔除ST股票、*ST股票、停牌股票上市不满100天的股票），没有把中证500股票池另外抽出来研究。
4. 在分组回测时，这里把三个因子对上下5%的值进行winsor处理，然后进行了市值和行业中性化（用OLS和Huber两种回归方法）。
5. 为了更好地观察分组表现，这里画出各组alpha净值曲线（组内股票等权），（每只股票的alpha即每天每只股票收益率减去当天股票池所有股票收益率的均值）。在计算因子的IC和IR时，也是用股票的alpha和因子值来计算。

## 因子描述性统计

1. 全样本因子分布(winsor后）
   注：这里的RV扩大了10000倍。

![RV.png](Image/feature_plot/RV.png?t=1681550084826)

![RSkew.png](Image/feature_plot/RSkew.png?t=1681550116888)

![Rkurtosis.png](Image/feature_plot/Rkurtosis.png?t=1681550165241)

2. 因子分位数时间序列图

![RVpercentage.png](Image/feature_plot/RVpercentage.png?t=1681550281339)

![RSkew.png](Image/feature_plot/RSkew.png?t=1681550337793)

![Rkurtosispercentage.png](Image/feature_plot/Rkurtosispercentage.png?t=1681550406660)

## 研究结果

### 一、 分组alpha净值结果

在原研报因子的月频表现中，Rskew因子表现最好，但这里日频表现中Rkurtosis因子表现最好，RV和Rskew因子来选股时各组区分度不佳。并且不同的回归方法（ols和huber）对结果有一定的影响。

1. OLS

![RV_OLS_Log_TCap_Industry.png](Image/alpha_nav/RV_OLS_Log_TCap_Industry.png?t=1681550536254)

![RSkew_OLS_Log_TCap_Industry.png](Image/alpha_nav/RSkew_OLS_Log_TCap_Industry.png?t=1681550564361)

![Rkurtosis_OLS_Log_TCap_Industry.png](Image/alpha_nav/Rkurtosis_OLS_Log_TCap_Industry.png?t=1681550586720)

2. Huber

![RV_OLS_Log_TCap_Industry.png](Image/alpha_nav/RV_OLS_Log_TCap_Industry.png?t=1681550617916)

![RSkew_Huber_Log_TCap_Industry.png](Image/alpha_nav/RSkew_Huber_Log_TCap_Industry.png?t=1681550642824)

![Rkurtosis_Huber_Log_TCap_Industry.png](Image/alpha_nav/Rkurtosis_Huber_Log_TCap_Industry.png?t=1681550662960)

### 二、Rskurtosis指标IC和IR表现

IR为年化指标，IC为日度指标。


|                      | alpha\_IR | alpha\_IC\_mean | alpha\_IC\_std | alpha\_IC\_min | alpha\_IC\_max | alpha\_IC\_negative\_value\_ratio |
| -------------------- | --------- | --------------- | -------------- | -------------- | -------------- | --------------------------------- |
| 2016                 | -4.6590   | -0.0105         | 0.0357         | -0.1061        | 0.0926         | 0.6240                            |
| 2017                 | -5.9299   | -0.0146         | 0.0390         | -0.1260        | 0.0939         | 0.6352                            |
| 2018                 | -6.6872   | -0.0196         | 0.0465         | -0.1481        | 0.1035         | 0.6626                            |
| 2019                 | -6.4595   | -0.0165         | 0.0406         | -0.1198        | 0.1126         | 0.6639                            |
| 2020                 | -4.0226   | -0.0105         | 0.0415         | -0.1320        | 0.1337         | 0.6008                            |
| 2021                 | -3.4164   | -0.0070         | 0.0325         | -0.1098        | 0.0777         | 0.5844                            |
| 2022 till 2023-02-20 | -3.7772   | -0.0085         | 0.0356         | -0.1225        | 0.0851         | 0.5956                            |
