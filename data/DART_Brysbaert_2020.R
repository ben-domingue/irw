# Paper: https://journalofcognition.org/articles/10.5334/joc.95
# Data: https://osf.io/u4vhs/
library(readxl)
library(tidyr)
library(dplyr)

# -------- Process Dataset 1 -------- 
df1 <- read_excel("raw_data_study1.xlsx")
df1 <- df1 |>
  rename(id=Toegangscode, mother_language=`Moedertaal-`, gender=`Geslacht-`, age=`Leeftijd-`)
df1$mother_language <- ifelse(!is.na(df1$`Moedertaal- [Andere]`), df1$`Moedertaal- [Andere]`, df1$mother_language)
df1 <- df1 |>
  select(-`Moedertaal- [Andere]`, -`Aantal boeken gelezen in het afgelopen 1ar-`)
df1 <-  pivot_longer(df1, cols=-c(id, gender, age, mother_language), names_to='item', values_to='resp')

save(df1, file="DART_Brysbaert_2020_1.Rdata")
write.csv(df1, "DART_Brysbaert_2020_1.csv", row.names=FALSE)

# -------- Process Dataset 3 & 4 -------- 
df3 <- read_excel("raw_data_study3.xlsx")
df3 <- df3 |>
  rename(id=Subject, item=Name, resp=Correct) |>
  select(-ItemNr, -Condition)

df4 <- read_excel("raw_data_study4.xlsx")
df4 <- df4 |>
  rename(id=Subject, item=Name, resp=Correct) |>
  select(-ItemNr, -Condition)

# -------- Process Dataset 5 -------- 
# Pre-process artist data for accuracy evaluation of Dataset5
artist_data <- read_excel("DART_R Excel versie.xlsx")
Name <- c(artist_data$Name...1, artist_data$Name...4, artist_data$Name...7)
Code <- c(artist_data$Code...2, artist_data$Code...5, artist_data$Code...8)
artist_data <- data.frame(Name, Code)

df5 <- read_excel("raw_data_study5.xlsx")
df5 <- df5 |>
  rename(id=Participantcode)
artist_codes <- setNames(artist_data$Code, artist_data$Name)

# Loop through each artist's column in df5 and encode the responses
for (artist in names(df5)[-1]) {
  # Compare the participants' responses with the correct code and update df5 directly
  df5[[artist]] <- ifelse(df5[[artist]] == artist_codes[artist], 1, 0)
}
df5 <-  pivot_longer(df5, cols=-c(id), names_to='item', values_to='resp')

stacked_df <- bind_rows(
  df3 %>% mutate(group = "Study 3"),
  df4 %>% mutate(group = "Study 4"),
  df5 %>% mutate(group = "Study 5")
)

save(stacked_df, file="DART_Brysbaert_2020_3&4&5.Rdata")
write.csv(stacked_df, "DART_Brysbaert_2020_3&4&5.csv", row.names=FALSE)
