import json
import requests
import sqlite3
import geocoder
import bs4
import operator
# import matplotlib.pyplot as plt
import math
import plotly.graph_objs as go




####### Global Constants ####### 
DB_NAME = 'db.sqlite'
CACHE_FILE_NAME='cache.json'
YELP_API_KEY = ""
MAPBOX_TOKEN = ""
HEADERS = {}
CACHE = {}


####### Class declarations ########
class RESTAURANT:
    def __init__(self,  name='', city='', rating=0.0, price='', phone_num='', category='', lat=0.0, lon=0.0, address='', zipcode='', review_num = 0, city_idx=-1, state_idx= -1, url=""):
        self.name = name
        self.city = city
        self.rating = rating
        self.price = price
        self.phone_num = phone_num
        self.category = category
        self.lat = lat
        self.lon = lon
        self.address = address
        self.zipcode = zipcode
        self.review_num = review_num
        self.city_idx = city_idx
        self.state_idx = state_idx
        self.url = url


    def print_res(self):
        return f"({self.rating}) {self.name} : ".rjust(10) + f"{self.address}, ".rjust(10)+ f"{self.phone_num}"




######## K-D Tree ############

def construct_node(val, left, right):
    """
    Node constructor in json format
    """
    node = {}
    node["val"] = val
    node["left"] = left
    node["right"] = right
    return node

def build_kd_tree(res_list, depth):
    """
    Construct the k-d tree from a list of restaurants
    Return a dict of kd-tree
    """
    if len(res_list) == 0:
        return "None"
    
    res_list.sort(key=operator.itemgetter(depth % 2))
    middle = len(res_list) // 2

    return construct_node(
        val = res_list[middle],
        left = build_kd_tree(res_list[:middle], depth+1),
        right = build_kd_tree(res_list[middle+1:], depth+1)
    )

# def show_tree(tree, plot=True):
#     def recur_p(node, depth):
#         if node == "None":
#             return
#         if depth % 2 == 0:
#             plt.axvline(x=node["val"][0], ymin=0, ymax=1)
#         else:
#             plt.axhline(y=node["val"][1], xmin=0, xmax=5)
#         plt.scatter(node["val"][0], node["val"][1])
#         recur_p(node["left"], depth+1)
#         recur_p(node["right"], depth+1)

#     recur_p(tree, 0)
#     if plot:
#         plt.show()

def nodes_within_distance(tree, x, y, d):
    """
    Search the kd tree to find node within distance d from location (x, y)
    return: a list of nodes that satisfy the condition 
    """
    node_list = []
    def recur_h(node, x, y, d, depth):
        if node == "None":
            return

        if within_distance(x, y, node["val"][0], node["val"][1], d):
            node_list.append(node["val"])

        if depth % 2 == 0:
            # Partitioning over x
            if within_distance(x, y, node["val"][0], y, d):
                # if the partition line (vertical at x) 
                # passes through or intersects the circle, search both branches
                recur_h(node["left"], x, y, d, depth+1)
                recur_h(node["right"], x, y, d, depth+1)
            else:
                # otherwise consider which branch is closer to the target
                if x< node["val"][0]:
                    recur_h(node["left"], x, y, d, depth+1)
                else:
                    recur_h(node["right"], x, y, d, depth+1)

        else:
            #partitioning over y
            if within_distance(x, y, x, node["val"][1], d):
                # if the partition line (horizontal at y) 
                # passes through or intersects the circle, search both branches
                recur_h(node["left"], x, y, d, depth+1)
                recur_h(node["right"], x, y, d, depth+1)
            else:
                # otherwise consider which branch is closer to the target
                if y< node["val"][1]:
                    recur_h(node["left"], x, y, d, depth+1)
                else:
                    recur_h(node["right"], x, y, d, depth+1)  
    recur_h(tree, x, y ,d, 0)

    return node_list


# def within_distance(x1, y1, x2, y2, d):
#     return (x1-x2)**2 + (y1-y2)**2 <= d**2

