import datetime
import pandas as pd
import numpy as np
import os
from tqdm import tqdm

def interact_feature_engineer(samples, data, customers, articles, uid, iid, time_col):
    date_ths = str(data[time_col].max())

    last_month = 30
    last_month_date = datetime.datetime.strptime(date_ths, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(days=last_month)
    data_lm = data[data[time_col] >= last_month_date]

    last_week = 7
    last_week_date = datetime.datetime.strptime(date_ths, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(days=last_week)
    data_lw = data[data[time_col] >= last_week_date]

    data_ = data[data[uid].isin(samples[uid].unique())]
    #     data_ = data[data[uid].isin(samples[uid].unique())].merge(articles, on=iid, how='left')

    cols = ['sales_channel_id']
    for col in tqdm(cols):
        tmp = data_.groupby([uid])[col].agg('count').reset_index()
        new_col = 'customer_{}_hist_cnt'.format(col)
        tmp.columns = [uid, new_col]
        samples = samples.merge(tmp, on=uid, how='left')

    # 上次购买候选物品距今时间
    tmp = data.groupby([uid, iid])[time_col].agg('max').reset_index()
    tmp['purchase_corr_article_max_time'] = (
                datetime.datetime.strptime(date_ths, '%Y-%m-%d %H:%M:%S') - tmp[time_col]).dt.days
    samples = samples.merge(tmp[[uid, iid, 'purchase_corr_article_max_time']],
                            on=[uid, iid], how='left')

    # 过去购买过该物品次数统计
    tmp = data.groupby([uid, iid])[time_col].agg('count').reset_index()
    tmp.columns = [uid, iid, 'purchase_corr_article_cnt']
    samples = samples.merge(tmp, on=[uid, iid], how='left')

    cols = ['count']

    # 过去三天购买过的物品次数统计
    last_3days = 3  # 30
    last_3days_date = datetime.datetime.strptime(date_ths, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(days=last_3days)
    tmp = data_lw[data_lw[time_col] >= last_3days_date].groupby([uid, iid])['price'].agg(
        cols).reset_index()
    new_col = ['customer_article_last_3days_{}'.format(col) for col in cols]
    tmp.columns = [uid, iid] + new_col
    samples = samples.merge(tmp, on=[uid, iid], how='left')

    # 过去两周购买过的物品次数统计
    last_2weeks = 14
    last_2weeks_date = datetime.datetime.strptime(date_ths, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(days=last_2weeks)
    tmp = data_lm[data_lm[time_col] >= last_2weeks_date].groupby([uid, iid])['price'].agg(
        cols).reset_index()
    new_col = ['customer_article_last_2weeks_{}'.format(col) for col in cols]
    tmp.columns = [uid, iid] + new_col
    samples = samples.merge(tmp, on=[uid, iid], how='left')

    # 过去一个月购买过的物品次数统计
    cols = ['count']
    tmp = data_lm.groupby([uid, iid])['price'].agg(cols).reset_index()
    new_col = ['customer_article_last_month_{}'.format(col) for col in cols]
    tmp.columns = [uid, iid] + new_col
    samples = samples.merge(tmp, on=[uid, iid], how='left')

    # 过去一周购买过的物品次数统计
    tmp = data_lw.groupby([uid, iid])['price'].agg(cols).reset_index()
    new_col = ['customer_article_last_week_{}'.format(col) for col in cols]
    tmp.columns = [uid, iid] + new_col
    samples = samples.merge(tmp, on=[uid, iid], how='left')

    # 过去一天购买过的物品次数统计
    tmp = data_lw[data_lw[time_col] == data_lw[time_col].max()].groupby([uid, iid])['price'].agg(
        cols).reset_index()
    new_col = ['customer_article_last_day_{}'.format(col) for col in cols]
    tmp.columns = [uid, iid] + new_col
    samples = samples.merge(tmp, on=[uid, iid], how='left')

    # 历史最近一次点击距今时间
    tmp = data_.groupby(uid)[time_col].agg('max').reset_index()
    tmp['latest_purchase_time_sub'] = (
                datetime.datetime.strptime(date_ths, '%Y-%m-%d %H:%M:%S') - tmp[time_col]).dt.days
    samples = samples.merge(tmp[[uid, 'latest_purchase_time_sub']], on=uid, how='left')

    del data_, tmp

    return samples
