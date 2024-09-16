# Paper:
# Data: https://osf.io/mwszy/
library(dplyr)
library(tidyr)
library(haven)

# Remove participants whose responses are all NAs
remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) == "id")])) == (ncol(df) - 1)), ]
  return(df)
}

# ------ Process Autism-Spectrum Quotient Scale Dataset ------ 
aq_df <- read.csv("./aqALL.csv")
aq_columns <- grep("^aq([1-9]|[1-4][0-9]|50)cont$", names(aq_df), value = TRUE)
aq_columns <- append(aq_columns, "ID")
aq_df <- aq_df[, aq_columns] # Select only detailed responses.

aq_df <- aq_df %>% rename(id=ID)
aq_df <- remove_na(aq_df)
aq_df <- pivot_longer(aq_df, cols=-id, names_to="item", values_to = "resp")

attach_df <- read.csv("./attachmentAGING.csv")
attach_df <- attach_df |>
  select(-ends_with("reversed"), -X, -ends_with("scale")) |>
  rename(id=ID)
attach_df <- remove_na(attach_df)
attach_df <- pivot_longer(attach_df, cols=-id, names_to="item", values_to = "resp")

aq_df <- rbind(aq_df, attach_df)

save(aq_df, file="AASDR_Lodi-Smith_2021_AQ.Rdata")
write.csv(aq_df, "AASDR_Lodi-Smith_2021_AQ.csv", row.names=FALSE)

# ------ Process Alexithymia Dataset ------ 
alex_df <- read.csv("./alexithymiaAGING.csv")
alex_df <- alex_df |>
  select(-X, -alexmean) |>
  rename(id=ID)
alex_df <- pivot_longer(alex_df, cols=-id, names_to="item", values_to="resp")

save(alex_df, file="AASDR_Lodi-Smith_2021_Alexithymia.Rdata")
write.csv(alex_df, "AASDR_Lodi-Smith_2021_Alexithymia.csv", row.names=FALSE)

# ------ Process Big Five Inventory-2 Dataset ------
bfi2_df <- read.csv("./traitsAGING.csv")
bfi2_df <- bfi2_df |>
  select(-X, -starts_with("autism"), -ends_with("r"), -C, -A, -E, -O, -ES) |>
  rename(id=ID)
bfi2_df <- remove_na(bfi2_df)
bfi2_df <- pivot_longer(bfi2_df, cols=-id, names_to="item", values_to="resp")

save(bfi2_df, file="AASDR_Lodi-Smith_2021_BFI2.Rdata")
write.csv(bfi2_df, "AASDR_Lodi-Smith_2021_BFI2.csv", row.names=FALSE)

# ------ Process BRFSS Dataset ------
brfss_df <- read.csv("./brfssAGING.csv")
brfss_df <- brfss_df |>
  select(-X)

# ------ Process Clinical Personality Survey Dataset ------ 
cps_df <- read.csv("./clinicalpersonalityAGING.csv")
cps_df <- cps_df |>
  select(ID, starts_with("pid")) |>
  rename(id=ID)
cps_df <- remove_na(cps_df)
cps_df <- pivot_longer(cps_df, cols=-id, names_to="item", values_to="resp")

save(cps_df, file="AASDR_Lodi-Smith_2021_CPS.Rdata")
write.csv(cps_df, "AASDR_Lodi-Smith_2021_CPS.csv", row.names=FALSE)

# ------ Process Dark Triad Dataset ------
dt_df <- read.csv("./darktraidALL.csv")
dt_df <- dt_df |>
  select(ID, starts_with("s")) |>
  rename(id=ID)
dt_df <- remove_na(dt_df)
dt_df <- pivot_longer(dt_df, cols=-id, names_to="item", values_to="resp")

save(dt_df, file="AASDR_Lodi-Smith_2021_DT.Rdata")
write.csv(dt_df, "AASDR_Lodi-Smith_2021_DT.csv", row.names=FALSE)

