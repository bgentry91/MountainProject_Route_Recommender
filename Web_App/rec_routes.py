import pandas as pd
import numpy as np
import pickle
import requests
import json
import csv
import flask


########----Python script for flask BE for recommender project---------------------------------#######
#####-------Use recommender.html for frontend--------------------------------------------------######
######-------See comments and structure documentation on final presentation for more info!!-----####
####---------Lots of speed opportunties here... TODO!------------------------------------------#####



#function to utilize selenium & darrinward.com to build mapping based on route coordinates
#shows TSP shortest path between routes
#output as an iframe in HTML
def get_url(coord_list):
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    import re

    CHROME_PATH = '/Applications/Google Chrome.app'
    CHROMEDRIVER_PATH = '/Applications/chromedriver'

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("headless")  

    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options) 

    driver.get("https://www.darrinward.com/lat-long/")

    cord_input = driver.find_element_by_id("geos")
    cord_input.clear()
    for coord in coord_list:
            cord_input.send_keys(str(coord[0]) + "," + str(coord[1]))
            cord_input.send_keys(Keys.RETURN)

    cord_enter = driver.find_element_by_class_name("submit-button")
    cord_enter.send_keys(Keys.RETURN)

    url = driver.current_url

    driver.close()
    
    import re

    out = re.search(r'\?id=(.*?)\&', url).group(1)
    return out

