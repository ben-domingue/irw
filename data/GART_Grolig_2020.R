# Paper: https://link.springer.com/article/10.1007/s11145-019-10014-3
# Data: https://osf.io/4hcwt/
library(tidyr)
library(dplyr)

data <- read.table("raw.data_German.ART_A.dat", header = TRUE, sep = "", stringsAsFactors = FALSE)
data <- data |>
  rename(id=subid)
data <-  pivot_longer(data, cols=-c(id, age, gender), names_to='item', values_to='resp')

# ------ Process Dataset 2 ------
lines <- readLines("raw.data_German.ART_B.dat")

# Identify which line(s) have a different number of elements
# line_lengths <- sapply(strsplit(lines, "\\s+"), length)
# problem_lines <- which(line_lengths != 78)
lines[28] <- sub("\\. Mai\tmale$", "\tmale", lines[28])
lines[23] <- sub("\\. Mai\tmale$", "\tmale", lines[23])
writeLines(lines, con="raw.data_German.ART_B_Fixed.dat")

data2 <- read.table("raw.data_German.ART_B_Fixed.dat", header = TRUE, sep = "", stringsAsFactors = FALSE)
data2 <- data2 |>
  rename(id=subid)
data2 <-  pivot_longer(data2, cols=-c(id, age, gender), names_to='item', values_to='resp')
data2$id <- as.character(data2$id)

# Merge 2 datasets
stacked_df <- bind_rows(
  data %>% mutate(group = "Study 1"),
  data2 %>% mutate(group = "Study 2")
)

save(stacked_df, file="GART_Grolig_2020.Rdata")
write.csv(data2, "GART_Grolig_2020.csv", row.names=FALSE)
