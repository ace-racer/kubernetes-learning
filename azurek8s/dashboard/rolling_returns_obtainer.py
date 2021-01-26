import pandas as pd
from datetime import datetime, timedelta, date


class RollingReturnsObtainer:
    def __init__(self, funds_df, period_in_years):
        """
        The period would imply the date with which the current NAV will be compared
        """
        self.funds_df = funds_df
        self.period_in_years = period_in_years
        self.funds_df = RollingReturnsObtainer.transform_mutual_fund_df(self.funds_df)
        self.dates_with_navs_sorted = self._get_dates_with_navs()

    @staticmethod
    def transform_mutual_fund_df(fund_df):
        if fund_df is None or fund_df.empty:
            return

        print(fund_df.head(20))
        fund_df["date"] = pd.to_datetime(fund_df["date"], format='%d-%m-%Y')
        fund_df["nav"] = fund_df["nav"].astype(float)
        print(fund_df.head(20))
        return fund_df

    def get_closest_date_with_nav(self, current_date):
        low = 0
        high = len(self.dates_with_navs_sorted)
        
        while low < high:
            mid = (low + high) // 2
            
            if self.dates_with_navs_sorted[mid][0] == current_date:
                return self.dates_with_navs_sorted[mid][0], self.dates_with_navs_sorted[mid][1]
            elif self.dates_with_navs_sorted[mid][0] < current_date:
                low = mid + 1
            else:
                high = mid - 1
                
        return self.dates_with_navs_sorted[mid][0], self.dates_with_navs_sorted[mid][1]

    def get_windowed_nav(self, current_date):
        total_days = int(self.period_in_years * 365)
        x_days_early = timedelta(total_days)
        
        if type(current_date) == str:
            current_date = datetime.strptime(current_date, '%Y-%m-%d')
        
        window_date = current_date - x_days_early
        #print(window_date)
        past_date, past_nav = self.get_closest_date_with_nav(window_date)
        return past_date, past_nav    

    def _get_dates_with_navs(self):
        dates_with_navs = self.funds_df.values
        dates_with_navs_sorted = sorted(dates_with_navs, key=lambda x: x[0])
        print('Dates with NAVs sorted by dates')
        print(dates_with_navs_sorted[:20])
        return dates_with_navs_sorted

    @staticmethod
    def _get_annualized_return_helper(current_nav, previous_nav, years):
        cumulative_return = (current_nav - previous_nav) / previous_nav
        total_days = int(years * 365)
        annualized_return = (1 + cumulative_return)**(365/total_days) - 1
        return round(annualized_return * 100, 2)

    def get_annualized_return(self, row):
        current_nav = row['nav']
        previous_nav = row['Prev Nav']
        years = self.period_in_years
        return RollingReturnsObtainer._get_annualized_return_helper(current_nav, previous_nav, years)

    def get_rolling_annualized_returns(self, period_to_consider_in_years = 1):
        old_returns_series = self.funds_df['date'].apply(self.get_windowed_nav)
        # print(old_returns_series.head(20))

        columns = ('Prev date', 'Prev Nav')
        old_returns_df = pd.DataFrame([[a, b] for a,b in old_returns_series.values ], columns=columns)

        combined_df = pd.concat([self.funds_df, old_returns_df], sort=False, axis=1)
        # print(combined_df.head(20))

        combined_df['Annualized Return'] = combined_df.apply(self.get_annualized_return, axis=1)

        print(combined_df.head(20))
        print(combined_df.tail(20))

        total_days = int(period_to_consider_in_years * 365)
        x_days_early = timedelta(total_days)
        today = datetime.today()

        window_date = today - x_days_early
        returns_df = combined_df[combined_df['date'] >= window_date]
        print('Combined DF after filtering')
        print(returns_df.head(20))
        print(returns_df.tail(20))

        return round(returns_df['Annualized Return'].mean(), 2)