#function to build recommendations based on user inputs/filters
def get_recommendations(email, min_diff, max_diff, stars, route_type, radius, rpd, locA, locB, locC, locD):

	#importing required pickle files (maybe we can get away with just doing this once for speed, instead of every call?)
	with open("full_dataset.pkl", 'rb') as picklefile: 
	    df = pickle.load(picklefile)

	with open('probability_matrix_10000_50.pkl', 'rb') as picklefile:
	    df_sent_pb = pickle.load(picklefile)

	with open('user_prefs.pkl', 'rb') as picklefile:
	    df_up = pickle.load(picklefile)

	#getting user route histories
	#get API key from mountainproject.com
	def get_ticks(email = None, userId = None):
	    
	    if email is None and userId is None:
	        print('Error - nothing passed')
	        return []

	    key = 'your_api_key_goes_here.com'
	    if email is not None:
	        if userId is not None:
	            print('Input UserID OR Email')
	            return []
	        else:
	            url = 'https://www.mountainproject.com/data/get-ticks?email=' + email + '&key=' + key   
	    else:
	        url = 'https://www.mountainproject.com/data/get-ticks?userId=' + userId + '&key=' + key
	        
	    r = requests.get(url)

	    data = r.json()

	    start_list = []

	    for route in data['ticks']:
	        start_list.append(route['routeId'])
	    
	    return start_list

	#get user's route history
	#todo - allow userId entry as well
	start_list = get_ticks(email = email)

	#get initial restrictions from ticked routes/filters:
	df_tick = df[df['id'].isin(start_list)].copy()
	df_tick = df_tick[df_tick.rating != 0]
	if min_diff == "":
		min_rating = df_tick.rating.min()
	else:
		min_rating = min_diff
	if max_diff == "":
		max_rating = df_tick.rating.max()
	else:
		max_rating = max_diff
	if route_type == "Any":
		fav_type = ['Sport','Trad','TR']
	else:
		fav_type = []
		fav_type.append(route_type)
	min_stars = stars
	min_votes = 2
	day_routes = rpd

	#apply above filters for comparison routes
	#need different levels to facilitate tree structure
	#last line in each excludes routes the user has already completed
	if locA == "":
		test_list = df[(df.type.isin(fav_type)) &
		               (df.rating >= min_rating) &
		               (df.rating <= max_rating) & 
		               (df.stars >= min_stars) & 
		               (df.starVotes >= min_votes) & 
		               (-df['id'].isin(start_list))]['id'].tolist()
	elif locB == "":
		test_list = df[(df.loc0 == locA) &
                       (df.type.isin(fav_type))&
                       (df.rating >= min_rating) &
                       (df.rating <= max_rating) & 
                       (df.stars >= min_stars) & 
                       (df.starVotes >= min_votes) & 
                       (-df['id'].isin(start_list))]['id'].tolist()
	elif locC == "":
		test_list = df[(df.loc0 == locA) &
                       (df.loc1 == locB) &
                       (df.type.isin(fav_type)) &
                       (df.rating >= min_rating) &
                       (df.rating <= max_rating) & 
                       (df.stars >= min_stars) & 
                       (df.starVotes >= min_votes) & 
                       (-df['id'].isin(start_list))]['id'].tolist()

	elif locD == "":
		test_list = df[(df.loc0 == locA) &
                       (df.loc1 == locB) &
                       (df.loc2 == locC) &
                       (df.type.isin(fav_type)) &
                       (df.rating >= min_rating) &
                       (df.rating <= max_rating) & 
                       (df.stars >= min_stars) & 
                       (df.starVotes >= min_votes) & 
                       (-df['id'].isin(start_list))]['id'].tolist()
	else:
		test_list = df[(df.loc0 == locA) &
                       (df.loc1 == locB) &
                       (df.loc2 == locC) &
                       (df.loc3 == locD) &
                       (df.type.isin(fav_type)) &
                       (df.rating >= min_rating) &
                       (df.rating <= max_rating) & 
                       (df.stars >= min_stars) & 
                       (df.starVotes >= min_votes) & 
                       (-df['id'].isin(start_list))]['id'].tolist()


	#get potential route probabilities from matrix
	test_probs = df_sent_pb[df_sent_pb.index.isin(test_list)]


	#calculating consine distances on entire tick list
	from sklearn.metrics.pairwise import cosine_similarity

	df_out = None

	#iterate through ticked routes and get similarties
	#still using sentences here - going to take the top 5 (mean_num) similar sentences and mean them to get similarity
	#this helps deal with descriptions of varying lengths
	for tick in start_list:
	    route_probs = df_sent_pb[df_sent_pb.index == tick]
	    if len(route_probs) !=0:
	        df_abc = pd.DataFrame(cosine_similarity(test_probs, route_probs), columns = [route_probs.index])
	        df_abc.index = test_probs.index
	        df_abc['max_sent'] = df_abc.max(axis=1)
	        
	        mean_num = 5

	        df_abc.columns = df_abc.columns.get_level_values(0)
	        df_abc['id'] =df_abc.index
	        df_abc.sort_values(['id','max_sent'], ascending=False, inplace=True)
	        df_abc = df_abc.groupby(df_abc.index).head(mean_num)
	        df_bcd = pd.DataFrame(df_abc.groupby(df_abc.index).max_sent.sum())
	        df_bcd['max_sent'] = df_bcd['max_sent']/mean_num

	        if df_out is None:
	            df_out = df_bcd
	            df_out.columns.values[0] = tick
	        else:
	            df_out[tick] = df_bcd.iloc[:,0]

	#calculating total ranking based on tick list
	df_out['total_sim'] = df_out.sum(axis=1)
	df_out.reset_index(inplace=True)
	df_out = df_out[['id','total_sim']]
	df_out = df_out.merge(df[['id','url','latitude','longitude']], on='id')
	df_out.sort_values('total_sim', ascending=False, inplace=True)
	df_out.reset_index(inplace=True, drop=True)
	df_out.reset_index(inplace=True)
	df_out.columns.values[0] = 'ranking'
	df_out['ranking'] = len(df_out) - df_out.ranking

	#get userID from email (thanks API!)
	#need this for extrinsic model
	def get_userId(email):
	    key = 'your_api_key_goes_here'
	    url = ('https://www.mountainproject.com/data/get-user?email='
	        + email + '&key=' + key)
	        
	    r = requests.get(url)

	    data = r.json()
	    userId = data['id']
	        
	    return userId

	#adjust ranking to account for missing values in extrinsic model
	def adj_ranking(value, shift, adjust):
	    if value == 0:
	        value == adjust
	    else:
	        value == value+shift
	    return value

	#calculating user preference for extrinsic model
	df_up = df_up[df_up.index.isin(test_list)]
	userId = get_userId(email)
	df_up = pd.DataFrame(df_up[str(userId)])
	df_up.sort_values(str(userId), inplace=True)
	df_up.reset_index(inplace=True)
	df_up.reset_index(inplace=True)
	del df_up[str(userId)]
	ranking_shift = len(df_out) - len(df_up)
	ranking_adjust = (len(df_out) - len(df_up))/2
	df_up.columns.values[0] = 'ranking_ext'
	df_up.columns.values[1] = 'routeid'

	#join two models, shift user preference ranking, create final ranking
	df_out = df_out.merge(df_up, how="left", left_on='id', right_on='routeid')
	del df_out['routeid']
	df_out['ranking_ext'].fillna(0, inplace=True)
	df_out['ranking_ext'] = df_out.apply(lambda x: adj_ranking(x['ranking_ext'], 
	                                                               ranking_shift, ranking_adjust),
	                                       axis=1)
	df_out['ranking'] = df_out.apply(lambda x: x['ranking'] + x['ranking_ext'], axis=1)
	del df_out['ranking_ext']
	df_out.sort_values('ranking', ascending=False, inplace=True)


	#calculating distance
	def haversine_np(lon1, lat1, lon2, lat2):

	    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

	    dlon = lon2 - lon1
	    dlat = lat2 - lat1

	    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

	    c = 2 * np.arcsin(np.sqrt(a))
	    mi = 3956 * c
	    return mi


	#calculating distance
	df_dist = df_out[['id','latitude','longitude']].copy()
	df_dist['tmp'] = 1
	df_dist = pd.merge(df_dist,df_dist,on='tmp')

	df_dist['dist'] = df_dist.apply(lambda row: haversine_np(row['longitude_x'], 
	                                            row['latitude_x'], 
	                                            row['longitude_y'], 
	                                            row['latitude_y']), axis=1)

	# check that distance is within radius, calculate score based on top # routes (day_routes)
	def calc_score(route, distance, day_routes):
	    df_near = df_dist[(df_dist.id_x == route) & (df_dist.dist <=distance)]
	    df_score = df_near.merge(df_out, left_on='id_y', right_on='id')
	    df_score.sort_values('ranking', ascending = False, inplace=True)
	    route_list = " ".join(str(x) for x in df_score.head(day_routes)['id'].tolist())
	    return ([df_score.head(day_routes).ranking.sum(), route_list])


	#for each route, calculate best potential list of routes based on what is within given radius
	df_out['score_report'] = df_out.apply(lambda x: calc_score(x['id'],radius, day_routes), axis=1)


	#cleanup
	df_out['day_score'] = df_out.apply(lambda x: x['score_report'][0], axis=1)
	df_out['route_list'] = df_out.apply(lambda x: x['score_report'][1], axis=1)
	del df_out['score_report']

	#create list of suggested routes for that day
	day_output = [int(i) for i in df_out.sort_values('day_score', ascending=False).head(1).route_list.tolist()[0].split()]


	#get lats and longs for calculating TSP
	df_day = df_out[df_out['id'].isin(day_output)]
	df_day = df_day[['id','latitude','longitude']].copy()


	#calc distances for TSP
	df_day['tmp'] = 1
	df_day = pd.merge(df_day,df_day,on='tmp')

	df_day['dist'] = df_day.apply(lambda row: haversine_np(row['longitude_x'], 
	                                            row['latitude_x'], 
	                                            row['longitude_y'], 
	                                            row['latitude_y']), axis=1)

	#create a NXN matrix of distances for TSP
	dist_array = []
	for loc in day_output:
	    dist_array.append(df_day[df_day.id_x == loc].dist.tolist())


	#Run TSP
	from tsp_solver.greedy import solve_tsp
	path = solve_tsp(dist_array)


	#order route list by shortest path
	sorted_day = [day_output[i] for i in path]
	#get lats and longs for each route by shortest path
	df_z = df[df['id'].isin(sorted_day)]
	df_z = df_z[['id','url','latitude','longitude','rating','name']]

	# Create the dictionary that defines the order for sorting
	sorterIndex = dict(zip(sorted_day,range(len(sorted_day))))

	# Generate a rank column that will be used to sort
	# the dataframe numerically
	df_z['order'] = df_z['id'].map(sorterIndex)
	df_z.sort_values('order', inplace=True)

	#get url path from selenium
	a = df_z['latitude'].tolist()
	b = df_z['longitude'].tolist()
	from itertools import zip_longest
	coord_list = (list(zip_longest(a,b, fillvalue="")))
	url_string = get_url(coord_list)

	return df_z.url.tolist(), df_z.name.tolist(), url_string


