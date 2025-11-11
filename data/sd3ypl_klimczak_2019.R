library(dplyr)
library(haven)

data_1 <- read_sav("Study-1-factor-analysis.sav")
data_2 <- read_sav("Study-2-external-validity.sav")

data_1 <- data_1%>%
  rename(id = nob,
         cov_gender = płeć,
         cov_age = wiek,
         cov_grade = klasa)%>%
  mutate(study =1,
         id = paste(study, id, sep = "_"))

data_2 <- data_2%>%
  rename(id = nob,
         cov_gender = Pleć,
         cov_age = Wiek,
         cov_grade = Klasa,
         cov_school= Szkoła)%>%
  mutate(id = paste("2", id, sep = "_"))


pivot_scale <- function(data, prefix) {
  data %>%
    zap_labels()%>%
    select(id, starts_with("cov_"), matches(paste0("^", prefix, "\\d+$"))) %>%
    pivot_longer(
      cols = starts_with(prefix),
      names_to = "item",
      values_to = "resp"
    )
}

scales <- c("SES", "BFQ", "A")

for (scale in scales) {
  data_sub <- pivot_scale(data_2, scale)
  write.csv(data_sub, paste0("sd3ypl_klimczak_2019_", tolower(scale), ".csv"), row.names = FALSE)
}


data2_SD <- data_2%>%
  mutate(study = 2)%>%
  select(id, starts_with("cov_"), starts_with("SD"))

names(data_1)[startsWith(names(data_1), "SD")] <- sapply(data_1[startsWith(names(data_1), "SD")], \(x) attr(x, "label"))

names(data2_SD)[startsWith(names(data2_SD), "SD")] <- sapply(data2_SD[startsWith(names(data2_SD), "SD")], \(x) attr(x, "label"))
names(data2_SD) <- gsub("^N", "Narc", names(data2_SD))
names(data2_SD) <- gsub("^P", "Psych", names(data2_SD))
names(data2_SD) <- gsub("^M", "Mach", names(data2_SD))

data2_SD<- data2_SD %>% 
  zap_label() %>%
  mutate(study =2)

data_1 <- zap_label(data_1)

data <-bind_rows(data_1, data2_SD)%>%
  pivot_longer(
  cols = starts_with(c("N", "M", "P")),
  names_to = "item",
  values_to = "resp"
)

write.csv(data, "sd3ypl_klimczak_2019_sd3.csv", row.names = FALSE)
