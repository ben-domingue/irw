# Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/G4E2SR
# Paper: 
library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)
library(readr)
library(readxl)
library(sas7bdat)

rm(list =ls()) 
remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) - 1)), ]
  return(df)
}

update_df_by_id <- function(df1, df2) {
  # Iterate over each row in df1
  for (i in 1:nrow(df1)) {
    row_id <- df1$ID[i]  # Extract the ID
    values_to_assign <- df1[i, -1]  # Exclude the ID column
    
    # Assign values to df2 where IDs match
    df2[df2$ID == row_id, names(values_to_assign)] <- values_to_assign
  }
  
  return(df2)  # Return the updated dataframe
}


BC_daily_df <- read.sas7bdat("promis_ecolval_bc_daily.sas7bdat")
BC_demos_df <- read.sas7bdat("promis_ecolval_bc_demos.sas7bdat")
CS_daily_df <- read.sas7bdat("promis_ecolval_cs_daily.sas7bdat")
CS_demos_df <- read.sas7bdat("promis_ecolval_cs_demos.sas7bdat")
HS_daily_df <- read.sas7bdat("promis_ecolval_hs_daily.sas7bdat")
HS_demos_df<- read.sas7bdat("promis_ecolval_hs_demos.sas7bdat")
OA_daily_df <- read.sas7bdat("promis_ecolval_oa_daily.sas7bdat")
OA_demos_df<- read.sas7bdat("promis_ecolval_oa_demos.sas7bdat")
pms_daily_df <- read.sas7bdat("promis_ecolval_pms_daily.sas7bdat")
pms_demos_df<- read.sas7bdat("promis_ecolval_pms_demos.sas7bdat")

# ---------------------------------------- BC Data ----------------------------------------
# -------- BC Demographic  --------
BC_SOCIO_df <- BC_demos_df %>%
  select(ID, starts_with("SOCIO"))
BC_SOCIO_df  <- remove_na(BC_SOCIO_df)
BC_SOCIO_df <- BC_SOCIO_df |>
  rename(cov_age=SOCIO02, cov_gender=SOCIO03, cov_marital=SOCIO06, cov_if_lat=SOCIO04)

BC_daily_df <- update_df_by_id(BC_SOCIO_df, BC_daily_df)
BC_daily_df <- BC_daily_df |>
  rename(id=ID, wave=DAY)
# -------- Daily - BC Anxiety Scale --------
BC_DDEDANX_df <- BC_daily_df %>%
  select(id, wave,starts_with("cov"), starts_with("DDEDANX"),-(DDEDANXSE),-(DDEDANXTS))
BC_DDEDANX_df  <- remove_na(BC_DDEDANX_df)
BC_DDEDANX_df <- pivot_longer(BC_DDEDANX_df, cols=-c(id, wave, starts_with("cov")), names_to="item", values_to="resp")

# -------- Daily - BC Depression Scale --------
BC_DDEDDEP_df <- BC_daily_df %>%
  select(id, wave, starts_with("cov"), starts_with("DDEDDEP"),-(DDEDDEPSE),-(DDEDDEPTS))
BC_DDEDDEP_df  <- remove_na(BC_DDEDDEP_df)
BC_DDEDDEP_df <- pivot_longer(BC_DDEDDEP_df, cols=-c(id, wave, starts_with("cov")), names_to="item", values_to="resp")

# -------- Daily - BC Fatigue Scale --------
BC_DDFATEXP_df <- BC_daily_df %>%
  select(id, wave, starts_with("cov"), starts_with("DDFATEXP"))
BC_DDFATEXP_df  <- remove_na(BC_DDFATEXP_df)
BC_DDFATEXP_df <- pivot_longer(BC_DDFATEXP_df, cols=-c(id, wave, starts_with("cov")), names_to="item", values_to="resp")

#  -------- BC Global Health --------
BC_demos_df <- update_df_by_id(BC_SOCIO_df, BC_demos_df)
BC_demos_df <- BC_demos_df |>
  rename(id=ID)

