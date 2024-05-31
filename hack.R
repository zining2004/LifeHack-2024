library(httr)
library(jsonlite)
library(MASS)
library(zoo)
library(dplyr)
library(rpart)
library(rpart.plot)
library(lubridate)


crime_data = read.csv("atlcrime.csv")[, 2:12]

#functions
get_weather<- function(long, lat, date) {
  base_url <- "https://archive-api.open-meteo.com/v1/era5"
  
  url <- paste0(base_url, "?latitude=", lat, "&longitude=", long, 
                "&start_date=", date, "&end_date=", date, "&hourly=temperature_2m,precipitation")
  
  response <- GET(url)
  weather_data <- fromJSON(content(response, as = "text"))
  return(weather_data)
}

find_local_max <- function(data) {
  dens <- kde2d(data$long, data$lat, n = 100) # 2D kernel density estimate
  roll_max <- zoo::rollapply(dens$z, 3, max, fill = NA, align = "center")
  local_max <- which(dens$z == roll_max, arr.ind = TRUE)
  if (nrow(local_max) == 0) {
    return(data.frame(long = numeric(0), lat = numeric(0)))
  } else {
    maxima <- data.frame(
      long = dens$x[local_max[, 1]],
      lat = dens$y[local_max[, 2]]
    )
    return(maxima)
  }
}

#making weather dataset
number = length(crime_data[,1])
crime_data$temp = NA
crime_data$precipitation = NA

for (index in 1:number) {
  long = crime_data$long[index]
  lat = crime_data$lat[index]
  date = as.Date(crime_data$date[index], format="%m/%d/%Y")
  weather = get_weather(long, lat, date)
  hour_temp = weather$hourly$temperature_2m 
  crime_data$temp[index] = mean(hour_temp)
  prec = weather$hourly$precipitation
  crime_data$precipitation[index] = sum(prec)
}


#clustering to find patrol route
heads = c("long","lat")
location = crime_data[, heads]
k.max = 15 #maximum number of clusters to test
wss = numeric(k.max)
for (i in 1:k.max) {
  wss[i] = sum(kmeans(location, centers = i)$withinss)
}

plot(1:k.max, wss, pch=20) 
centroids = 9 #based on the graph

kmodel = kmeans(location, centers = centroids)
coordinates = kmodel$centers
crime_data$cluster = kmodel$cluster
crime_data$occurence = NA
occ = kmodel$size
for (i in 1:number) {
  index = crime_data$cluster[i]
  crime_data$occurence[i] = occ[index]
}

write.csv(crime_data, "atlcrime_weather.csv")

local_maximas = crime_data %>% group_by(cluster) %>% do(find_local_max(.))
local_maximas = bind_rows(local_maximas, data.frame(coordinates))
write.csv(local_maximas, "nodes.csv")


