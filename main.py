import eel
import pandas as pd
import json
from bson.json_util import dumps # converts mongodb cursor into python suitable 
import glob
import os
from pymongo import MongoClient # pip install "pymongo[srv]"
from bson.objectid import ObjectId #mongodb objectid
from datetime import datetime
import csv
import numpy as np
import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import sys
import requests #pip install requests
from geopy.geocoders import Nominatim # pip install geopy
from MLModel import ML_Model
import chart_studio
import plotly.express as px
import chart_studio.plotly as py


db_object = None
machine_learning = None


def pd_to_json(df):
    """helper function, converts python dataframe to json-formatted string"""
    result = df.to_json(orient="index")
    parsed = json.loads(result)
    return parsed

def get_db():
    """helper function, returns the resale price table as an object to run operations (like querying) on"""
    global db_object
    if db_object is None:
        PATH = os.getcwd() + '\\data\\'
        CONNECTION_STR = ""
        with open(PATH + '/access_url.txt', 'r') as f:
            CONNECTION_STR = f.readline()
        print(CONNECTION_STR)
        initial_time = datetime.now()
        client = MongoClient(CONNECTION_STR)
        print(f"Connected to MongoDB client in {(datetime.now() - initial_time).total_seconds()}")
        db = client.test
        db_object = db["resale_prices"]

    return db_object


def get_csv_as_pd():
    """helper function, converts all data rows in all csv files in the "data" folder into a single python dataframe"""
    path = os.getcwd() + '\\data\\cleaned\\'
    print(f"CWD:{path}")
    csv_files = glob.glob(os.path.join(path, "*.csv"))
    df = pd.concat((pd.read_csv(f) for f in csv_files), ignore_index=True)
    return df


@eel.expose
def init_ml_model():
    """Sets the regression model into the global variable"""
    global machine_learning
    if not machine_learning:
        machine_learning = ML_Model()


@eel.expose
def get_predicted_value(input_list):
    global machine_learning
    # note: input_list must must be a list of dictionaries, with each dict representing each row
    df = pd.DataFrame([input_list])
    result = machine_learning.predict_values(df)
    print("The predicted value(s) is/are:")
    print(result)
    return result[0] # result comes out as list


@eel.expose
def get_prediction_graph(input_row, years_ahead):
    global machine_learning
    # note: input_list must must be a list of dictionaries, with each dict representing each row
    months_to_iterate = int(years_ahead) * 12
    e = input_row.copy()
    input_list = [e]
    date_val = input_row["month"].split("-")
    year_val = int(date_val[0])
    month_val = int(date_val[1])

    for i in range(months_to_iterate):
        
        if month_val >= 12:
            year_val += 1
            month_val = 1
        else:
            month_val += 1
        input_row["month"] = str(year_val) + "-" + str(month_val)
        temp_dict = input_row.copy()
        input_list.append(temp_dict)

    date_list = [e["month"] for e in input_list]
    print(f"Date list: {date_list}")
    df = pd.DataFrame(input_list)
    print(df.head(3))
    print(df.tail(3))
    result = machine_learning.predict_values(df)
    print("The predicted value(s) is/are:")
    print(result)
    prediction_graph_df = pd.DataFrame(
        {
            "date" : date_list,
            "predicted_price" : result
        })
    print(prediction_graph_df.head(2))
    print(prediction_graph_df.tail(2))
    print(len(prediction_graph_df.index))
    

    fig = px.line(prediction_graph_df, x='date', y='predicted_price')
    url = py.plot(fig, filename = 'prediction_graph', auto_open=False)
    print(url)
    return url
    # test result output
    # return result[0] # result comes out as list


@eel.expose
def get_dropdown_values(column_names = [], query_dict = {}):
    """retrieves all unique data from specified columns in the .csv file containing dataset"""
    output_dict = {}
    db = get_db()
    if len(column_names) > 0:  # checks if columns were added in the function args 
        initial_time = datetime.now()
        for key in column_names: # for every column name
            distinct_value_list = db.distinct(key, query_dict) # get all distinct values of each column name
            output_dict[key] = distinct_value_list # insert key name with distinct values in dict
        print(f"Done collating unique values in {(datetime.now() - initial_time).total_seconds()}")
        return output_dict
    else:
        # if no columns were specified, this function is useless
        print("No columns specified in function. Aborting....")
        return None
    # sample result: { flat_type: (7) […], town: (27) […], street_name: (579) […], flat_model: (21) […], month: (393) […] }
    # if len(column_names) > 0:

    #     if input_df == None:
    #         input_df = get_csv_as_pd()

    #     for name in column_names:
    #         if name in input_df.columns:
    #             output_dict[name] = list(input_df[name].unique())
    #         else:
    #             print(f"{name} is not a valid column.\n Column list:{input_df.columns}\n")
    #     return json.loads(json.dumps(output_dict, indent = 4))
    # else:
    #     print("No columns specified in function. Aborting....")
    #     return None
    
