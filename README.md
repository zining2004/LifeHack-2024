atlanta-background.jpg - background picture for the website.

output.png - the heatmap of crime probabilities under the crime predictions page

atlcrime.csv - dataset found on Kaggle (https://www.kaggle.com/datasets/priscillapun/crime-in-atlanta-2017)

atlcrime_weather.csv - dataset including weather conditions, cluster number, and the number of crime cases in each cluster

nodes.csv - crime hotspots (local maximum) of every cluster, used to construct the patrol path 

hack.qmd - generate weather data and then used to cluster crime incidents and generate the nodes.csv and atlcrime_weather.csv files

app.R - Shiny app that allows users to input values and predicts crime probability. 

patrolpath.py - to generate the heatmap based on the number of crimes

style.css - to define the presentation and layout of our index.html file

index.html - main entry point of our website

route.html - page to present the optimal patrol route 

prediction.html - uses app.r to predict crime probabiilties and types.

crime_heatmap.html - display the heatmap that gives an overview of the density of number of crimes happening in Atlanta

optimized_patrol_routes.html - map to plot the points of crime hotspots and show the optimal patrol route