### functions to get proper areas for filter dropdowns
def get_loc1():
    out_list = []
    with open("loc_dict.pkl", 'rb') as picklefile: 
        loc_dict = pickle.load(picklefile)
    for key in loc_dict:
        out_list.append(key)
    out_list = sorted(out_list)
    return out_list

def get_loc2(loc1):
    out_list = []
    with open("loc_dict.pkl", 'rb') as picklefile: 
        loc_dict = pickle.load(picklefile)
    for key in loc_dict[loc1]:
        out_list.append(key)
    out_list = sorted(out_list)
    return out_list

def get_loc3(loc1, loc2):
    out_list = []
    with open("loc_dict.pkl", 'rb') as picklefile: 
        loc_dict = pickle.load(picklefile)
    for key in loc_dict[loc1][loc2]:
        out_list.append(key)
    out_list = sorted(out_list)
    return out_list

def get_loc4(loc1, loc2, loc3):
    out_list = []
    with open("loc_dict.pkl", 'rb') as picklefile: 
        loc_dict = pickle.load(picklefile)
    for key in loc_dict[loc1][loc2][loc3]:
        out_list.append(key)
    out_list = sorted(out_list)
    return out_list


#---------- URLS AND WEB PAGES -------------#

# Initialize the app
app = flask.Flask(__name__)

