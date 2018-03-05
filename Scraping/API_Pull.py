import pandas as pd
import time

#######------Code to pull route data from mountain project API----#########
######-------Obtain your own API key on mountainproject.com--------########
#####------Be nice! MountainProject is a great service!------------######


# pulled route URLs using Collect_Route_URLs.ipynb
# this is a fairly manual process - see documents

routeurl_filename = 'yourfilenamehere'
df_url = pd.read_csv(routeurl_filename + '.csv')
id_list = df_url['id'].tolist()

#function to pull routes given input list
#input list defined below (only 100 routes per request, I did 100 at a time)
#append them to DF
def make_df(route_list):
    from collections import defaultdict
    import requests
    import json
    import pandas as pd
    
    df = None
    
    routes = ','.join([str(i) for i in route_list])
    
    key = 'Enter your API Key Here'

    url = 'https://www.mountainproject.com/data/get-routes?routeIds=' + routes + '&key=' + key
    
    r_dict = defaultdict(list)
    r = requests.get(url)
    data = r.json()
                
    for i in range(len(route_list)):
        try:
            r_dict['id'].append(data['routes'][i]['id'])
        except:
            r_dict['id'].append(0)

        try:    
            r_dict['latitude'].append(data['routes'][i]['latitude'])
        except:
            r_dict['latitude'].append(0)

        try:
            r_dict['longitude'].append(data['routes'][i]['longitude'])
        except:
            r_dict['longitude'].append(0)

        try:
            r_dict['name'].append(data['routes'][i]['name'])
        except:
            r_dict['name'].append(0)

        for j in range(10):
            try:
                r_dict['loc' + str(j)].append(data['routes'][i]['location'][j])
            except:
                r_dict['loc' + str(j)].append(0)
        try:
            r_dict['pitches'].append(data['routes'][i]['pitches'])
        except:
            r_dict['pitches'].append(0)

        try:
            r_dict['rating'].append(data['routes'][i]['rating'])
        except:
            r_dict['rating'].append(0)

        try:
            r_dict['starVotes'].append(data['routes'][i]['starVotes'])
        except:
            r_dict['starVotes'].append(0)

        try:
            r_dict['stars'].append(data['routes'][i]['stars'])
        except:
            r_dict['stars'].append(0)

        try:
            r_dict['type'].append(data['routes'][i]['type'])
        except:
            r_dict['type'].append(0)
        
    if df is None:
        df = pd.DataFrame.from_dict(r_dict)
    else:
        df2 = pd.DataFrame.from_dict(r_dict)
        df = pd.concat([df,df2])
        
    return(df)

df_out = None

#determine routes in list to pass to API (100/request)
#pull from API, add to dataframe
for i in range(int(len(id_list)/100)+1):
    list_start = i*100
    if ((i+1)*100) < len(id_list):
        list_end = ((i+1)*100)
    else:
        list_end = len(id_list)
    try_list = id_list[list_start:list_end]
    
    if df_out is None:
        df_out = make_df(try_list)
    else:
        df_a = make_df(try_list)
        df_out = pd.concat([df_out, df_a])
    print(i)
    time.sleep(1)

df_out.reset_index(inplace=True)

# ouput file
filename = 'yourfilename'

df_out.to_csv(filename + '.csv')