def calc_distance(lat1, lon1, lat2, lon2):
    """Calculate the distance between two points given lattitude and longitude"""
    # convert lattitude and longitude to radian
    lat1 = lat1/(180/math.pi) 
    lat2 = lat2/(180/math.pi) 
    lon1 = lon1/(180/math.pi) 
    lon2 = lon2/(180/math.pi) 

    # radius of Earch in km
    r = 6371
       
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))

    return (c * r)

def within_distance(lat1, lon1, lat2, lon2, max_d):
    """ 
    Determines whether the distance between
    (lat1, lon1) and (lat2, lon2) is within max_d
    """
    d = calc_distance(lat1, lon1, lat2, lon2)
    return d**2 <= max_d**2


######## CACHE functions #########

def gen_unique_key(base_url, params):
    """
    Generate a unique key for cache based on url request and parameters 
    """
    params_list = []
    for key in params:
        params_list.append(f'{key}_{params[key]}')
    params_list.sort()
    unique_key = base_url + "_" + "_".join(params_list)
    return unique_key

def load_from_cache(file_name):
    """
    Load the CACHE object from the json file
    """
    try:
        file = open(file_name, 'r')
        cache = json.loads(file.read())
        file.close()
    except:
        cache = {}
    return cache


def save_to_cache( file_name, cache):
    """
    Store the CACHE object into the json file
    """
    file = open(file_name, 'w')
    file.write(json.dumps(cache))
    file.close()



######## API calls #########

def make_url_request(baseurl):
    """
    Helper function to make api request with only base url
    Store the response in cache to improve performance
    """
    if baseurl in list(CACHE.keys()):
        return CACHE[baseurl]

    response = requests.get(baseurl)
    CACHE[baseurl] = response.text
    save_to_cache(CACHE_FILE_NAME, CACHE)
    return CACHE[baseurl]

def make_api_request(baseurl, params):
    """
    Helper function to make api request with base url address and query
    Store the response in cache to improve performance
    """
    cache_key = gen_unique_key(baseurl, params)
    if cache_key in CACHE:
        return CACHE[cache_key]

    response = requests.get(baseurl, headers=HEADERS, params=params)
    CACHE[cache_key] = response.json()
    save_to_cache(CACHE_FILE_NAME, CACHE)
    return CACHE[cache_key]

    
def yelp_api_request(city, term="restaurants"):
    """
    Fetch information from yelp based on city and term (restaurant,cafe and etc)
    """
    baseurl = "https://api.yelp.com/v3/businesses/search"
    params = {"location": city,"term": term}
    return make_api_request(baseurl, params)





def init_cities_db (state_city_dict):
    """
    Initialize the database for cities
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT name FROM sqlite_master WHERE type='table' AND name='Cities'
                """)
    if not cur.fetchone():
        cur.execute("""
            CREATE TABLE "Cities" (
                "Id"    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "City"  TEXT NOT NULL,
                "State" TEXT NOT NULL
            );
            """)
        for state in state_city_dict:
            for city in state_city_dict[state]:
                cur.execute("""
                    INSERT INTO Cities VALUES (NULL, ?, ?)
                """, (city, state))
        conn.commit()

    conn.close()


def init_state_city(CACHE):
    """
    Scrape cities from britannica.com and store in cache
    return: state_city_dict={}: A dict that maps state names to city lists
            states_list: 1d array where states_list[i] = state name
            cities_list: 2d array where cities_list[i][j] = city name


    """
    if "cache_info" in CACHE:
        return CACHE["cache_info"]["state_city_dict"], CACHE["cache_info"]["states_list"], CACHE["cache_info"]["cities_list"]
    # scrape states from britannica.com
    base_url = "https://www.britannica.com/topic/list-of-cities-and-towns-in-the-United-States-2023068"
    response_text = make_url_request(base_url)
    soup = bs4.BeautifulSoup(response_text, 'html.parser')
    states_list = soup.find_all('h2', class_="h1")
    states_list = [state.find("a", class_="md-crosslink").text for state in states_list]
    CACHE["cache_info"] = {}
    for s in states_list:
        CACHE["cache_info"][s] = {}

    # scrape the cities from britannica.com
    cities_soup = soup.find_all("ul", class_="topic-list")
    cities_list = []
    i=0
    for cities in cities_soup:
        cities_list.append([city.find("a").text if city.text != "Napa" else "Napa" for city in cities])
        for city in cities_list[i]:
            CACHE["cache_info"][states_list[i]][city] = {}
        i+=1
    
    state_city_dict = dict(zip(states_list, cities_list))
    CACHE["cache_info"]["state_city_dict"] = state_city_dict
    CACHE["cache_info"]["states_list"] =  states_list
    CACHE["cache_info"]["cities_list"] = cities_list
    save_to_cache(CACHE_FILE_NAME, CACHE)
    return state_city_dict, states_list, cities_list
    


