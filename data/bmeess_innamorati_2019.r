# Paper: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0216164
# Data: https://osf.io/9tkqh/files/osfstorage
library(readxl)
library(dplyr)
library(tidyr)

study1_df <- read_excel("PsychomData_Study1_Study2.xlsx", sheet = "Study 1")
study2_df <- read_excel("PsychomData_Study1_Study2.xlsx", sheet = "Study 2")
study1_df <- study1_df %>% mutate(across(everything(), ~ ifelse(. == 999, NA, .)))
study2_df <- study2_df %>% mutate(across(everything(), ~ ifelse(. == 999, NA, .)))

# ---------- Process EES 75 ----------
ees75_df <- study1_df
ees75_df <- ees75_df %>% mutate(id = row_number())
ees75_df <- ees75_df |>
  rename(cov_age=Age, cov_sex=Sex, cov_marital=Marital, cov_school=School, cov_job=Job)
ees75_df <- pivot_longer(ees75_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

save(ees75_df, file="bmeess_innamorati_2019_ees75.Rdata")
write.csv(ees75_df, "bmeess_innamorati_2019_ees75.csv", row.names=FALSE)

# ---------- Pre-process Study2 Data ---------
study2_df <- study2_df |>
  rename(cov_age=Age, cov_sex=Sex, cov_school=School,cov_job=Job)
study2_df <- study2_df |> mutate(id=row_number())

# ---------- Process EES 30 ----------
ees30_df <- study2_df |>
  select(id, starts_with("cov"), starts_with("EES"))
ees30_df <- pivot_longer(ees30_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

save(ees30_df, file="bmeess_innamorati_2019_ees30.Rdata")
write.csv(ees30_df, "bmeess_innamorati_2019_ees30.csv", row.names=FALSE)

# ---------- Process MC 30 ----------
mc_df <- study2_df |>
  select(id, starts_with("cov"), starts_with("MC"))
mc_df <- pivot_longer(mc_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

save(mc_df, file="bmeess_innamorati_2019_mc.Rdata")
write.csv(mc_df, "bmeess_innamorati_2019_mc.csv", row.names=FALSE)

# ---------- Process BEES ----------
bees_df <- study2_df |>
  select(id, starts_with("cov"), starts_with("BEES"))
bees_df <- pivot_longer(bees_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

save(bees_df, file="bmeess_innamorati_2019_bees.Rdata")
write.csv(bees_df, "bmeess_innamorati_2019_bees.csv", row.names=FALSE)

# ---------- Process IRI ----------
iri_df <- study2_df |>
  select(id, starts_with("cov"), starts_with("IRI"))
iri_df <- pivot_longer(iri_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

save(iri_df, file="bmeess_innamorati_2019_iri.Rdata")
write.csv(iri_df, "bmeess_innamorati_2019_iri.csv", row.names=FALSE)

# ---------- Process TDI ----------
tdi_df <- study2_df |>
  select(id, starts_with("cov"), starts_with("TDI"))
tdi_df <- pivot_longer(tdi_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

save(tdi_df, file="bmeess_innamorati_2019_tdi.Rdata")
write.csv(tdi_df, "bmeess_innamorati_2019_tdi.csv", row.names=FALSE)