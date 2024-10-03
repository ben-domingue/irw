# Paper: https://osf.io/preprints/psyarxiv/mcwsg
# Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/F3KS7M
library(haven)
library(dplyr)
library(tidyr)
library(readxl)

scale_to_7 <- function(x) {
  return(round(1 + (x / 10) * 6))
}

study2_df_path <- "./Dataset/Study2/Study2Data.sav"
study2_df <- read_sav(study2_df_path)

study3_df_path <- "./Dataset/Study3/DataStudy_3.sav"
study3_df <- read_sav(study3_df_path)

# ------ Process Study 2 Dataset ------
study2_df[] <- lapply(study2_df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})
study2_df <- study2_df |>
  select(-Usia, -JK, -Universitas, -Angkatan, -Email, -PSRP, -PPSR, -PSIP) |>
  rename(id=Nama, figure=Tokoh)

study2_psr_df <- study2_df |>
  select(id, figure, starts_with("a"))
study2_ppsr_df <- study2_df |>
  select(id, figure, starts_with("b"))
study2_psi_df <- study2_df |>
  select(id, figure, starts_with("c"))

study2_psr_df <- pivot_longer(study2_psr_df, cols=-c(id, figure), names_to="item", values_to="resp")
study2_ppsr_df <- pivot_longer(study2_ppsr_df, cols=-c(id, figure), names_to="item", values_to="resp")
study2_psi_df <- pivot_longer(study2_psi_df, cols=-c(id, figure), names_to="item", values_to="resp")

save(study2_psr_df, file="PSR-P_Scale_Intimacy_Hakim_2018_Study2_PSR.Rdata")
write.csv(study2_psr_df, "PSR-P_Scale_Intimacy_Hakim_2018_Study2_PSR.csv", row.names=FALSE)
save(study2_psi_df, file="PSR-P_Scale_Intimacy_Hakim_2018_Study2_PSI.Rdata")
write.csv(study2_psi_df, "PSR-P_Scale_Intimacy_Hakim_2018_Study2_PSI.csv", row.names=FALSE)
save(study2_ppsr_df, file="PSR-P_Scale_Intimacy_Hakim_2018_Study2_PPSR.Rdata")
write.csv(study2_ppsr_df, "PSR-P_Scale_Intimacy_Hakim_2018_Study2_PPSR.csv", row.names=FALSE)

# ------ Process Study 3 Dataset ------
study3_df[] <- lapply(study3_df, function(col){
  attr(col, "label") <- NULL
  return(col)
})
study3_df <- study3_df |>
  select(-Age, -Favpol, -RWA, -BA, -IDEO, -ELAB, -PolEff, 
         -PSRP, -Country, -Gender) |>
  rename(id=ID, figure=PI1)
study3_df$figure <- tolower(study3_df$figure)

study3_lib_df <- study3_df |>
  select(id, figure, starts_with("Lib"))
study3_df <- study3_df |>
  select(-starts_with("Lib"))

study3_lib_df[] <- lapply(study3_lib_df, function(column) {
  if (is.numeric(column) && !identical(column, study3_lib_df$id)) {
    scale_to_7(column)
  } else {
    column  # Return 'id' or non-numeric columns unchanged
  }
})

study3_lib_df <- pivot_longer(study3_lib_df, cols=-c(id, figure), names_to="item", values_to="resp")
study3_df <- pivot_longer(study3_df, cols=-c(id, figure), names_to="item", values_to="resp")
study3_df <- rbind(study3_df, study3_lib_df)

save(study3_df, file="PSR-P_Scale_Intimacy_Hakim_2018_Study3.Rdata")
write.csv(study3_df, "PSR-P_Scale_Intimacy_Hakim_2018_Study3.csv", row.names=FALSE)
