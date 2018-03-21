# MountainProject Route Recommender
The goal of this project was to create a recommendation engine and associated web application to build the "perfect" day of rock climbing routes for a given MountainProject user. This was done by combining an intrinsic model based on route descriptions (similar routes to those in your history) with an extrinsic model based on user preferences (routes that similar users have completed). The user also has the option to filter by his or her preferences to narrow down the recommendations. Finally, the application outputs the shortest path between each route using a travelling salesman optimization. A presentation outline of the project can be found [here](https://github.com/bgentry91/MountainProject_Route_Recommender/blob/master/Mountain_Project_Route_Recommender_Small.pdf). A short video of the web app "in action" can be found [here](https://github.com/bgentry91/MountainProject_Route_Recommender/blob/master/Route_Recommender_Final.mp4).

An outline of the structure of the engine and application can be seen below.
![App Structure](https://github.com/bgentry91/MountainProject_Route_Recommender/blob/master/Images/App_Structure.png)

A poor quality screenshot of the app's interface can be seen below.
![Interface](https://github.com/bgentry91/MountainProject_Route_Recommender/blob/master/Images/App_ScreenShot.png)

Data was either scraped directly from mountain project or pulled via API. Data collection code can be found in [here](https://github.com/bgentry91/MountainProject_Route_Recommender/tree/master/Scraping).

The web app was developed using a Flask (python) backend with associated JavaScript/HTML front end. Unfortunately, this app is currently not hosted and is only utilized as a proof of concept. The code for both the front & back ends can be found [here](https://github.com/bgentry91/MountainProject_Route_Recommender/tree/master/Web_App).
