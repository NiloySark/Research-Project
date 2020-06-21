# Research-Project
Source Code for Computer Science Research Project Regarding Video game Analysis

Data collection: 

Steamid.py 

Generates Steam ID and does API call to Get appropriate Player Information and stores it as an individual file on a Couchdb Instance
The API key and Couchdb Instance IP address are encrypted for security purposes.

FriendID.py

Accesses the stored steam IDs from CouchDB, Makes an API call to get the Friend information and using the Friend IDs makes API calls to get their information.

Data Refinement: 

Aus.JSON 
Contains city name and coordinate information for all of Australia

Appinfo.JSON
Contains information about individual games such as their price and genres.

final.JSON
Is the Final  JSON Updated with the city names,coordinates, game genre and thier prices.

Updated.JSON
Is the resultant JSON after updating the Player info JSON with the City information.

Refine.py
Loads up 'games1.json' (the JSON that contains the cumulative infomation of ALL the data from CouchDB), updates that with the city information from Aus.JSON for all players and stores them in Updated.JSON

Refine2.py
Loads up Updated.JSON and appinfo.json, checks every game ID and adds the approrpriate information to the playerdata

Data Analysis:

Attendance.JSON
contains information about the number of people who dropped out of school per state.

Domestic.JSON
contains information about Domestic violence and other violent incidents percity in Australia.

Final2.JSON
another version of Final.JSON that is updated for all users with the city information and game information.

analyze.py
The python script for analysis, creates a nested dictionary containing states and cities and for each city stores the players that are in them.
calculates the total playtimes,expenses,number of players and the games that are played per state and per city, finds the top 5 for each for ease of analysis and then plots the appropriate graphs using MatPlotLib library.


