library(rpart)
library(shiny)
library(ggplot2)
library(leaflet)
library(DT)

#prediction
crime_data = read.csv("atlcrime_weather.csv")
number = nrow(crime_data)

for (index in 1:number) {
  crime_data$month[index] = as.integer(substr(crime_data$date[index], 1, 2))
}
crime_data$cluster_crime = paste(crime_data$cluster, crime_data$crime, sep = "_")
tree_model = rpart(cluster_crime ~ temp + precipitation + occurence + month, data = crime_data, method="class")

ui <- fluidPage(
  titlePanel("Crime Prediction in Atlanta"),
  sidebarLayout(
    sidebarPanel(
      numericInput("temp", "Temperature:", value = 25, min = -10, max = 50),
      numericInput("precipitation", "Precipitation:", value = 0.1, min = 0, max = 10),
      numericInput("occurence", "Occurrence:", value = 100, min = 0, max = 1000),
      numericInput("month", "Month:", value = 1, min = 1, max = 12),
      actionButton("predict", "Predict")
    ),
    
    mainPanel(
      DTOutput("probTable"),
      leafletOutput("map")
    )
  )
)

server <- function(input, output) {
  observeEvent(input$predict, {
    new_data <- data.frame(
      temp = input$temp,
      precipitation = input$precipitation,
      occurence = input$occurence,
      month = input$month
    )
    
    prediction_probs <- predict(tree_model, new_data, type = "prob")
    prediction_probs_df <- as.data.frame(t(prediction_probs))
    
    output$probTable <- renderDT({
      datatable(prediction_probs_df, options = list(pageLength = 5, autoWidth = TRUE))
    })
    
    output$map <- renderLeaflet({
      leaflet() %>%
        addTiles() %>%
        addMarkers(lng = -84.407809, lat = 33.759545, popup = "Prediction Location")
    })
  })
}

shinyApp(ui = ui, server = server)