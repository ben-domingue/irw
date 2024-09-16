# Paper: https://onlinelibrary.wiley.com/doi/full/10.1002/ab.22145?saml_referrer
# Data: https://osf.io/bskn9/
library(dplyr)
library(tidyr)
library(haven)

# Remove participants whose responses are all NAs
remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) == "id")])) == (ncol(df) - 1)), ]
  return(df)
}

df <- read.csv("BPAQ CFA dataset final_RMH.csv")
# ------ Process BPAQSF Dataset ------ 
bpaqsf_df <- df |>
  select(id, starts_with("bpaqsf"), -bpaqsf_aggTotal_b, 
         -bpaqsf_physAgg_b, -bpaqsf_verbAgg_b, -bpaqsf_anger_b,
         -bpaqsf_hostility_b, -bpaqsf_aggTotal_p, -bpaqsf_physAgg_p,
         -bpaqsf_verbAgg_p, -bpaqsf_anger_p, -bpaqsf_hostility_p, group)

bpaqsf_df$treat <- ifelse(bpaqsf_df$group %in% c(2, 3), 1, ifelse(bpaqsf_df$group == 1, 0, NA))
base_bpaqsf_df <- bpaqsf_df |>
  select(id, ends_with("b"), group, treat)
treat_bpaqsf_df <- bpaqsf_df |>
  select(id, ends_with("p"), group, treat)
names(base_bpaqsf_df) <- gsub("_b$", "", names(base_bpaqsf_df))
names(treat_bpaqsf_df) <- gsub("_p$", "", names(treat_bpaqsf_df))

treat_bpaqsf_df <- pivot_longer(treat_bpaqsf_df, cols=-c(id, group, treat), names_to="item", values_to="resp")
base_bpaqsf_df <- pivot_longer(base_bpaqsf_df, cols=-c(id, group, treat), names_to="item", values_to="resp")

treat_bpaqsf_df$wave <- 0
base_bpaqsf_df$wave <- 1
bpaqsf_df <- rbind(treat_bpaqsf_df, base_bpaqsf_df)

save(bpaqsf_df, file="BPAQ_Christopher_2024_BPAQSF.Rdata")
write.csv(bpaqsf_df, "BPAQ_Christopher_2024_BPAQSF.csv", row.names=FALSE)
# ------ Process PROMIS Dataset ------ 
promis_df <- df |>
  select(id, starts_with("promis"), -promis_sleep1r_b, -promis_sleep2r_b, -promis_alcScreen_b)
promis_df<- promis_df[, !grepl("score", names(promis_df), ignore.case = TRUE)]
promis_df <- remove_na(promis_df)
promis_df <- pivot_longer(promis_df, cols=-id, names_to="item", values_to="resp")

save(promis_df, file="BPAQ_Christopher_2024_PROMIS.Rdata")
write.csv(promis_df, "BPAQ_Christopher_2024_PROMIS.csv", row.names=FALSE)
# ------ Process PCL-5 Dataset ------
pcl5_df <- df |>
  select(id, starts_with("pcl"), -pcl5_ptsd_b)
pcl5_df <- remove_na(pcl5_df)
pcl5_df <- pivot_longer(pcl5_df, cols=-id, names_to="item", values_to="resp")

save(pcl5_df, file="BPAQ_Christopher_2024_PCL5.Rdata")
write.csv(pcl5_df, "BPAQ_Christopher_2024_PCL5.csv", row.names=FALSE)
# ------ Process PSS-10 Dataset ------
pss10_df <- df |>
  select(id, starts_with("pss"), -ends_with("r_b"), -pss_stress_b)
pss10_df <- remove_na(pss10_df)
pss10_df <- pivot_longer(pss10_df, cols=-id, names_to="item", values_to="resp")

save(pss10_df, file="BPAQ_Christopher_2024_PSS10.Rdata")
write.csv(pss10_df, "BPAQ_Christopher_2024_PSS10.csv", row.names=FALSE)
# ------ Process OLBI Dataset ------
obi_df <- df |>
  select(id, starts_with("obi"), -ends_with("r_b"), -obi_burnout_b)
obi_df <- remove_na(obi_df)
obi_df <- pivot_longer(obi_df, cols=-id, names_to="item", values_to="resp")

save(obi_df, file="BPAQ_Christopher_2024_OBSI.Rdata")
write.csv(obi_df, "BPAQ_Christopher_2024_OBSI.csv", row.names=FALSE)
# ------ Process SCS-SF Dataset ------
scssf_df <- df |>
  select(id, starts_with("scssf"), -ends_with("r_b"), -scssf_selfComp_b)
scssf_df <- remove_na(scssf_df)
scssf_df <- pivot_longer(scssf_df, cols=-id, names_to="item", values_to="resp")

save(scssf_df, file="BPAQ_Christopher_2024_SCSS.Rdata")
write.csv(scssf_df, "BPAQ_Christopher_2024_SCSS.csv", row.names=FALSE)
# ------ Process FFMQ-F Dataset ------
ffmqsf_df <- df |>
  select(id, starts_with("ffmqsf"), -ends_with("r_b"), -ffmqsf_mindfulness_b)
ffmqsf_df <- remove_na(ffmqsf_df)
ffmqsf_df <- pivot_longer(ffmqsf_df, cols=-id, names_to="item", values_to="resp")

save(ffmqsf_df, file="BPAQ_Christopher_2024_FFMQSF.Rdata")
write.csv(ffmqsf_df, "BPAQ_Christopher_2024_FFMQSF.csv", row.names=FALSE)