@eel.expose
def heatmap_plot():
    #this function is to plot the heatmap to predict the future price of flats based on type of flat and town area
    #below is just hardcoded example 
    vegetables = ["cucumber", "tomato", "lettuce", "asparagus",
              "potato", "wheat", "barley"]
    farmers = ["Farmer Joe", "Upland Bros.", "Smith Gardening",
           "Agrifun", "Organiculture", "BioGoods Ltd.", "Cornylee Corp."]

    harvest = np.array([[0.8, 2.4, 2.5, 3.9, 0.0, 4.0, 0.0],
                    [2.4, 0.0, 4.0, 1.0, 2.7, 0.0, 0.0],
                    [1.1, 2.4, 0.8, 4.3, 1.9, 4.4, 0.0],
                    [0.6, 0.0, 0.3, 0.0, 3.1, 0.0, 0.0],
                    [0.7, 1.7, 0.6, 2.6, 2.2, 6.2, 0.0],
                    [1.3, 1.2, 0.0, 0.0, 0.0, 3.2, 5.1],
                    [0.1, 2.0, 0.0, 1.4, 0.0, 1.9, 6.3]])


    fig, ax = plt.subplots()
    im = ax.imshow(harvest)

    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(len(farmers)), labels=farmers)
    ax.set_yticks(np.arange(len(vegetables)), labels=vegetables)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
         rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(vegetables)):
        for j in range(len(farmers)):
            text = ax.text(j, i, harvest[i, j],
                       ha="center", va="center", color="w")

    ax.set_title("Harvest of local farmers (in tons/year)")
    fig.tight_layout()
    fig.savefig('web/resources/heatmap3.jpg')
    #plt.show()
    # return savedfig
    


@eel.expose
def query_db(search_query_dict, result_limit = 2000):
    DATE_COLUMN_NAME = "month"
    data_table = get_db()
    
    # If we are getting everything, query dict should be an empty dict {}
    # sample query appearance:

    # "$and" : [{
    #                 "center_id" : { "$eq" : 11}
    #             },
    #             {
    #                 "meal_id" : { "$ne" : 1778}
    #             }]
    initial_time = datetime.now()
    if search_query_dict:  
        # if a query dict is specified, the code here runs to filter results
        query_list = []
        # search_query_dict format is { column_name : {"search_type": "...", "value": "..."} }
        for key,value in search_query_dict.items():  # for each *column to search* : *search value*
            search_value = value["value"]
            if search_value and "month_" in key: 
                # special condition, if user is trying to set a date filter range
                # column name value will either be month_earliest or month_latest
                if key == "month_earliest":
                    query_list.append({DATE_COLUMN_NAME: {"$gte": search_value}})
                if key == "month_latest":
                    query_list.append({DATE_COLUMN_NAME: {"$lte": search_value}})
                
            elif search_value:
                if value["search_type"] == "match_text":
                    # must match value. Acceptable to use here, since dropdowns take values from the data itself
                    query_list.append({key: {"$eq": search_value}}) 
                else:
                    # as a catch-all, if i do not specify the search_type value
                    query_list.append({key: {"$regex" : f".*{search_value}.*"}}) # search if string contains, case insensitive

        # search_query_dict = {})
        print(query_list)
        cursor = data_table.find({"$and" : query_list}, limit=result_limit).sort("month", -1)
        # exclude _id column, sort by month descending
    else:
        # else, get everything, limit results via result_limit
        cursor = data_table.find({}, limit=result_limit).sort("month", -1)
    print(f"Query done in {(datetime.now() - initial_time).total_seconds()}")
    initial_time = datetime.now()
    result = json.loads(dumps(cursor))
    print(f"JSON conversion done in {(datetime.now() - initial_time).total_seconds()}")

    return result
    
    # 2000
