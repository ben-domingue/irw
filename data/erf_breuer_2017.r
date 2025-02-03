# Paper: https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2020.00015/full
# Data: https://osf.io/5ru9q/
library(haven)
library(dplyr)
library(tidyr)

df <- read_sav("Data_Effects of Response Format.sav")

df <- df |>
  rename(id=nr, cov_gender=gender, cov_age=age)

# ---------- Process TAI Scale ----------
TAI_df <- df |>
  select(id, starts_with("cov"), starts_with("TAI"), -tai_total, -ends_with("MEAN"), -starts_with("TAI_"))
TAI_df <- pivot_longer(TAI_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

save(TAI_df, file="erf_breuer_2017_tai.Rdata")
write.csv(TAI_df, "erf_breuer_2017_tai.csv", row.names=FALSE)
# ---------- Process FRM_FR Scale ----------
FRMFR_df <- df |>
  select(id, starts_with("cov"), starts_with("FRM_FR"))
FRMFR_df <- pivot_longer(FRMFR_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

save(FRMFR_df, file="erf_breuer_2017_frmfr.Rdata")
write.csv(FRMFR_df, "erf_breuer_2017_frmfr.csv", row.names=FALSE)
# ---------- Process FRM_MC Scale ----------
FRMMC_df <- df |>
  select(id, starts_with("cov"), starts_with("FRM_MC"))
FRMMC_df <- pivot_longer(FRMMC_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

save(FRMMC_df, file="erf_breuer_2017_frmmc.Rdata")
write.csv(FRMMC_df, "erf_breuer_2017_frmmc.csv", row.names=FALSE)
# ---------- Process DOSP Scale ----------
DOSP_df <- df |>
  select(id, starts_with("cov"), starts_with("DOSP"), -dosp_total, -DOSP_GES)
DOSP_df <- pivot_longer(DOSP_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

save(DOSP_df, file="erf_breuer_2017_dosp.Rdata")
write.csv(DOSP_df, "erf_breuer_2017_dosp.csv", row.names=FALSE)