# Homepage
@app.route("/")
def viz_page():
    """
    Homepage: serve our visualization page
    """
    with open("recommender.html", 'r') as viz_file:
        return viz_file.read()

    

# Using this post method to return data from the python script
@app.route("/routes", methods=["POST"])
def route():
    """
    When A POST request with json data is made to this uri,
    Read the example from the json, generate recommended routes and
    send it with a response
    """
    data = flask.request.json
    email = data["email"]
    min_diff = data["min_diff"]
    max_diff = data["max_diff"]
    stars = int(data["stars"])
    route_type = data["type"]
    radius = float(data["radius"])
    rpd = int(data["rpd"])
    loc0 = data['loc1']
    loc1 = data['loc2']
    loc2 = data['loc3']
    loc3 = data['loc4']

    #get routes from pythons script
    url_list, names, map_url = get_recommendations(email, min_diff, max_diff, stars, route_type, radius, rpd,
    												loc0, loc1, loc2, loc3)

    # Put the result in a nice dict so we can send it as json
    results = {"url": url_list, "map_url": map_url, "name_list": names}
    return flask.jsonify(results)

@app.route("/loc", methods=["POST"])
def loc_one():
    """
    When A POST request with json data is made to this uri,
    Read the example from the json, generate list of areas and
    send it with a response
    """
    data = flask.request.json
    loc1 = data["loc1"]
    loc2 = data["loc2"]
    loc3 = data['loc3']
    if loc3 == "":
    	if loc2 == "":
    		if loc1 == "":
    			out_list = get_loc1()
    		else:
    			out_list = get_loc2(loc1)
    	else:
    		out_list = get_loc3(loc1, loc2)
    else:
    	out_list = get_loc4(loc1, loc2, loc3)


    # Put the result in a nice dict so we can send it as json
    results = {"loc": out_list}
    return flask.jsonify(results)


#--------- RUN WEB APP SERVER ------------#

# Start the app server on port 80
# (The default website port)
app.run(host='0.0.0.0')
app.run(debug=True)