BC_Global_df <- BC_demos_df %>%
  select(id, starts_with("cov"), starts_with("Global"))
BC_Global_df  <- remove_na(BC_Global_df)
BC_Global_df <- pivot_longer(BC_Global_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

#  -------- BC cdiag Health --------
BC_cdiag_df <- BC_demos_df %>%
  select(id, starts_with("cov"), starts_with("cdiag"))
BC_cdiag_df  <- remove_na(BC_cdiag_df)
BC_cdiag_df <- pivot_longer(BC_cdiag_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

# ---------------------------------------- CS Data ----------------------------------------
CS_demos_df <- CS_demos_df |>
  rename(id=ID, cov_race=RACE, cov_education=EDUCATION, cov_income=INCOME, cov_employed=EMPLOYED, cov_benefits=BENEFITS,
         cov_age=SOCIO02, cov_gender=SOCIO03, cov_marital=SOCIO06, cov_if_lat=SOCIO04) 

CS_Global_df <- CS_demos_df %>%
  select(id, starts_with("Global"), starts_with("cov"))
CS_Global_df  <- remove_na(CS_Global_df)
CS_Global_df <- pivot_longer(CS_Global_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

CS_cdiag_df <- CS_demos_df %>%
  select(id, starts_with("cov"), starts_with("cdiag"))
CS_cdiag_df  <- remove_na(CS_cdiag_df)
CS_cdiag_df <- pivot_longer(CS_cdiag_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

CS_demos_df <- CS_demos_df |>
  select(id, starts_with("cov"))
CS_daily_df <- update_df_by_id(CS_demos_df, CS_daily_df)
CS_daily_df <- CS_daily_df |>
  rename(id=ID, wave=DAY)

CS_DDEDDEP_df <- CS_daily_df %>%
  select(id, wave, starts_with("cov"), starts_with("DDEDDEP"), -("DDEDDEPTS"))
CS_DDEDDEP_df <- remove_na(CS_DDEDDEP_df)
CS_DDEDDEP_df <- pivot_longer(CS_DDEDDEP_df, cols=-c(id, wave, starts_with("cov")), names_to="item", values_to="resp")

CS_DDPAININ_df <- CS_daily_df %>%
  select(id, wave, starts_with("cov"), starts_with("DDPAININ"), -("DDPAININTS"), -("DDPAININSE"))
CS_DDPAININ_df <- remove_na(CS_DDPAININ_df)
CS_DDPAININ_df <- pivot_longer(CS_DDPAININ_df, cols=-c(id, wave, starts_with("cov")), names_to="item", values_to="resp")

# ---------------------------------------- HS Data ----------------------------------------
HS_demos_df <- HS_demos_df %>%
  rename(id=ID, cov_herntype=HERNTYPE, cov_race=RACE, cov_education=EDUCATION, cov_income=INCOME,
         cov_employed=EMPLOYED, cov_benefits=BENEFITS, cov_age=SOCIO02, cov_gender=SOCIO03, cov_marital=SOCIO06, cov_if_lat=SOCIO04)

HS_cdiag_df <- HS_demos_df %>%
  select(id, starts_with("cov"), starts_with("cdiag"))
HS_cdiag_df  <- remove_na(HS_cdiag_df)
HS_cdiag_df <- pivot_longer(HS_cdiag_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

HS_Global_df <- HS_demos_df %>%
  select(id, starts_with("cov"), starts_with("Global"))
HS_Global_df  <- remove_na(HS_Global_df)
HS_Global_df <- pivot_longer(HS_Global_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

HS_demos_df <- HS_demos_df |>
  select(id, starts_with("cov"))
HS_daily_df <- update_df_by_id(HS_demos_df, HS_daily_df)
HS_daily_df <- HS_daily_df |>
  rename(id=ID, wave=DAY)

HS_DDEDANX_df <- HS_daily_df %>%
  select(id,wave, starts_with("cov"), starts_with("DDEDANX"), -(DDEDANXSE),-(DDEDANXTS))
HS_DDEDANX_df <- remove_na(HS_DDEDANX_df)
HS_DDEDANX_df <- pivot_longer(HS_DDEDANX_df, cols=-c(id,wave, starts_with("cov")), names_to="item", values_to="resp")

HS_DDPAINBE_df <- HS_daily_df %>%
  select(id,wave, starts_with("cov"), starts_with("DDPAINBE"), -("DDPAINBETS"), -("DDPAINBESE"))
HS_DDPAINBE_df <- remove_na(HS_DDPAINBE_df)
HS_DDPAINBE_df <- pivot_longer(HS_DDPAINBE_df, cols=-c(id,wave, starts_with("cov")), names_to="item", values_to="resp")

# ---------------------------------------- OA Data ----------------------------------------
OA_demos_df <- OA_demos_df %>%
  rename(id=ID, cov_race=RACE, cov_education=EDUCATION, cov_income=INCOME,
         cov_employed=EMPLOYED, cov_benefits=BENEFITS, cov_age=SOCIO02, cov_gender=SOCIO03, cov_marital=SOCIO06, cov_if_lat=SOCIO04)

OA_cdiag_df <- OA_demos_df %>%
  select(id, starts_with("cov"), starts_with("cdiag"))
OA_cdiag_df  <- remove_na(OA_cdiag_df)
OA_cdiag_df <- pivot_longer(OA_cdiag_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

OA_Global_df <- OA_demos_df %>%
  select(id, starts_with("cov"), starts_with("Global"))
OA_Global_df  <- remove_na(OA_Global_df)
OA_Global_df <- pivot_longer(OA_Global_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

OA_demos_df <- OA_demos_df |>
  select(id, starts_with("cov"))
OA_daily_df <- update_df_by_id(OA_demos_df, OA_daily_df)
OA_daily_df <- OA_daily_df |>
  rename(id=ID, wave=DAY)

OA_DDPF_df <- OA_daily_df %>%
  select(id,wave, starts_with("cov"), starts_with("DDPF"), -("DDPFTS"),-("DDPFSE"))
OA_DDPF_df <- remove_na(OA_DDPF_df)
OA_DDPF_df <- pivot_longer(OA_DDPF_df, cols=-c(id,wave, starts_with("cov")), names_to="item", values_to="resp")

OA_DDPAININ_df <- OA_daily_df %>%
  select(id,wave, starts_with("cov"), starts_with("DDPAININ"), -("DDPAININTS"), -("DDPAININSE"))
OA_DDPAININ_df <- remove_na(OA_DDPAININ_df)
OA_DDPAININ_df <- pivot_longer(OA_DDPAININ_df, cols=-c(id,wave, starts_with("cov")), names_to="item", values_to="resp")

# ---------------------------------------- pms Data ----------------------------------------
pms_demos_df <- pms_demos_df %>%
  rename(id=ID, cov_race=RACE, cov_education=EDUCATION, cov_income=INCOME,
         cov_employed=EMPLOYED, cov_benefits=BENEFITS, cov_age=SOCIO02, cov_gender=SOCIO03, cov_marital=SOCIO06, cov_if_lat=SOCIO04)

pms_cdiag_df <- pms_demos_df %>%
  select(id, starts_with("cov"), starts_with("cdiag"))
pms_cdiag_df  <- remove_na(pms_cdiag_df)
pms_cdiag_df <- pivot_longer(pms_cdiag_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

pms_Global_df <- pms_demos_df %>%
  select(id, starts_with("cov"), starts_with("Global"))
pms_Global_df  <- remove_na(pms_Global_df)
pms_Global_df <- pivot_longer(pms_Global_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

pms_demos_df <- pms_demos_df |>
  select(id, starts_with("cov"))
pms_daily_df <- update_df_by_id(pms_demos_df, pms_daily_df)
pms_daily_df <- pms_daily_df |>
  rename(id=ID, wave=DAY)

pms_DDEDANG_df <- pms_daily_df %>%
  select(id,wave, starts_with("cov"), starts_with("DDEDANG"),-(DDEDANGSE),-(DDEDANGTS))
pms_DDEDANG_df  <- remove_na(pms_DDEDANG_df)
pms_DDEDANG_df <- pivot_longer(pms_DDEDANG_df, cols=-c(id,wave, starts_with("cov")), names_to="item", values_to="resp")

pms_DDEDDEP_df <- pms_daily_df %>%
  select(id,wave, starts_with("cov"), starts_with("DDEDDEP"),-(DDEDDEPSE),-(DDEDDEPTS))
pms_DDEDDEP_df  <- remove_na(pms_DDEDDEP_df)
pms_DDEDDEP_df <- pivot_longer(pms_DDEDDEP_df, cols=-c(id,wave, starts_with("cov")), names_to="item", values_to="resp")

# ---------------------------------------- Post-process ----------------------------------------
library(dplyr)  # Load dplyr for bind_rows()

# Assign group names
BC_Global_df$group <- "BC"
CS_Global_df$group <- "CS"
HS_Global_df$group <- "HS"
OA_Global_df$group <- "OA"
pms_Global_df$group <- "pms"

# Bind data frames, filling missing columns with NA
Global_df <- bind_rows(BC_Global_df, CS_Global_df, HS_Global_df, OA_Global_df, pms_Global_df)

# Save the combined dataset
save(Global_df, file = "evpromisi_stone_2021_global.Rdata")
write.csv(Global_df, "evpromisi_stone_2021_global.csv", row.names = FALSE)

BC_cdiag_df$ group <- "BC"
CS_cdiag_df$ group <- "CS"
HS_cdiag_df$group <- "HS"
OA_cdiag_df $group <- "OA"
pms_cdiag_df$group <- "pms"
cdiag_df <- bind_rows(BC_cdiag_df,CS_cdiag_df,HS_cdiag_df,OA_cdiag_df,pms_cdiag_df)
print(table(cdiag_df$resp))

save(cdiag_df, file="evpromisi_stone_2021_cdiag.Rdata")
write.csv(cdiag_df, "evpromisi_stone_2021_cdiag.csv", row.names=FALSE)

BC_DDEDDEP_df$ group <- "BC"
CS_DDEDDEP_df$ group <- "CS"
pms_DDEDDEP_df$group <- "pms"
DDEDDEP_df <- bind_rows(BC_DDEDDEP_df,CS_DDEDDEP_df,pms_DDEDDEP_df)
DDEDDEP_df <- DDEDDEP_df[DDEDDEP_df$resp %in% c(1, 2, 3, 4, 5), ]
save(DDEDDEP_df, file="evpromisi_stone_2021_ddeddep.Rdata")
write.csv(DDEDDEP_df, "evpromisi_stone_2021_ddeddep.csv", row.names=FALSE)

CS_DDPAININ_df$ group <- "CS"
OA_DDPAININ_df$group <- "OA"
DDPAININ_df <- bind_rows(CS_DDPAININ_df, OA_DDPAININ_df)
save(DDPAININ_df, file="evpromisi_stone_2021_ddpainin.Rdata")
write.csv(DDPAININ_df, "evpromisi_stone_2021_ddpainin.csv", row.names=FALSE)s

BC_DDEDANX_df$ group <- "BC"
HS_DDEDANX_df$group <- "HS"
DDEDANX_df <- bind_rows(BC_DDEDANX_df, HS_DDEDANX_df)
save(DDEDANX_df, file="evpromisi_stone_2021_ddedanx.Rdata")
write.csv(DDEDANX_df, "evpromisi_stone_2021_ddedanx.csv", row.names=FALSE)
