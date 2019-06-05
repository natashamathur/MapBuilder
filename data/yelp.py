#!/usr/bin/env python3

"""
Authors: Kevin Sun
Date of Last Edit: 6.3.2019
"""

import os
import sys
import pandas as pd
from yelpapi import YelpAPI
from pprint import pprint

# filepaths
COORDINATES = 'socioeconomic.csv'
# set global variables
YELP_KEY = 'GsAgBiywduecH_D-DDeB-ctBkWbUnFP_6w_b0CG4utMCu3s9Z3XIrNuyJum_NJ-FuIIsljD_7KTrOaHuZZjos6v-5-o5GSzfSsAVwySWhmlV4vnlN9ElxCE0xOBrWnYx'
CHICAGO_LAT = 41.881832
CHICAGO_LONG = -87.623177

CATEGORIES = ['restaurants', 'food', 'health', 'transport']
LIMIT = 12
PRICE = "1,2"
SORT_BY = "distance"

def build_chicago_yelp_df(coordinates, categories_list, limit, sort_by, yelp_api_key):
    '''
    This function builds a dataframe of businesses by making 
    a separate call on the Yelp API for each Chicago Neighorhood. It 
    returns a single dataframe to be used in mapping.

    Inputs:
        - coordinates: a string filpath for the socioeconomic.csv file that
                        contains the lat & longt information for each
                        neighorhood
        - categories)
    '''
    # import coordinates
    ses = pd.read_csv(coordinates)
    # initialize list for dfs
    df_list = []
    for n in ses.iterrows():
        lat = n[1].latitude
        longt = n[1].longitude
        cam = n[1]['COMMUNITY AREA NAME']
        
        df = get_yelp_df(categories_list, lat, longt, limit, sort_by, yelp_api_key)
        df_list.append(df)

    # append each neighorhood's df together into one long df
    chicago_df = pd.concat(df_list)
    # drop duplicates based on phone number
    chicago_df.drop_duplicates(subset=['phone'], inplace=True)
    # write to csv
    chicago_df.to_csv("yelp.csv")

    return chicago_df


def get_yelp_df(categories_list, lat, longt, limit,
    sort_by, yelp_api_key):
    '''
    This function takes a given latitude and longitude and makes a
    call to the Yelp API to pull the top 50 closest restaurant,
    food, health, transport, and grocery businesses.

    Intputs:
        - categories_list: a list of strings of Yelp categories
                        above set as global variable)
        - lat: a float representing either a user's current location 
                latitude or their desired location latitude
        - long: a float representing either a user's current location
                longitude or their desired location longitude
        - limit: an integer of maximum number of Yelp results that
                    will be returned from the query
        - sort_by: string representing a user's sorting preference
                    (options are: distance, best_match, rating,
                    review_count)
        - yelp_api_key: a string of the Yelp API Key

    Outputs:
        - df_final: a pandas dataframe of concatenated Yelp business results
                    for the given latitude and longitude
    '''
    df_list = []
    for category in categories_list:
        df = extract_yelp_data(category, lat, longt, limit, sort_by, yelp_api_key)
        df_list.append(df)

    df_final = pd.concat(df_list)

    return df_final


def extract_yelp_data(categories, lat, longt, limit, 
                        sort_by, yelp_api_key):
    """
    This function takes search results (a dictionary) and obtains the 
    name, zip code, address of the possible business matches in the
    form of a pandas dataframe.

    Inputs:
        - categories: a string of type of business (pulled from list
                        above set as global variable)
        - lat: a float representing either a user's current location 
                latitude or their desired location latitude
        - long: a float representing either a user's current location
                longitude or their desired location longitude
        - limit: an integer of maximum number of Yelp results that
                    will be returned from the query
        - sort_by: string representing a user's sorting preference
                    (options are: distance, best_match, rating,
                    review_count)
        - yelp_api_key: a string of the Yelp API Key

    Outputs:
        - yelp_results: a pandas dataframe the name, phone, lat, long,
                        additional_info, and type of each business
    """
    yelp_api = YelpAPI(yelp_api_key)
    if categories == "restaurants":
        # use separate query for restaurants to filter out $$$ and $$$$
        search_results = yelp_api.search_query(categories=categories,
                                               price=PRICE,
                                               latitude=lat,
                                               longitude=longt,
                                               limit=limit,
                                               sort_by=sort_by)
    else:
        search_results = yelp_api.search_query(categories=categories,
                                               latitude=lat,
                                               longitude=longt,
                                               limit=limit,
                                               sort_by=sort_by)

    # If Yelp query returns nothing, return None
    if not search_results:
        return None

    # Initialize lists for each planned column in Yelp results dataframe;
    # these are characteristics of each business that get returned to user
    names = []
    latitudes = []
    longitudes = []
    phones = []
    ratings = []
    addresses = []
    urls = []
    
    # obtain business information
    businesses = search_results['businesses']
    for i in businesses:
        # In case a Yelp business is missing a field:
        try:
            a_name = i['name']
            a_latitude = i['coordinates']['latitude']
            a_longitude = i['coordinates']['longitude']
            a_phone = i['phone']
            a_rating = i['rating']
            a_review_count = i['review_count']
            a_address = i['location']['address1']
            a_url = i['url']

            if a_phone not in phones: # exclude duplicates
                if all([a_name != "", a_phone != "", 
                        a_rating != "", a_review_count != "",
                        a_address != "",
                        a_url != ""]) & (a_latitude is not None) & (a_longitude is not None):
                    names.append(a_name)
                    latitudes.append(a_latitude)
                    longitudes.append(a_longitude)
                    phones.append(a_phone)
                    addresses.append(a_address)
                    urls.append(a_url)
                    # get ratings and review counts string
                    rate_str = "Yelp Rating: " + str(a_rating) + " Reviews: " + str(a_review_count)
                    ratings.append(rate_str)


        except KeyError:
            print("Key Error, some missing field from the Yelp return!")

    # cast Yelp results lists into pandas dataframe
    yelp_results = pd.DataFrame()
    yelp_results['name'] = names
    yelp_results['phone'] = phones
    yelp_results['latitude'] = latitudes
    yelp_results['longitude'] = longitudes
    yelp_results['addtional_info'] = ratings
    yelp_results['type'] = categories
    yelp_results['address'] = addresses
    yelp_results['url'] = urls


    return yelp_results