# ------ Process Desired Trait Change(TIPI) ------
tipi_df <- read.csv("./tipichangeALL.csv")
tipi_df <- tipi_df |>
  select(-X, -ends_with("change")) |>
  rename(id=ID)
tipi_df[ , -which(names(tipi_df) == "id")] <- tipi_df[ , -which(names(tipi_df) == "id")] + 3
tipi_df <- remove_na(tipi_df)
tipi_df <- pivot_longer(tipi_df, cols=-id, names_to="item", values_to="resp")

save(tipi_df, file="AASDR_Lodi-Smith_2021_TIPI.Rdata")
write.csv(tipi_df, "AASDR_Lodi-Smith_2021_TIPI.csv", row.names=FALSE)

# ------ Process Goals Dataset ------
goals_df <- read.csv("goalsAll.csv")
goals_df <- goals_df |>
  select(-X) |>
  rename(id=ID)
goals_df <- remove_na(goals_df)
goals_df <- pivot_longer(goals_df, cols=-id, names_to="item", values_to="resp")

save(goals_df, file="AASDR_Lodi-Smith_2021_Goals.Rdata")
write.csv(goals_df, "AASDR_Lodi-Smith_2021_Goals.csv", row.names=FALSE)

# ------ Process Grit Dataset ------
grit_df <- read.csv("gritAGING.csv")
grit_df <- grit_df[ , c("ID", paste0("grit", 1:8))]
grit_df <- grit_df |>
  rename(id=ID)
grit_df <- remove_na(grit_df)
grit_df <- pivot_longer(grit_df, cols=-id, names_to="item", values_to="resp")

save(grit_df, file="AASDR_Lodi-Smith_2021_Grit.Rdata")
write.csv(grit_df, "AASDR_Lodi-Smith_2021_Grit.csv", row.names=FALSE)

# ------ Process Loneliness Dataset ------
loneliness_df <- read.csv("./lonelinessAGING.csv")
loneliness_df <- loneliness_df[, c("ID", paste0("loneliness", 1:3))]
loneliness_df <- loneliness_df |>
  rename(id=ID)
loneliness_df <- remove_na(loneliness_df)
loneliness_df <- pivot_longer(loneliness_df, cols=-id, names_to="item", values_to="resp")

save(loneliness_df, file="AASDR_Lodi-Smith_2021_Loneliness.Rdata")
write.csv(loneliness_df, "AASDR_Lodi-Smith_2021_Loneliness.csv", row.names=FALSE)

# ------ Process PROMIS Dataset ------
promis_df <- read.csv("./promisAGING.csv")
promis_df <- promis_df |>
  select(ID, starts_with("promis29")) |>
  rename(id=ID)
promis_df <- remove_na(promis_df)
promis_df <- pivot_longer(promis_df, cols=-id, names_to="item", values_to="resp")

save(promis_df, file="AASDR_Lodi-Smith_2021_PROMIS.Rdata")
write.csv(promis_df, "AASDR_Lodi-Smith_2021_PROMIS.csv", row.names=FALSE)

# ------ Process Ryff Dataset ------ 
ryff_df <- read.csv("./pwbAGING.csv")
ryff_cols <- c(2, grep("[0-9]$", names(ryff_df)))
ryff_df <- ryff_df[ , ryff_cols]
ryff_df <- ryff_df |>
  rename(id=ID)
ryff_df <- remove_na(ryff_df)
ryff_df <- pivot_longer(ryff_df, cols=-id, names_to="item", values_to="resp")

save(ryff_df, file="AASDR_Lodi-Smith_2021_RYFF.Rdata")
write.csv(ryff_df, "AASDR_Lodi-Smith_2021_RYFF.csv", row.names=FALSE)

# ------ Process Purpose Dataset ------
purpose_df <- read.csv("./purposeALL.csv")
purpose_df <- purpose_df[, c("ID", paste0("spm", 1:6))]
purpose_df <- purpose_df |>
  rename(id=ID)
