library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)
library(readr)
library(readxl)
library(sas7bdat)

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) - 1)), ]
  return(df)
}

data_web_df <- read_csv("data_anonymizedWebRecruit.csv")
data_web_df <- data_web_df %>%
  mutate(id = row_number())
data_web_df <- data_web_df[-c(1, 2), ]

data_IR_df <- read_csv("data_anonymizedInternalRecruit.csv")
data_IR_df <- data_IR_df %>%
  mutate(id = row_number())
data_IR_df  <- data_IR_df [-c(1, 2), ]

DASS_web_df <- data_web_df |>
  select(starts_with("DASS"), id)
DASS_web_df <- remove_na(DASS_web_df)
DASS_web_df <- pivot_longer(DASS_web_df, cols=-c(id), names_to="item", values_to="resp")

DASS_IR_df <- data_IR_df |>
  select(starts_with("DASS"), id)
DASS_IR_df <- remove_na(DASS_IR_df)
DASS_IR_df <- pivot_longer(DASS_IR_df , cols=-c(id), names_to="item", values_to="resp")

DASS_web_df $group <- "WebRecruit"
DASS_IR_df$group <- "InternalRecruit"

DASS_df <- rbind(DASS_web_df,DASS_IR_df)

save(DASS_df, file="PEMAIW_Qiu_2020_DASS.Rdata")
write.csv(DASS_df, "PEMAIW_Qiu_2020_DASS.csv", row.names=FALSE)

FFMQ_web_df <- data_web_df |>
  select(starts_with("FFMQ"), id)
FFMQ_web_df <- remove_na(FFMQ_web_df)
FFMQ_web_df <- pivot_longer(FFMQ_web_df, cols=-c(id), names_to="item", values_to="resp")

FFMQ_IR_df <- data_IR_df |>
  select(starts_with("FFMQ"), id)
FFMQ_IR_df <- remove_na(FFMQ_IR_df)
FFMQ_IR_df <- pivot_longer(FFMQ_IR_df , cols=-c(id), names_to="item", values_to="resp")

FFMQ_web_df$group <- "WebRecruit"
FFMQ_IR_df$group <- "InternalRecruit"

FFMQ_df <- rbind(FFMQ_web_df,FFMQ_IR_df)

save(FFMQ_df, file="PEMAIW_Qiu_2020_FFMQ.Rdata")
write.csv(FFMQ_df, "PEMAIW_Qiu_2020_FFMQ.csv", row.names=FALSE)

MEQ_web_df <- data_web_df |>
  select(starts_with("MEQ"), id)
MEQ_web_df <- remove_na(MEQ_web_df)
MEQ_web_df <- pivot_longer(MEQ_web_df, cols=-c(id), names_to="item", values_to="resp")

MEQ_IR_df <- data_IR_df |>
  select(starts_with("MEQ"), id)
MEQ_IR_df <- remove_na(MEQ_IR_df)
MEQ_IR_df <- pivot_longer(MEQ_IR_df , cols=-c(id), names_to="item", values_to="resp")

MEQ_web_df$group <- "WebRecruit"
MEQ_IR_df$group <- "InternalRecruit"

MEQ_df <- rbind(MEQ_web_df,MEQ_IR_df)

save(MEQ_df, file="PEMAIW_Qiu_2020_MEQ.Rdata")
write.csv(MEQ_df, "PEMAIW_Qiu_2020_MEQ.csv", row.names=FALSE)

MLQ_web_df <- data_web_df |>
  select(starts_with("MLQ"), id)
MLQ_web_df <- remove_na(MLQ_web_df)
MLQ_web_df <- pivot_longer(MLQ_web_df, cols=-c(id), names_to="item", values_to="resp")

MLQ_IR_df <- data_IR_df |>
  select(starts_with("MLQ"), id)
MLQ_IR_df <- remove_na(MLQ_IR_df)
MLQ_IR_df <- pivot_longer(MLQ_IR_df , cols=-c(id), names_to="item", values_to="resp")

MLQ_web_df$group <- "WebRecruit"
MLQ_IR_df$group <- "InternalRecruit"

MLQ_df <- rbind(MLQ_web_df,MLQ_IR_df)

save(MLQ_df, file="PEMAIW_Qiu_2020_MLQ.Rdata")
write.csv(MLQ_df, "PEMAIW_Qiu_2020_MLQ.csv", row.names=FALSE)

PANAS_web_df <- data_web_df |>
  select(starts_with("PANAS"), id)
PANAS_web_df <- remove_na(PANAS_web_df)
PANAS_web_df <- pivot_longer(PANAS_web_df, cols=-c(id), names_to="item", values_to="resp")

PANAS_IR_df <- data_IR_df |>
  select(starts_with("PANAS"), id)
PANAS_IR_df <- remove_na(PANAS_IR_df)
PANAS_IR_df <- pivot_longer(PANAS_IR_df , cols=-c(id), names_to="item", values_to="resp")

PANAS_web_df $group <- "WebRecruit"
PANAS_IR_df$group <- "InternalRecruit"

PANAS_df <- rbind(PANAS_web_df,PANAS_IR_df)

save(PANAS_df, file="PEMAIW_Qiu_2020_PANAS.Rdata")
write.csv(PANAS_df, "PEMAIW_Qiu_2020_PANAS.csv", row.names=FALSE)

BWSS_web_df <- data_web_df |>
  select(starts_with("BWSS"), id)
BWSS_web_df <- remove_na(BWSS_web_df)
BWSS_web_df <- pivot_longer(BWSS_web_df, cols=-c(id), names_to="item", values_to="resp")

BWSS_IR_df <- data_IR_df |>
  select(starts_with("BWSS"), id)
BWSS_IR_df <- remove_na(BWSS_IR_df)
BWSS_IR_df <- pivot_longer(BWSS_IR_df , cols=-c(id), names_to="item", values_to="resp")

BWSS_web_df$group <- "WebRecruit"
BWSS_IR_df$group <- "InternalRecruit"

BWSS_df <- rbind(BWSS_web_df,BWSS_IR_df)

save(BWSS_df, file="PEMAIW_Qiu_2020_BWSS.Rdata")
write.csv(BWSS_df, "PEMAIW_Qiu_2020_BWSS.csv", row.names=FALSE)

SWLS_web_df <- data_web_df |>
  select(starts_with("SWLS"), id)
SWLS_web_df <- remove_na(SWLS_web_df)
SWLS_web_df <- pivot_longer(SWLS_web_df, cols=-c(id), names_to="item", values_to="resp")

SWLS_IR_df <- data_IR_df |>
  select(starts_with("SWLS"), id)
SWLS_IR_df <- remove_na(SWLS_IR_df)
SWLS_IR_df <- pivot_longer(SWLS_IR_df , cols=-c(id), names_to="item", values_to="resp")

SWLS_web_df $group <- "WebRecruit"
SWLS_IR_df $group <- "InternalRecruit"

SWLS_df <- rbind(SWLS_web_df,SWLS_IR_df)

save(SWLS_df, file="PEMAIW_Qiu_2020_SWLS.Rdata")
write.csv(SWLS_df, "PEMAIW_Qiu_2020_SWLS.csv", row.names=FALSE)