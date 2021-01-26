import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from dashboard.india_mf_nav_obtainer import IndiaMFNavObtainer
import seaborn as sns
from typing import List
from datetime import datetime, timedelta, date
from sklearn.preprocessing import MinMaxScaler, PolynomialFeatures
from sklearn.linear_model import ElasticNet
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import RandomizedSearchCV
import scipy.stats as stats
from time import time
import joblib

MODELS_LOCATION = os.path.join(os.getcwd(), 'Models')

if not os.path.exists(MODELS_LOCATION):
    os.makedirs(MODELS_LOCATION)


class FutureValuePrediction:

    def __init__(self, fund_id, fund_name, fund_df, start_year, force_retrain=False):
        self.start_year = start_year
        self.fund_df = FutureValuePrediction.transform_mutual_fund_df(fund_df)
        self.fund_id = fund_id
        self.fund_name = fund_name
        self.force_retrain = force_retrain

    @staticmethod
    def get_week_for_date(required_date):
        """
            month: Start from 1 and till 12
        """
        year = required_date.year
        month = required_date.month
        day = required_date.day
        days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        # Adjust for leap year
        if year % 4 == 0:
            days_per_month[1] = 29
        
        # slice till the month (it starts from 1)
        total_days_ytd = sum(days_per_month[:(month - 1)]) + day
        week = total_days_ytd // 7
        return week

    @staticmethod
    def transform_mutual_fund_df(fund_df):
        if not fund_df.empty:
            print(fund_df.head(20))
            fund_df["date"] = pd.to_datetime(fund_df["date"], format='%d-%m-%Y')
            fund_df["nav"] = fund_df["nav"].astype(float)
            fund_df.set_index('date', inplace=True)
            fund_df["Year"] = fund_df.index.year
            fund_df["Week"] = fund_df.index.map(FutureValuePrediction.get_week_for_date)
            return fund_df

    def _get_train_test_data_for_fund(self, fund_df, test_ratio = 0.2):
        fund_df = fund_df[fund_df["Year"] >= self.start_year]
        fund_df = fund_df.groupby(["Year", "Week"])["nav"].mean().reset_index()
        fund_df["X"] = fund_df.apply(lambda x: (x["Year"] - self.start_year)*52 + x["Week"], axis=1)
        fund_df = fund_df.drop(columns=["Year", "Week"])
        print(fund_df.head())
        
        X = fund_df["X"].values
        X = X.reshape(-1, 1)
        y = fund_df["nav"].values
        

        total_samples = X.shape[0]
        num_train_samples = int((1-test_ratio) * total_samples)

        X_train = X[:num_train_samples]
        y_train = y[:num_train_samples]

        X_test = X[num_train_samples + 1:]
        y_test = y[num_train_samples + 1:]
        
        print("Train shapes")
        print(X_train.shape)
        print(y_train.shape)
        
        print("Test shapes")
        print(X_test.shape)
        print(y_test.shape)
        
        return X, y, X_train, y_train, X_test, y_test

    def _train_model_for_fund(self, fund_id, fund_name, fund_df, force_retrain = False):
        
        X, y, X_train, y_train, X_test, y_test = self._get_train_test_data_for_fund(fund_df)
        
        model_location = os.path.join(MODELS_LOCATION, f'best_nav_estimator_{fund_id}_{self.start_year}.joblib')
        
        if not force_retrain and os.path.exists(model_location):
            print('Model already exists hence loading it.')
            fund_best_estimator = joblib.load(model_location)
        else:
            print('Model does not exist or force retrain, hence performing training')
            fund_regr = ElasticNet(random_state=0)
            param_dist = {
                            'l1_ratio': stats.uniform(0, 1),
                            'alpha': stats.uniform(0, 1)
                        }

            # run randomized search
            n_iter_search = 5
            random_search = RandomizedSearchCV(fund_regr, param_distributions=param_dist,
                                            n_iter=n_iter_search)

            start = time()
            random_search.fit(X_train, y_train)
            print("RandomizedSearchCV took %.2f seconds for %d candidates"
                " parameter settings." % ((time() - start), n_iter_search))

        
            fund_best_estimator = random_search.best_estimator_
            score = fund_best_estimator.score(X_test, y_test)
            print(f'Estimator score: {score}')
            print(random_search.best_params_)
            joblib.dump(fund_best_estimator, model_location)

        y_test_predict = fund_best_estimator.predict(X_test)
        y_train_predict = fund_best_estimator.predict(X_train)

        plt.plot(X, y, label = "Actual Navs")
        plt.plot(X_test, y_test_predict, label = "Predicted NAVs for test data")
        plt.plot(X_train, y_train_predict, label='Predicted NAVs for train data')

        plt.xlabel('Weeks')
        # Set the y axis label of the current axis.
        plt.ylabel('Nav values')
        # Set a title of the current axes.
        plt.title('Actual and predicted Nav values for {0} fund'.format(fund_name))
        # show a legend on the plot
        plt.legend()

        # Display a figure.
        self._estimator_plot = plt

        return fund_best_estimator

    def get_future_val_for_investment(self, invested_total, future_date):
        estimator = self._train_model_for_fund(self.fund_id, self.fund_name, self.fund_df, self.force_retrain)
        
        #latest_date = self.fund_df.iloc[0]['date']
        latest_nav = self.fund_df.iloc[0]['nav']
        
        print('Latest NAV')
        print(latest_nav)
        
        total_units = invested_total / latest_nav
        
        if type(future_date) == str:
            future_date = datetime.strptime(future_date, '%Y-%m-%d')
        year = future_date.year
        week = FutureValuePrediction.get_week_for_date(future_date)
        
        x = (year - self.start_year)*52 + week
        print('Prediction X value')
        print(x)
        
        X = np.array([x]).reshape(-1, 1)
        print(X)
        print(X.shape)
        
        y = estimator.predict(X)
        print(y)
        print(y.shape)
        
        future_nav = y[0]
        
        future_val = total_units * future_nav
        return round(future_val, 2)

    def get_estimator_plot(self):
        return self._estimator_plot
    