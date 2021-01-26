import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List
from datetime import datetime, timedelta
import streamlit as st
import joblib

import dashboard.utils as utils
from dashboard.india_mf_nav_obtainer import IndiaMFNavObtainer
from dashboard.rolling_returns_obtainer import RollingReturnsObtainer
from dashboard.future_prediction import FutureValuePrediction

india_mf_nav_obtainer = IndiaMFNavObtainer()

st.title("Indian Mutual funds dashboard")

# Get the name of the mutual fund from the user
st.subheader("Mutual fund details")
fund_name = st.text_input('Mutual fund name')

# Show the results sorted by score
funds_df = india_mf_nav_obtainer.fuzzy_search_mf_by_name(fund_name)
st.dataframe(funds_df)


# Get Id of the mutual fund to find
fund_id = st.text_input('Scheme code for the fund (from above table)')
fund_df = india_mf_nav_obtainer.get_historical_nav_for_mf(fund_id)

# Show the NAV values since inception
if fund_df is not None:
    st.subheader('NAV values')
    fund_df_transformed = utils.transform_mutual_fund_df(fund_df)
    st.line_chart(fund_df_transformed['nav'])

    # Returns for 1, 3 and 5 years
    one_year_return = utils.get_annualized_returns_for_fund(fund_df, 1)
    three_year_return = utils.get_annualized_returns_for_fund(fund_df, 3)
    five_year_return = utils.get_annualized_returns_for_fund(fund_df, 5)

    st.text(f'Annualized 1 year return: {one_year_return}%. 3 year return: {three_year_return}% and 5 year return {five_year_return}%.')

    # Metrics - variance, SD, Min, max, average and median NAV values
    metrics = utils.get_nav_metrics(fund_df, 3)
    print(metrics)

    st.subheader('Rolling returns')
    rolling_returns_period = st.text_input('Period (years)')
    if rolling_returns_period:
        fund_df = india_mf_nav_obtainer.get_historical_nav_for_mf(fund_id)
        rolling_returns_obtainer = RollingReturnsObtainer(fund_df, int(rolling_returns_period))
        period_to_consider_months = 2
        fund_returns = rolling_returns_obtainer.get_rolling_annualized_returns(period_to_consider_in_years=(period_to_consider_months/12))
        st.text(f'Rolling annualized returns for {rolling_returns_period} years is {fund_returns}% when averaged over {period_to_consider_months} months.')

    st.subheader('Predicted returns on future date')
    future_date = st.date_input('Enter future date')
    start_year = st.text_input('Enter start year (YYYY)', value='2016')
    amount_to_invest = st.text_input('Enter amount to invest (Rs.)', value='10000')
    if future_date:
        fund_df = india_mf_nav_obtainer.get_historical_nav_for_mf(fund_id)
        future_value_predictor = FutureValuePrediction(fund_id, fund_name, fund_df, int(start_year))
        print('Future date')
        print(future_date)
        amount_to_invest = float(amount_to_invest)
        future_val = future_value_predictor.get_future_val_for_investment(amount_to_invest, future_date)
        st.pyplot(future_value_predictor.get_estimator_plot())
        future_return = utils.get_return_percent_future_val(future_val, amount_to_invest)
        st.text(f'The return will be {future_val} which is {future_return}% for {fund_name} on {future_date}')
