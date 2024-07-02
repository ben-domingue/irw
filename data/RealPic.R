#paper. https://link.springer.com/article/10.3758/s13428-020-01523-z
library(dplyr)
library(tidyr)
library(readxl)

data <- read_excel("Table1.Item norms (Supplemental materials)_revisedversion.xls", sheet = 2, skip = 1)

data <- data %>%
  select("Original File Name",Mean...11,Mean...26,Mean...41,Mean...56,Mean...71,Mean...86,Mean...101) %>%
  rename(id = "Original File Name",Familiarity = Mean...11,Typicality = Mean...26,
         "Picture-name agreement" = Mean...41,"Visual Complexity" = Mean...56,
         "Aesthetic Appeal" = Mean...71,Arousal = Mean...86,Valence = Mean...101 )

data_1 <- data %>%
  pivot_longer(
    cols = -c(id), 
    names_to = "item", 
    values_to = "resp"
  )

saveRDS(data_1, "RealPic.RData")         


##saved as realpic_souza2021.Rdata
