## Introduction
The aim of the app is to fetch information of restaurants given state and city, 
and perform data visualization of the restaurants. The program will ask you 
to choose a state and city by entering a number, and then you can choose different plots
by entering p{number}.   

## Prequisite
You need to acquire to access tokens from yelp and mapbox

mapbox access token : https://docs.mapbox.com/help/getting-started/access-tokens

yelp api key: https://www.yelp.com/developers/documentation/v3/get_started


## Commands
### Step 1
A list of states with index number will be displayed in the terminal.
Choose a state by entering a number.

### Step 2
A list of cities will be displayed in the terminal.
Choose a city by entering a number, or enter "0" to go back to step 1.

### Step 3
A list of restaurants will be displayed in the terminal.
You can either enter a number to display the details, 
or enter p{number} to show a graph (for example: p1) 

### Step 4 (If p4 is entered in Step3)
This option allows you to set constaint on the data, including distance to home (in km), 
minimum rating (from 0 to 5) and maxmimum price (from 0 to 3). Then, you can retrieve the similar plots
of restaurants with constraints

