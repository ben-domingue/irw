library(pks)
library(tibble)
library(dplyr)
library(tidyr)

setwd("~/Desktop")

data(probability)
pb <- probability[!is.na(probability$b201), sprintf("b2%.2i", 1:12)]
Q1=sf1 <- read.table(header = TRUE, text = "
                    item cp id pb un
                    1  0  0  1  0
                    2  1  0  0  0
                    3  0  0  0  1
                    4  0  1  0  0
                    5  1  0  1  0
                    6  1  0  1  0
                    7  0  0  1  1
                    8  0  0  1  1
                    9  0  1  1  0
                    10  1  1  0  0
                    11  1  1  1  0
                    12  0  1  1  1
                    ")
Q1=Q1[,-1]

colnames(Q1) <- paste0("A", 1:4)
colnames(pb) <- paste0("V", 1:12)

convert.fraction.data <- function(dat, Q) {
  
  item_names <- colnames(dat)
  
  dat_with_id <- rownames_to_column(dat, var = "id")
  
  dat_ready <- dat_with_id %>%
    pivot_longer(cols = -id, names_to = "item", values_to = "resp") %>%
    left_join(as.data.frame(Q) %>% 
                add_column(item = item_names)) 
  return (dat_ready)
}
pb_ready <- convert.fraction.data(pb, Q1)

# switch the column order of the pb_ready for column id and item
pb_ready <- pb_ready %>% select(item, id, resp, everything())

# change the name of column 4-7 to Q_matrix_A1, Q_matrix_A2, Q_matrix_A3, Q_matrix_A4
colnames(pb_ready)[4:7] <- paste0("Q_matrix_A", 1:4)

# save the pb_ready as a .Rdata file
save(pb_ready, file = "probability.Rdata")
