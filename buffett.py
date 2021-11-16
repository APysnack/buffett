import os
from os import listdir, path
from os.path import isfile, join
import sys
import yfinance as yf
import tensorflow as tf
from tensorflow import keras
import numpy as np
import torch
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import mplfinance as mpf
import csv
from sklearn.model_selection import train_test_split
from utils.utils import *
from extra.definitions import *
from extra.individual import individualReport


# only used for testing/debugging: random list of tickers that have records for 2017, 2018, and 2019
truncated_tickers = ['UVSP', 'TCBK', 'ITCI', 'CENTA', 'CZR', 'EMN', 'KTCC', 'TREX', 'DPZ', 'TRMB', 'AEY', 'IO', 'ONVO', 'UNB', 'ASTC', 'SYN', 'CHGG', 'ZDGE', 'KDMN', 'PACW', 'ENPH', 'YUM', 'BBGI', 'INSG', 'ABIO', 'SNBR', 'PGRE', 'ZYXI', 'MBI', 'SNOA', 'SCVL', 'RCKT', 'BMRN', 'LKFN', 'IT', 'VKTX', 'PCRX', 'SNPS', 'ISRG', 'CMI', 'WMK', 'SMBC', 'GILD', 'IBTX', 'IBOC', 'MICT', 'LIND', 'SLG', 'GTN', 'BLD', 'CASI', 'DBD', 'CSU', 'APAM', 'PGTI', 'BAH', 'TUP', 'EFX', 'HSII', 'NCR', 'G', 'RDN', 'CIDM', 'ASTE', 'MCFT', 'RYN', 'SCL', 'OPTT', 'OFG',
                     'OFC', 'PBHC', 'SBNY', 'EXTN', 'OFLX', 'SELB', 'GROW', 'SUP', 'KAR', 'PHIO', 'RBB', 'ASIX', 'BUSE', 'JELD', 'LBAI', 'XENT', 'HROW', 'TBPH', 'APRN', 'SCYX', 'OGE', 'LRCX', 'BAND', 'CIA', 'HMHC', 'RPT', 'BHLB', 'SNAP', 'WM', 'SGRY', 'IDT', 'NEE', 'SHAK', 'GWB', 'ED', 'MTOR', 'ACLS', 'CHTR', 'POR', 'PPG', 'CATC', 'UFCS', 'TJX', 'GBL', 'CNXN', 'ILMN', 'NSC', 'PCYO', 'IP', 'CYCC', 'APT', 'IQV', 'R', 'PDEX', 'PPL', 'BFIN', 'WVVI', 'CTG', 'SEB', 'DE', 'PK', 'BDX', 'PLSE', 'WRB', 'IHC', 'INGN', 'WHR', 'POWL', 'PANL', 'SAFT', 'AMNB', 'OCC']


def get_ticker_list():
    tickers = []
    files = [x for x in listdir(TEST2017) if isfile(join(TEST2017, x))]
    tickers_2017 = [os.path.splitext(x)[0] for x in files]

    files = [x for x in listdir(TEST2018) if isfile(join(TEST2018, x))]
    tickers_2018 = [os.path.splitext(x)[0] for x in files]

    files = [x for x in listdir(TEST2019) if isfile(join(TEST2019, x))]
    tickers_2019 = [os.path.splitext(x)[0] for x in files]

    for ticker in tickers_2019:
        if (ticker in tickers_2018):
            if (ticker in tickers_2017):
                tickers.append(ticker)

    return tickers


def initialize_stocks(path, prev_path, prev_s_date, prev_e_date, first_iter, tickers):
    good_tickers = []
    for ticker in tickers:
        print("Working on: ", ticker)
        prev_df = get_df_from_csv(prev_path, ticker)
        stock_df = get_df_from_csv(path, ticker)
        s_date1, e_date1 = format_date_str(prev_s_date, prev_e_date)
        beginning, end = get_valid_dates(prev_df, s_date1, e_date1)
        roi = get_roi_between_dates(prev_df, beginning, end)
        if(first_iter is False or roi > 0):
            if(first_iter is True):
                good_tickers.append(ticker)
            mean = get_mean_between_dates(prev_df, beginning, end)
            std = get_std_between_dates(prev_df, beginning, end)
            cov = get_cov_between_dates(prev_df, beginning, end)
            add_col_to_df(stock_df, path,
                          f'{ticker}_appended', 'prev_year_roi', roi)
            add_col_to_df(stock_df, path,
                          f'{ticker}_appended', 'prev_year_mean', mean)
            add_col_to_df(stock_df, path,
                          f'{ticker}_appended', 'prev_year_std', std)
            add_col_to_df(stock_df, path,
                          f'{ticker}_appended', 'prev_year_cov', cov)
            add_daily_return_to_df(
                stock_df, path, f'{ticker}_appended', '1d_return', -1)
            add_daily_return_to_df(
                stock_df, path, f'{ticker}_appended', '2d_return', -2)
            add_daily_return_to_df(
                stock_df, path, f'{ticker}_appended', '3d_return', -3)
            add_z_score_to_df(stock_df, path, f'{ticker}_appended')
            add_prev_z_to_df(stock_df, path, f'{ticker}_appended',
                             'yesterday_z', 'z_score', 1)
            add_prev_z_to_df(stock_df, path, f'{ticker}_appended',
                             '2_days_back_z', 'z_score', 2)
            add_prev_z_to_df(stock_df, path, f'{ticker}_appended',
                             '3_days_back_z', 'z_score', 3)
            add_momentum_to_df(stock_df, path, f'{ticker}_appended')
            delete_unnamed_cols(stock_df)
            save_df_to_csv(stock_df, path, f'{ticker}_appended')
    return good_tickers