def build_restaurants_list(city_idx, state_idx, city):
    """
    Use the json response from yelp api to generate restaurants objects, given the city
    return: a list of restaurant objects
    """
    state = CACHE["cache_info"]["states_list"][state_idx]
    res_list = []

    # from cache
    if "res_list" in CACHE["cache_info"][state][city]:

        for res in CACHE["cache_info"][state][city]["res_list"]:

            temp_r = RESTAURANT(name=res["name"], city=res["city"],     
                rating=res["rating"], price=res["price"], lat=res["lat"], 
                lon=res["lon"], address=res["address"], 
                zipcode=res["zipcode"], review_num = res["review_num"], 
                phone_num=res["phone_num"], city_idx=city_idx, state_idx=state_idx,
                url = res['url']
            )
            res_list.append(temp_r)

        return res_list

        
    # If it's not present in cache, get it from the yelp api
    yelp_dict = yelp_api_request(city)
    

    CACHE["cache_info"][state][city]["res_list"] = []

    tree_list = []
    i=0
    for res in yelp_dict["businesses"]:       
        price = 0 if "price" not in res else len(res["price"])
        temp_r = RESTAURANT(name=res["name"], city=res["location"]["city"],     
            rating=res["rating"], price=price, lat=res["coordinates"]["latitude"], 
            lon=res["coordinates"]["longitude"], address=res["location"]["address1"], 
            zipcode=res["location"]["zip_code"], review_num = res["review_count"], 
            phone_num=res["display_phone"], city_idx=city_idx, state_idx=state_idx, 
            url=res['url']
        )

        res_list.append(temp_r)

        tree_list.append([temp_r.lat, temp_r.lon, i])
        i += 1

        # store the restaurant in cache
        res_obj = {}
        res_obj["name"] = res["name"]
        res_obj["city"] = res["location"]["city"]
        res_obj["rating"]=res["rating"]
        res_obj["price"]=price
        res_obj["lat"] = res["coordinates"]["latitude"]
        res_obj["lon"] = res["coordinates"]["longitude"]
        res_obj["address"] = res["location"]["address1"]
        res_obj["zipcode"] = res["location"]["zip_code"]
        res_obj["review_num"] = res["review_count"]
        res_obj["phone_num"] = res["display_phone"]
        res_obj["city_idx"] = city_idx
        res_obj["state_idx"] = state_idx
        res_obj["url"] = res['url']

        CACHE["cache_info"][state][city]["res_list"].append(res_obj)

    # store the kd tree of a given city in cache
    CACHE["cache_info"][state][city]["kd_tree"] = build_kd_tree(tree_list, 0)

    save_to_cache(CACHE_FILE_NAME, CACHE)
    
    return res_list



def print_states(states):
    # print all states in terminal
    print(f"\nStates in USA: ")
    for i in range(len(states)):
        print(str(i + 1).rjust(2) + ": " + states[i])

def print_cities(cities, state):
    # print all cities in terminal
    print(f"\nCities in {state}:")
    for i in range(len(cities)):
        print(str(i + 1).rjust(2) + ": " + cities[i])
    print ("0:  Select another state")

def print_restaurants(res_list, city):
    # print all restaurants in terminal
    print(f"\nRestaurants in {city}:")
    for i in range(len(res_list)):
        print(str(i + 1).rjust(2) + ": " + res_list[i].print_res())



def input_state(states_list):
    """
    Helper function to prompt the user to enter a state number
    """
    while True:
        state_idx = input("Enter the state (a number) or 'quit': ")
        if int(state_idx) < 1 or int(state_idx) > len(states_list):
            print("Enter a valid state number")
        elif state_idx == 'quit':
            exit()
        else:
            break
    return int(state_idx) -1

