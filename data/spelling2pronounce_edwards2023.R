##paper. https://link.springer.com/article/10.3758/s13428-023-02205-2#data-availability
##data. https://github.com/ashleyaedwards/SpellingToPronunciationTransparencyRatings

library(tidyr)

data <- data.frame()
current_id <- 1

for (i in 1:93) {
  file_name <- paste0("cleaned", i, ".csv")
  data_i <- read.csv(file_name) # Read in different datasets
  data_i$id <- seq(from=current_id, by=1, length.out=nrow(data_i)) # Assign an id to each participant
  current_id <- max(data_i$id) + 1
  
  data_i <- data_i |>
    pivot_longer(cols=-id, names_to="item", values_to="resp")
  data <- rbind(data, data_i)
}

df<-as.data.frame(data)
df$rater<-df$id
df$id<-df$item
df$item<-'difficulty'

save(df, file="spelling2pronounce_edwards2023.Rdata")