purpose_df <- remove_na(purpose_df)
purpose_df <- pivot_longer(purpose_df, cols=-id, names_to="item", values_to="resp")

save(purpose_df, file="AASDR_Lodi-Smith_2021_Purpose.Rdata")
write.csv(purpose_df, "AASDR_Lodi-Smith_2021_Purpose.csv", row.names=FALSE)

# ------ Process Resillience Dataset ------
resillience_df <- read.csv("resilienceAGING.csv")
resillience_df <- resillience_df[, c("ID", paste0("brs_", 1:6))]
resillience_df <- resillience_df |>
  rename(id=ID)
resillience_df <- remove_na(resillience_df)
resillience_df <- pivot_longer(resillience_df, cols=-id, names_to="item", values_to="resp")

save(resillience_df, file="AASDR_Lodi-Smith_2021_Resillience.Rdata")
write.csv(resillience_df, "AASDR_Lodi-Smith_2021_Resillience.csv", row.names=FALSE)

# ------ Process Satisfaction with Life Dataset ------
swls_df <- read.csv("swlsAGING.csv")
swls_df <- swls_df[, c("ID", paste0("swls", 1:5))]
swls_df <- swls_df |>
  rename(id=ID)
swls_df <- remove_na(swls_df)
swls_df <- pivot_longer(swls_df, cols=-id, names_to="item", values_to="resp")

save(swls_df, file="AASDR_Lodi-Smith_2021_SWLS.Rdata")
write.csv(swls_df, "AASDR_Lodi-Smith_2021_SWLS.csv", row.names=FALSE)

# ------ Process Self-concept Clarity Dataset ------
scc_df <- read.csv("sccALL.csv")
scc_df <- scc_df[, c("ID", paste0("scc", 1:12))]
scc_df <- scc_df |>
  rename(id=ID)
scc_df <- remove_na(scc_df)
scc_df <- pivot_longer(scc_df, cols=-id, names_to="item", values_to="resp")

save(scc_df, file="AASDR_Lodi-Smith_2021_SCC.Rdata")
write.csv(scc_df, "AASDR_Lodi-Smith_2021_SCC.csv", row.names=FALSE)

# ------ Process Self-Esteem Dataset ------
rse_df <- read.csv("selfesteemALL.csv")
rse_df <- rse_df |>
  select(-X, -rsesmean) |>
  rename(id=ID)
rse_df <- remove_na(rse_df)
rse_df <- pivot_longer(rse_df, cols=-id, names_to="item", values_to="resp")

save(rse_df, file="AASDR_Lodi-Smith_2021_RSE.Rdata")
write.csv(rse_df, "AASDR_Lodi-Smith_2021_RSE.csv", row.names=FALSE)

# ------ Process Social Camouflage Dataset ------
catq_df <- read.csv("./camouflageAGING.csv")
catq_df <- catq_df[, c("ID", paste0("catq", 1:25))]
catq_df <- catq_df |>
  rename(id=ID)
catq_df <- remove_na(catq_df)
catq_df <- pivot_longer(catq_df, cols=-id, names_to="item", values_to="resp")

save(catq_df, file="AASDR_Lodi-Smith_2021_CATQ.Rdata")
write.csv(catq_df, "AASDR_Lodi-Smith_2021_CATQ.csv", row.names=FALSE)

# ------ Process Social Investment Dataset ------
worksi_df <- read.csv("socialinvestmentAGING.csv")
worksi_df <- worksi_df |>
  select(-X, -ends_with("mean")) |>
  rename(id=ID)
worksi_df <- remove_na(worksi_df)
worksi_df <- pivot_longer(worksi_df, cols=-id, names_to="item", values_to="resp")

save(worksi_df, file="AASDR_Lodi-Smith_2021_SI.Rdata")
write.csv(worksi_df, "AASDR_Lodi-Smith_2021_SI.csv", row.names=FALSE)
