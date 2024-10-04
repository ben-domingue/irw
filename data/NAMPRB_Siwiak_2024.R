# Paper: https://www.researchgate.net/profile/Klara-Buczel/publication/380193423_New_Age_of_measuring_paranormal_and_related_beliefs_Psychometric_properties_and_correlates_of_the_Polish_version_of_the_Survey_of_Scientifically_Unaccepted_Beliefs_SSUB/links/6630f38506ea3d0b7419c08d/New-Age-of-measuring-paranormal-and-related-beliefs-Psychometric-properties-and-correlates-of-the-Polish-version-of-the-Survey-of-Scientifically-Unaccepted-Beliefs-SSUB.pdf
# Data: https://osf.io/k2453/
library(dplyr)
library(tidyr)
library(haven)
library(readxl)

# ------ Helper Function ------
remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) == "id")])) == (ncol(df) - 1)), ]
  return(df)
}

df <- read_excel("data_SSUB-PL_adaptation.xlsx")
df <- df |>
  rename(id=Participant, sample=Sample) |>
  select(-Gender, -Age, -Education)

# ------ Process SSUB Dataset ------
ssub_df <- df |>
  select(id, sample, starts_with("SSUB"), -ends_with("mean"))
retest_ssub_df <- ssub_df[ssub_df$sample == 5, c("id", "sample", paste0("SSUB_RETEST_", 1:20))]

colnames(retest_ssub_df) <- gsub("RETEST", "NAB", colnames(retest_ssub_df)) # Rename retest as they are the same questions as wave 1
retest_ssub_df <- pivot_longer(retest_ssub_df, cols=-c("id", "sample"), names_to="item", values_to="resp")
retest_ssub_df$wave <- 1

ssub_df <- ssub_df |>
  select(-starts_with("SSUB_RETEST"))
#ssub_df$wave <- ifelse(ssub_df$sample == 5, 0, 0)
ssub_df$wave <- 0
ssub_df <- pivot_longer(ssub_df, cols=-c("id", "sample", "wave"), names_to="item", values_to="resp")

ssub_df <- rbind(ssub_df, retest_ssub_df)
ssub_df <- ssub_df |>
  select(-sample)

save(ssub_df, file="NAMPRB_Siwiak_2024_SSUB.Rdata")
write.csv(ssub_df, "NAMPRB_Siwiak_2024_SSUB.csv", row.names=FALSE)

# ------ Process GCBS Dataset ------
gcbs_df <- df |>
  select(id, starts_with("GCBS"), -ends_with("mean"))
gcbs_df <- remove_na(gcbs_df)
gcbs_df <- pivot_longer(gcbs_df, cols=-c("id"), names_to="item", values_to="resp")

save(gcbs_df, file="NAMPRB_Siwiak_2024_GCBS.Rdata")
write.csv(gcbs_df, "NAMPRB_Siwiak_2024_GCBS.csv", row.names=FALSE)

#  ------ Process NEO-FFI Dataset ------
neoffi_df <- df |>
  select(id, starts_with("NEO_FFI"))
neoffi_df <- remove_na(neoffi_df)
neoffi_df <- pivot_longer(neoffi_df, cols=-id, names_to="item", values_to="resp")

save(neoffi_df, file="NAMPRB_Siwiak_2024_NEOFFI.Rdata")
write.csv(neoffi_df, "NAMPRB_Siwiak_2024_NEOFFI.csv", row.names=FALSE)

# ------ Process DES-R-PL Dataset ------
desrpl_df <- df |>
  select(id, starts_with("DES"), -ends_with("sum"))
desrpl_df <- remove_na(desrpl_df)
desrpl_df <- pivot_longer(desrpl_df, cols=-id, names_to="item", values_to="resp")
desrpl_df <- desrpl_df %>%
  mutate(resp = ifelse(resp == 8, NA, resp))

save(desrpl_df, file="NAMPRB_Siwiak_2024_DESRPL.Rdata")
write.csv(desrpl_df, "NAMPRB_Siwiak_2024_DESRPL.csv", row.names=FALSE)

# ------ Process Kon-2066 Dataset ------
kon2066_df <- df |>
  select(id, starts_with("KON"), -ends_with("sum"))
kon2066_df <- remove_na(kon2066_df)
kon2066_df <- pivot_longer(kon2066_df, cols=-id, names_to="item", values_to="resp")

save(kon2066_df, file="NAMPRB_Siwiak_2024_KON2066.Rdata")
write.csv(kon2066_df, "NAMPRB_Siwiak_2024_KON2066.csv", row.names=FALSE)

# ------ Process BSR10 Dataset ------
bsr_df <- df |>
  select(id, starts_with("BSR"), -ends_with("mean"))
bsr_df <- remove_na(bsr_df)
bsr_df <- pivot_longer(bsr_df, cols=-id, names_to="item", values_to="resp")

save(bsr_df, file="NAMPRB_Siwiak_2024_BSR10.Rdata")
write.csv(bsr_df, "NAMPRB_Siwiak_2024_BSR10.csv", row.names=FALSE)

# ------ Process KOP20 Dataset ------
kop_df <- df |>
  select(id, starts_with("KOP"), -ends_with("mean"))
kop_df <- remove_na(kop_df)
kop_df <- pivot_longer(kop_df, cols=-id, names_to="item", values_to="resp")

save(kop_df, file="NAMPRB_Siwiak_2024_KOP20.Rdata")
write.csv(kop_df, "NAMPRB_Siwiak_2024_KOP20.csv", row.names=FALSE)

# ------ Process AOT Dataset ------
aot_df <- df |>
  select(id, starts_with("AOT"), -ends_with("mean"))
aot_df <- remove_na(aot_df)
aot_df <- pivot_longer(aot_df, cols=-id, names_to="item", values_to="resp")

save(aot_df, file="NAMPRB_Siwiak_2024_AOT.Rdata")
write.csv(aot_df, "NAMPRB_Siwiak_2024_AOT.csv", row.names=FALSE)