import pandas as pd
from datetime import datetime, timedelta, date

def transform_mutual_fund_df(fund_df):
    if fund_df is None or fund_df.empty:
        return

    print(fund_df.head(20))
    fund_df["date"] = pd.to_datetime(fund_df["date"], format='%d-%m-%Y')
    fund_df["nav"] = fund_df["nav"].astype(float)
    fund_df.set_index('date', inplace=True)
    print(fund_df.head(20))
    return fund_df

def filter_fund_df_by_date(fund_df, years):
    total_days = int(years * 365)
    today = datetime.today()
    x_days_early = timedelta(total_days)
    since_date = today - x_days_early
    fund_df = fund_df[fund_df.index >= since_date]
    print('Dataframe after filter by date')
    print(fund_df.head())
    print(fund_df.tail())
    return fund_df


def get_annualized_returns_for_fund(fund_df, years):
    
    fund_df = filter_fund_df_by_date(fund_df, years)
    current_nav = fund_df.iloc[0]['nav']
    earliest_nav = fund_df.iloc[-1]['nav']
    
    print('Current NAV')
    print(current_nav)
    print('Earliest NAV')
    print(earliest_nav)
    
    # Formula
    # https://www.investopedia.com/terms/a/annualized-total-return.asp#:~:text=Key%20Takeaways-,An%20annualized%20total%20return%20is%20the%20geometric%20average%20amount%20of,the%20annual%20return%20was%20compounded.
    cumulative_return = (current_nav - earliest_nav) / earliest_nav
    total_days = int(years * 365)
    annualized_return = (1 + cumulative_return)**(365/total_days) - 1
    return round(annualized_return * 100, 2)

def get_nav_metrics(fund_df, years):
    fund_df = filter_fund_df_by_date(fund_df, years)
    metrics = {}
    metrics['mean'] = round(fund_df['nav'].mean(),2)
    metrics['max'] = round(fund_df['nav'].max(), 2) 
    metrics['min'] = round(fund_df['nav'].min(), 2)
    metrics['var'] = round(fund_df['nav'].var(), 2)
    metrics['standard deviation'] = round(fund_df['nav'].std(), 2)
    metrics['median'] = round(fund_df['nav'].median())
    return metrics

def get_return_percent_future_val(future_val, invested_total):
    diff = (future_val - invested_total)
    return round((diff / invested_total) * 100, 2)