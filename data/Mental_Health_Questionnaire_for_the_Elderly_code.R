setwd('C:/Users/siena/Desktop/irw/Mental Health Questionnaire for the Elderly')

#Read original data
data <- read.csv('Mental_Health_Questionnaire_for_the_Elderly_original.csv')

data_by_id <- data[with(data, order(data$ID), decreasing = FALSE),]

dropnames <- c('X', 'A2_Y', 'A2_M', 'A4O', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6',
                'C1_1_25O', 'C1_2O', 'D1.1', colnames(data_by_id[120:135]))

data_dropped <- data_by_id[, !names(data_by_id) %in% c(dropnames)]

#id column
id <- as.data.frame(rep(data_dropped$ID, 105))

#item column
item <- as.data.frame(rep(colnames(data_dropped[2:106]), each = 1318))

#resp column
resp_data <- data.frame()

for (i in 2:106){
  resp_data1 <- data.frame(data_dropped[i])
  colnames(resp_data1) <- c('resp')
  resp_data <- rbind(resp_data, resp_data1)
}

#combine
df <- cbind(id, item, resp_data)
colnames(df) <- c('id', 'item', 'resp')
df$resp[df$resp == 999999] <- NA
save(df, file = 'Mental_Health_Questionnaire_for_the_Elderly.Rdata') 