def input_city(cities_list, state):
    """
    Helper function to prompt the user to enter a city number
    """
    print_cities(cities_list, state)
    while True:
        city_idx = input("Enter the city (a number): ")
        if city_idx == 'quit':
            exit()
        elif int(city_idx) < 0 or int(city_idx) > len(cities_list):
            print("Enter a valid city number: ")
        else:
            break
    return int(city_idx) -1

def input_constraint(res_list, kd_tree):
    """
    Plot the restaurants given a set of constraints. 
    Prompt the user to enter min rating, max price and max distance 
    """
    min_rating = float(input("Please Enter a minummum rating (from 0 to 5): "))
    max_p = float(input("Please Enter a maximum price (from 0 to 3): "))
    g = geocoder.ip('me')
    cur_lat = g.latlng[0]
    cur_lon = g.latlng[1]

    print(f"\n1: Use my current location (lattitude:{cur_lat}, longitude:{cur_lon})")
    print("2: Use a custom location")
    if int(input("Please enter your choice: ")) != 1:
        cur_lat = float(input("Please enter your lattitude: "))
        cur_lon = float(input("Please enter your longitude: "))
    max_d = float(input("Please enter a maximum distance in km: "))

    # retrieve a list of restaurants satisfying the distance condition
    res_idx_list = nodes_within_distance(kd_tree, cur_lat, cur_lon, max_d)

    name = []
    text = []
    lat = []
    lon = []
    rating = []
    r_l = []

    
   
    for idx in res_idx_list:
        res = res_list[idx[2]]

        if res.rating>= min_rating and res.price <= max_p:
            name.append(res.name)
            d = calc_distance(cur_lat, cur_lon, res.lat, res.lon)
            text.append(res.print_res()+ f", Distance from Current Location: {d} km")
            lat.append(res.lat)
            lon.append(res.lon)
            rating.append(res.rating)
            r_l.append(res)
    
    while True:
        print("\np1: Show all restaurants on map with the constraint")
        print("p2: Plot all restaurants by rating with the constraint")
        print("p3: Plot all restaurants by price with the constraint")
        print("0:  Go back to previous options")
        cin = input("\nChoose a plot given constraint: ")     
        if cin == "p1":
                
            fig = go.Figure(
                go.Scattermapbox(
                    text=text,
                    lat=lat,
                    lon=lon,
                    mode='markers',
                    marker=go.scattermapbox.Marker(color=rating,colorbar=dict(title="ratings"))          
            ))
            
            trace2 = go.Scattermapbox(
                lat=[cur_lat],
                lon=[cur_lon],
                text='Your Current Location',
                mode='markers',
                marker=go.scattermapbox.Marker(color='red', size = 15)    
            )
            fig.add_trace(trace2)
            fig.update_layout(
                dict(
                    autosize=True,
                    mapbox=go.layout.Mapbox(
                        accesstoken=MAPBOX_TOKEN,
                        center=go.layout.mapbox.Center(lat=res_list[0].lat,lon=res_list[0].lon),
                        zoom=15
                    )                     
                )               
            )
            fig.show()
        elif cin == "p2":
            r_l2 = sorted(r_l, key=lambda x: x.rating, reverse=True)
            rate2 = []
            name2 = []
            for res in r_l2:
                rate2.append(res.rating)
                name2.append(res.name)
            fig = go.Figure(
                go.Bar(x=name,y=rate2),
            )
            fig.update_yaxes(title_text="Rating")
            fig.show()
        elif cin == "p3":
            r_l3 = sorted(r_l, key=lambda x: x.price, reverse=True)
            price3 = []
            name3 = []
            for res in r_l3:
                name3.append(res.name)
                price3.append(res.price)
            fig = go.Figure(
                go.Bar(x=name3,y=price3),
            )
            fig.update_yaxes(title_text="Price")
            fig.show()
        elif cin == "0":
            break
        else:
            print("Please Enter a valid command")

    


    