@eel.expose
def csvFormat(data): 

    PATH = os.getcwd() + '\\web\\resources\\'
    key = data[0].keys()
    
    with open(PATH + 'queryData.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, key)
        writer.writeheader()
        writer.writerows(data)
        

# @eel.expose
# def query_csv(search_query_dict = None, max_rows = 2000):
#     """retrieves data from .csv file containing dataset. returns data as JSON to allow the Javascript code to handle the data as an object"""
#     df = get_csv_as_pd()

#     if search_query_dict: # if there is a JSON object added into the parameters
#         # https://www.geeksforgeeks.org/python-filtering-data-with-pandas-query-method/ for multiple query method
        
#         print(search_query_dict)
#         # conditions = []
#         for key,value in search_query_dict.items():
#             # conditions.append(df[key].str.contains(value))

#             if value and "month_" in key: # special condition, if user is trying to set a date filter range
#                 if key == "month_earliest":
#                     df = df[df["month"] >= value]
#                 if key == "month_latest":
#                     df = df[df["month"] <= value]
#                 print(f"Filtered. Nuber of rows: {len(df.index)}")

#             elif value and key in df.columns: # if value is not empty, and if column name exists in dataframe
#                 print(key)
#                 print(value)
#                 df = df[df[key].astype(str).str.contains(value)]
#                 print(f"Filtered. Nuber of rows: {len(df.index)}")

            
        
#         # sample search_query_json = {
#         #     "month": "",
#         #     "town": "",
#         #     "flat_type": "",
#         #     "street_name": "",
#         #     "storey_range": "",
#         #     "floor_area_sqm": "",
#         #     "flat_model": "",
#         #     "lease_commencement_date": "",
#         #     "resale_price": "",
#         #     "remaining_lease": ""
#         # }
    
#     print(df["month"].min())
#     print(df["month"].max())
#     df = df.iloc[:max_rows]  # determines max rows shown
    
#     return pd_to_json(df)

def getPostalCode(streetName, block):
    #initialize Nominatim API
    geolocator = Nominatim(user_agent="geoapiExercises")

    datatable = get_db()
    geolocator = Nominatim(user_agent="geoapiExercises")

    # datatable = get_db()
    place =str(309)+ "," + "ANG MO KIO AVE 1"
    location = geolocator.geocode(place)

    #traverse the data
    data = location.raw
    loc_data = data['display_name'].split(',')
    loc_data_new = []
    for i in loc_data:
        replaced = i.replace(' ','')
        loc_data_new.append(replaced)
    print(loc_data_new)
    print(loc_data_new[-2])
    return loc_data_new[-2]

#returns the id of the record when user click into it
@eel.expose
def getRecordId(month,town,flat_type,block,street_name,storey_range,floor_area_sqm,flat_model,lease_commence_date,resale_price,remaining_lease):
    data_table = get_db()
    record = data_table.find_one({"month":month, "town":town,"flat_type":flat_type,"block":block,"street_name":street_name,"storey_range":storey_range,"floor_area_sqm":floor_area_sqm,"flat_model":flat_model,"lease_commence_date":lease_commence_date,"resale_price":resale_price,"remaining_lease":remaining_lease})
    return record["_id"]

#get the record details by id
@eel.expose
def getRecordByRecordId(id):
    data_table = get_db()
    # cursor = data_table.find({'_id': id})
    # result = json.loads(dumps(cursor))
    # return result
    record = data_table.find_one({'_id': ObjectId(id) })
    return record

#display map
# @eel.expose
# def displayMap(postalcode):
#     response = requests.get("https://developers.onemap.sg/commonapi/staticmap/getStaticImage?layerchosen=default&postal="+postalcode+"&zoom=17&height=512&width=512")
#     return response

if __name__ == "__main__":
    
    eel.init('web', allowed_extensions=['.js', '.html'])
    # mode value depends on preferred browser. should find a way to implement our own browser check
    chart_studio.tools.set_credentials_file(username='tjl081', api_key='3aQmYk1TJQIdiao8Pqip')
    print("main.py running") 
    # Call a Javascript function. the results are queued then displayed the moment the webpage starts up
    eel.start('main.html', mode="chrome-app") # code seems to pause here while website is running.




# we constantly fetch data from the CSV with every user query. while this seems inefficient, it is the only way (i know) to get live data.
# also easier integration when converting to database access

