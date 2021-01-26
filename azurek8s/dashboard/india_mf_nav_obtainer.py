import requests
import pandas as pd
from typing import List
import json
import os
from datetime import datetime
import glob
from fuzzywuzzy import fuzz, process

STAGING_LOCATION = os.path.join(os.getcwd(), 'data')

if not os.path.exists(STAGING_LOCATION):
    os.makedirs(STAGING_LOCATION)

FUND_NAV_API = "https://api.mfapi.in/mf/{0}"
ALL_MUTUAL_FUNDS_API = "https://api.mfapi.in/mf"
STORED_FILE_PATTERN = "{0}*.pkl"

class IndiaMFNavObtainer:
    def __init__(self, force=False):
        self.funds_df = IndiaMFNavObtainer.get_all_fund_details()
    
    @staticmethod
    def _delete_files(file_locations: List[str]):
        for file_with_location in file_locations:
            print("Removing the file {0}".format(file_with_location))
            os.remove(file_with_location)

    @staticmethod
    def _get_latest_modified_file(file_locations: List[str]) -> pd.DataFrame:
        if len(file_locations) > 0:
            file_location_with_modified_time = [(file_location, os.path.getmtime(file_location)) for file_location in file_locations]
            file_location_with_modified_time.sort(key=lambda x: x[1], reverse=True)
            latest_file_location = file_location_with_modified_time[0][0]
            return pd.read_pickle(latest_file_location)

        return None

    @staticmethod
    def get_historical_nav_for_mf(mutual_fund_id: str) -> pd.DataFrame:
        today_date = datetime.today().strftime('%Y_%m_%d')
        file_name = mutual_fund_id + "_" + today_date + ".pkl"
        existing_file_pattern = STORED_FILE_PATTERN.format(mutual_fund_id)
        existing_files_with_locations = glob.glob(STAGING_LOCATION + existing_file_pattern)
        existing_file_names = [os.path.basename(f) for f in existing_files_with_locations]
        should_delete_existing_files = False

        if len(existing_files_with_locations) > 0:
            # file exists for the current date already
            if file_name in existing_file_names:
                print("Found existing response data for date {0}".format(today_date))
                return pd.read_pickle(os.path.join(STAGING_LOCATION, file_name))
            # these are older files and can be removed
            else:
                should_delete_existing_files = True


        request_url = FUND_NAV_API.format(mutual_fund_id)
        print(request_url)
        
        try:
            response = requests.get(request_url)
            nav_df = None
            
            if response:
                json_data = json.loads(response.text)
                # print(json_data)
                nav_data = json_data.get("data")
                if nav_data is None or len(nav_data) == 0:
                    raise ValueError('No historical NAV data')
                nav_df = pd.DataFrame(nav_data)
                nav_df.to_pickle(os.path.join(STAGING_LOCATION, file_name))
                print("Saved the response as a pickle file")
                return nav_df
        except Exception as e:
            print("Error occurred. Details: " + str(e))
            should_delete_existing_files = False

        if should_delete_existing_files:
            IndiaMFNavObtainer._delete_files(existing_files_with_locations)

        # load the latest available dataframe - when the current request has errored!  
        return IndiaMFNavObtainer._get_latest_modified_file(existing_files_with_locations)

    @staticmethod
    def get_all_fund_details(force=False):
        request_url = ALL_MUTUAL_FUNDS_API
        print(request_url)

        try:
            response = requests.get(request_url)
            funds_df = None
            file_path = os.path.join(STAGING_LOCATION, 'all_funds.pkl')
            if not force and os.path.exists(file_path):
                print('Reading from pickled file')
                return pd.read_pickle(file_path)
            
            if response:
                json_data = json.loads(response.text)
                print(json_data)
                funds_df = pd.DataFrame(json_data)
                funds_df.to_pickle(file_path)
                print("Saved the response as a pickle file")
                return funds_df
        except Exception as e:
            print("Error occurred. Details: " + str(e))

    def fuzzy_search_mf_by_name(self, search_text, limit=10):
        if not search_text:
            print('No search text')
            return

        results = process.extract(search_text.lower(), self.funds_df['schemeName'], scorer=fuzz.token_set_ratio, limit=limit)
        fuzzy_df = pd.DataFrame(results, columns=['matched_text', 'score', 'idx'])
        merged_df = pd.merge(fuzzy_df, self.funds_df['schemeCode'], left_on='idx', right_index=True)
        merged_df = merged_df.drop(columns='idx')
        return merged_df