def input_options(state,city, res_list):
    """
    Helper function to prompt the user to enter options for data visualization
    """
    res_list.sort(key=lambda x: x.rating, reverse=True)
    name = []
    text = []
    lat = []
    lon = []
    rating = []
    review_num = []

    for res in res_list:
        name.append(res.name)
        text.append(res.print_res())
        lat.append(res.lat)
        lon.append(res.lon)
        rating.append(res.rating)
        review_num.append(res.review_num)
    while True:
        print("\nEnter a restaurant number for detailed information, or select a plot for data visualization (p1, p2 and etc)")
        print("p1: Show all restaurants on map")
        print("p2: Plot all restaurants by rating")
        print("p3: Plot all restaurants by price")
        print("p4: Set constraints and plot restaurants")
        print("0: Select another city")
        cin = input("\nEnter a number or a plot: ")     
        if cin == "p1":
            
            fig = go.Figure(
                go.Scattermapbox(
                    text=text,
                    lat=lat,
                    lon=lon,
                    mode='markers',
                    marker=go.scattermapbox.Marker(color=rating,colorbar=dict(title="ratings"))          
            ))

            fig.update_layout(
                dict(
                    autosize=True,
                    mapbox=go.layout.Mapbox(
                        accesstoken=MAPBOX_TOKEN,
                        center=go.layout.mapbox.Center(lat=sum(lat)/len(lat),lon=sum(lon)/len(lon)),
                        zoom=15
                    )                     
                )               
            )
            fig.show()
        elif cin == "p2":
            fig = go.Figure(
                go.Bar(x=name,y=rating),
            )
            fig.update_yaxes(title_text="Rating")
            fig.show()
        elif cin == "p3":
            res_list3 = sorted(res_list, key=lambda x: x.price, reverse=True)
            price3 = []
            name3 = []
            for res in res_list3:
                name3.append(res.name)
                price3.append(res.price)
            fig = go.Figure(
                go.Bar(x=name3,y=price3),
            )
            fig.update_yaxes(title_text="Price")
            fig.show()
        elif cin == "p4":
            kd_tree = CACHE["cache_info"][state][city]["kd_tree"]
            input_constraint(res_list, kd_tree)
            
        elif cin.isdigit():
            if int(cin) == 0:
                break
            res = res_list[int(cin)]
            print(f"\nRestaurant: {res.name}")
            print(f"Address: {res.address}, {res.zipcode}")
            print(f"Rating: {res.rating} from {res.review_num} reviews")
            print(res.url)
            
        else:
            print("Please Enter a valid Command")
    




def main():
    global CACHE 
    CACHE = load_from_cache(CACHE_FILE_NAME)
    state_city_dict, states_list, cities_list = init_state_city(CACHE)
    init_cities_db(state_city_dict)

    global YELP_API_KEY
    if "YELP_API_KEY" not in CACHE:
        YELP_API_KEY = input("Please enter your yelp api key (https://www.yelp.com/developers/documentation/v3/get_started): ")      
        CACHE["YELP_API_KEY"] = YELP_API_KEY
    else:
        YELP_API_KEY = CACHE["YELP_API_KEY"]

    global MAPBOX_TOKEN
    if "MAPBOX_TOKEN" not in CACHE: 
        MAPBOX_TOKEN = input("Please enter your mapbox access token (https://docs.mapbox.com/help/getting-started/access-tokens): ")
        CACHE["MAPBOX_TOKEN"] = MAPBOX_TOKEN
    else:
        MAPBOX_TOKEN = CACHE["MAPBOX_TOKEN"]
    global HEADERS
    HEADERS = {'Authorization': f'Bearer {YELP_API_KEY}'}
    while True:
        print_states(states_list)
        state_idx = input_state(states_list)
        cities = cities_list[state_idx]
        print_cities(cities, states_list[state_idx])
        city_idx = input_city(cities, states_list[state_idx])
        if city_idx == -1:
            continue
        city = cities[city_idx]

        
        res_list = build_restaurants_list(city_idx, state_idx, city)
        print_restaurants(res_list, city)

        input_options(states_list[state_idx],city, res_list)
        
    


if __name__ == "__main__":
    main()
    











        
