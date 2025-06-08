# Paper: https://www.sonabusinessschool.com/journal/previous-issues/june-2017/relationship-academic-process.pdf
# Data: https://dataverse.harvard.edu/file.xhtml?persistentId=doi:10.7910/DVN/1KDJTZ/QTQOC4&version=1.0
library(haven)
library(dplyr)
library(tidyr)
library(readxl)

df <- read_excel("CFC Dataset without AP - Vaidhyanatha Balaji.xlsx")
df <- df |>
  rename(cov_age=Age, cov_edu='Education Level', cov_nationality=Nationality)
df <- df %>%
  mutate(id = row_number())
df <- pivot_longer(df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

write.csv(df, "mrv_panasiuk_2025.csv", row.names = FALSE)
save(df,  file="mrv_panasiuk_2025.rdata")
