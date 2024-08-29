# Paper:https://link.springer.com/article/10.3758/s13428-023-02184-4
# Data: https://osf.io/t5js9/
library(tidyr)
library(dplyr)

data <- read.csv("./combined_data.csv")
data <- data[!data$userID %in% c(8387, 8885, 9943), ] # Remove duplicate participants and those who did not declare their gender
rownames(data) <- NULL
data <- data |>
  select(userID, age, AMI_CV_1:AMI_CV_18) |> # Keep only items and relevant columns
  rename(id=userID)
data <- pivot_longer(data, cols=-c(age, id), names_to='item', values_to='resp')

save(data, file="AMI_CV.Rdata")
write.csv(data, "AMI_CV.csv", row.names=FALSE)