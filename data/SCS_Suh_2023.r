# Data: https://osf.io/wsjkb/
# Paper: https://link.springer.com/article/10.1007/s41811-024-00214-3
library(haven)
library(dplyr)
library(tidyr)

ea_df <- read_sav("SCS EA dataset.sav")
korea_df <- read_sav("SCS Korean dataset.sav")

ea_df <- ea_df |>
  rename(id=ID)
korea_df <- korea_df |>
  rename(id=ID)

# ---------- Process SCS Dataset ----------
ea_scs <- ea_df |>
  select(id, starts_with("SCS"), -starts_with("SCS_Short"))
ea_scs <- pivot_longer(ea_scs, cols=-id, names_to="item", values_to="resp")
ea_scs$group <- "US"

korea_scs <- korea_df |>
  select(id, starts_with("SCS"))
korea_scs <- pivot_longer(korea_scs, cols=-id, names_to="item", values_to="resp")
korea_scs$group <- "Korea"

scs_df <- rbind(ea_scs, korea_scs)

save(scs_df, file="SCS_Suh_2023_SCS.Rdata")
write.csv(scs_df, "SCS_Suh_2023_SCS.csv", row.names=FALSE)

# ---------- Process SIAPS Dataset ----------
ea_siaps <- ea_df |>
  select(id, starts_with("SIAPS"), -ends_with("F2"), -ends_with("F1"))
ea_siaps[ea_siaps == 999] <- NA
ea_siaps <- pivot_longer(ea_siaps, cols=-id, names_to="item", values_to="resp")

save(ea_siaps, file="SCS_Suh_2023_SIAPS.Rdata")
write.csv(ea_siaps, "SCS_Suh_2023_SIAPS.csv", row.names=FALSE)

# ---------- Process BFNE Dataset ----------
ea_bfne <- ea_df |>
  select(id, starts_with("BFNE"), -ends_with("T"))
ea_bfne[ea_bfne == 999] <- NA
ea_bfne <- pivot_longer(ea_bfne, cols=-id, names_to="item", values_to="resp")
ea_bfne <- ea_bfne[!is.na(ea_bfne$resp),]
ea_bfne$group <- "US"

korea_bfne <- korea_df |>
  select(id, starts_with("BFNE"), -BFNE)
korea_bfne[korea_bfne == 999] <- NA
korea_bfne[korea_bfne == 0] <- NA
korea_bfne <- pivot_longer(korea_bfne, cols=-id, names_to="item", values_to="resp")
korea_bfne <- korea_bfne[!is.na(korea_bfne$resp),]
korea_bfne$group <- "Korea"

bfne_df <- rbind(korea_bfne, ea_bfne)

save(bfne_df, file="SCS_Suh_2023_BFNE.Rdata")
write.csv(bfne_df, "SCS_Suh_2023_BFNE.csv", row.names=FALSE)