def download_stocks_to_csv():
    # DOWNLOAD STOCKS FROM YAHOO - NEED TO CONTINUE FROM 500 for 2015
    tickers = get_column_from_csv(FPATH + "Wilshire-5000-Stocks.csv", "Ticker")
    folder = PATH2016
    for i in range(1, 3481):
        save_to_csv_from_yahoo(
            folder, tickers[i], S_YEAR0, S_MONTH0, S_DAY0, E_YEAR0, E_MONTH0, E_DAY0)


def preprocess_data(path_to_data, tickers):
    b_threshold = 0.04

    for ticker in tickers:
        df = get_df_from_csv(path_to_data, f'{ticker}_appended')
        df = delete_unnamed_cols(df)
        df.drop(df.columns[[0, 1, 2, 3, 4, 5, 6, 8, 9, 15, 16, 17]],
                axis=1, inplace=True)

        classArray = []

        for i, value in enumerate(df['1d_return']):
            if(value > b_threshold or df['2d_return'][i] > b_threshold or df['3d_return'][i] > b_threshold):
                classArray.append('\'buy\'')
            else:
                classArray.append('\'dbuy\'')
        df['classification'] = classArray
        df.drop(df.columns[[2, 3, 4]], axis=1, inplace=True)
        df.drop(labels=[0, 1, 2], axis=0, inplace=True)
        save_df_to_csv_without_index(
            df, path_to_data, f'{ticker}_preprocessed')


def compile_data(path_to_data, fname, tickers):
    small_dfs = []
    for ticker in tickers:
        df = get_df_from_csv(path_to_data, f'{ticker}_preprocessed')
        df = delete_unnamed_cols(df)
        small_dfs.append(df)

    market_df = pd.concat(small_dfs, ignore_index=True)
    save_df_to_csv_without_index(market_df, path_to_data, fname)


def get_data_for_model(path_to_file):
    with open(path_to_file) as f:
        reader = csv.reader(f)
        next(reader)

        data = []
        for row in reader:
            data.append({
                "evidence": [float(cell) for cell in row[:6]],
                "label": 1 if row[6] == "\'buy\'" else 0
            })

    out_data = [row["evidence"] for row in data]
    out_labels = [row["label"] for row in data]
    return out_data, out_labels


if __name__ == "__main__":
    val = int(input(
        "What would you like to do?\n1. Individual Report\n2. Generate Neural Network Model from Stock Data\n"))
    if (val == 1 or val == 2):
        if(val == 1):
            individualReport()
        else:
            all_tickers = get_ticker_list()
            # download_stocks_to_csv()
            # initializes stock data and adds necessary cols for 2018 to ready for preprocessing
            good_tickers = initialize_stocks(
                PATHYEAR2, PATHYEAR1, S_DATE_STR1, E_DATE_STR1, True, all_tickers)

            # initializes stock data and adds necessary cols for 2019 to ready for preprocessing
            initialize_stocks(PATHYEAR3, PATHYEAR2, S_DATE_STR2,
                              E_DATE_STR2, False, good_tickers)

            # filters out unnecessary columns and retains values to be used for training/testing
            preprocess_data(PATHYEAR2, good_tickers)
            preprocess_data(PATHYEAR3, good_tickers)

            compile_data(PATHYEAR2, 'market_2018', good_tickers)
            compile_data(PATHYEAR3, 'market_2019', good_tickers)

            path_to_file = f'{PATHYEAR2}\\market_2018.csv'
            training_data_2018, training_labels_2018 = get_data_for_model(
                path_to_file)
            path_to_file = f'{PATHYEAR3}\\market_2019.csv'
            testing_data_2019, testing_labels_2019 = get_data_for_model(
                path_to_file)

            model = tf.keras.models.Sequential()
            model.add(tf.keras.layers.Dense(
                16, input_shape=(6,), activation="relu"))
            model.add(tf.keras.layers.Dense(1, activation="sigmoid"))

            model.compile(optimizer="adam", loss="binary_crossentropy",
                          metrics=["TruePositives", "TrueNegatives", "FalsePositives", "FalseNegatives"])
            model.fit(training_data_2018, training_labels_2018, epochs=7)
            model.evaluate(testing_data_2019, testing_labels_2019, verbose=2)

            model.save('first_model.model')
            new_model = tf.keras.models.load_model('first_model.model')

            # csv_to_arff(f'C:\\Users\\purle\\Documents\\stocks\\test\\2018\\market_2018.csv',
            #             f'C:\\Users\\purle\\Documents\\stocks\\test\\2018\\market_2018.arff', '2018_Stock_Market')

            # csv_to_arff(f'C:\\Users\\purle\\Documents\\stocks\\test\\2019\\market_2019.csv',
            #             f'C:\\Users\\purle\\Documents\\stocks\\test\\2019\\market_2019.arff', '2019_Stock_Market')
    else:
        print("Error with input")
