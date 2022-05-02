## Introduction
The aim of the app is to fetch information of restaurants given state and city, 
and perform data visualization of the restaurants. The program will ask you 
to choose a state and city by entering a number, and then you can choose different plots
by entering p{number}.  

## Prequisite
You need to acquire to access tokens from yelp and mapbox

mapbox access token : https://docs.mapbox.com/help/getting-started/access-tokens

yelp api key: https://www.yelp.com/developers/documentation/v3/get_started

Install dependencies by running:
```
$ pip install -r requirement.txt
```

Run the Program:
```  
$ python main.py
```  


## Commands
### Step 1
A list of states with index number will be displayed in the terminal.
Choose a state by entering a number.

### Step 2
A list of cities will be displayed in the terminal.
Choose a city by entering a number, or enter "0" to go back to step 1.

### Step 3
A list of restaurants will be displayed in the terminal.
You can either enter a number to display the restaurant details, 
or enter p{number} to show a graph (for example: p1) 

### Step 4 (If p4 is entered in Step3)
This option allows you to set constaint on the data, including distance to home (in km), 
minimum rating (from 0 to 5) and maxmimum price (from 0 to 3). Then, you can retrieve plots
of restaurants with constraints similar to that from step3


## Data Structure
The data structure I choose is kd-tree. The user may want to set constraint on distance between current location and the restaurant. However, the location of the user may not be static and storing the distances during API call is not sufficient. One naïve approach is to iterate through the restaurant list, and for each restaurant, calculate the distance between restaurant and user location and then filter out the outlier, which has a time complexity of O(N). With a balanced kd-tree, binary search can be performed, and the average time complexity can be reduced to O(log(N)). 


The idea of kd-tree is to partition the nodes with alternating axis. When building a 2d kd-tree with latitude and longitude as coordinates, we choose a pivot and partition the rest of nodes over latitude (nodes with smaller or equal latitude than the pivot belong to the left branch, and nodes with larger latitude goes to the right branch), and then we partition over longitude and repeat. 
 
When searching for nodes within a certain distance, if the current partition line is within the search distance, we need to search both branches; otherwise, we choose the branch that is closest to the user location. 
The kd-tree in the program is built completely with dictionary:
Node[“left”] and Node[“right”] are pointing to another node or “None”, and Node[“val”] contains a list of [latitude, longitude, restaurant_index]. Therefore, there’s no extra conversion between json and tree. The tree is constructed and cached in CACHE["cache_info"][state][city]["kd_tree"], when the restaurants of a city are fetched.


All the tree-related functions are inside “kd-tree.py”:
build_kd_tree(node_list): constructs the kd-tree from a list of nodes
nodes_within_distance(tree, x, y, d): returns a list of nodes within the search range formed by ((x-coordinate, y-coordinate), distance)
show_tree(tree): plot the space partition and nodes


