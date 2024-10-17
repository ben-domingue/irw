# Paper:https://pubmed.ncbi.nlm.nih.gov/38311907/
# Data: https://osf.io/f7rp3/

library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)
library(readr)
library(readxl)
library(sas7bdat)

rm(list =ls()) 
remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id", "date"))])) == (ncol(df) - 2)), ]
  return(df)
}

FB_CHILD_df <- read_csv("FB_Child_Parent_PROMIS_vF_CHILD.csv")
FB_CHILD_df  <- FB_CHILD_df %>%
  rename(id = childid)

FB_PROXY_df <- read_csv("FB_Child_Parent_PROMIS_vF_PROXY.csv")
FB_PROXY_df  <- FB_PROXY_df %>%
  rename(id = parentid)

FI_CHILD_df <- read_csv("FI_Child_Parent_PROMIS_vF_CHILD.csv")
FI_CHILD_df  <- FI_CHILD_df %>%
  rename(id = childid)

FI_PROXY_df <- read_csv("FI_Child_Parent_PROMIS_vF_PROXY.csv")
FI_PROXY_df  <- FI_PROXY_df %>%
  rename(id = parentid)

GH_CHILD_df <- read_csv("GH_Child_Parent_PROMIS_vF_CHILD.csv")
GH_CHILD_df   <- GH_CHILD_df %>%
  rename(id = childid)

GH_PROXY_df <- read_csv("GH_Child_Parent_PROMIS_vF_PROXY.csv")
GH_PROXY_df   <- GH_PROXY_df  %>%
  rename(id = childid)

LS_CHILD_df <- read_csv("LS_Child_Parent_PROMIS_vF_CHILD.csv")
LS_CHILD_df   <- LS_CHILD_df %>%
  rename(id = childid)

LS_PROXY_df <- read_csv("LS_Child_Parent_PROMIS_vF_PROXY.csv")
LS_PROXY_df  <- LS_PROXY_df %>%
  rename(id = parentid)

MP_CHILD_df <- read_csv("MP_Child_Parent_PROMIS_vF_CHILD.csv")
MP_CHILD_df <- MP_CHILD_df  %>%
  rename(id = childid)

MP_PROXY_df <- read_csv("MP_Child_Parent_PROMIS_vF_PROXY.csv")
MP_PROXY_df   <- MP_PROXY_df%>%
  rename(id = parentid)

Phy_CHILD_df <- read_csv("Phy_Child_Parent_PROMIS_vF_CHILD.csv")
Phy_CHILD_df <- Phy_CHILD_df %>%
  rename(id = childid)

Phy_PROXY_df <- read_csv("Phy_Child_Parent_PROMIS_vF_PROXY.csv")
Phy_PROXY_df  <- Phy_PROXY_df %>%
  rename(id = parentid)

PhysAct_CHILD_df <- read_csv("PhysAct_Child_Parent_PROMIS_vF_CHILD.csv")
PhysAct_CHILD_df <- PhysAct_CHILD_df %>%
  rename(id = childid)

PhysAct_PROXY_df <- read_csv("PhysAct_Child_Parent_PROMIS_vF_PROXY.csv")
PhysAct_PROXY_df  <- PhysAct_PROXY_df %>%
  rename(id = parentid)

Pos_Aff_CHILD_df <- read_csv("Pos_Aff_Child_Parent_PROMIS_vF_CHILD.csv")
Pos_Aff_CHILD_df <- Pos_Aff_CHILD_df %>%
  rename(id = childid)

Pos_Aff_PROXY_df <- read_csv("Pos_Aff_Child_Parent_PROMIS_vF_PROXY.csv")
Pos_Aff_PROXY_df  <- Pos_Aff_PROXY_df %>%
  rename(id = parentid)

Psych_CHILD_df <- read_csv("Psych_Child_Parent_PROMIS_vF_CHILD.csv")
Psych_CHILD_df <- Psych_CHILD_df %>%
  rename(id = childid)

Psych_PROXY_df <- read_csv("Psych_Child_Parent_PROMIS_vF_PROXY.csv")
Psych_PROXY_df <- Psych_PROXY_df %>%
  rename(id = parentid)

Strength_CHILD_df <- read_csv("Strength_Child_Parent_PROMIS_vF_CHILD.csv")
Strength_CHILD_df <- Strength_CHILD_df %>%
  rename(id = childid)

Strength_PROXY_df <- read_csv("Strength_Child_Parent_PROMIS_vF_PROXY.csv")
Strength_PROXY_df <- Strength_PROXY_df %>%
  rename(id = parentid)

#-------- Process Family Dataset ------
FBCHILD_df <- FB_CHILD_df |>
  select(starts_with("FAM_FB"), id)
FBCHILD_df <- remove_na(FBCHILD_df)
FBCHILD_df <- pivot_longer(FBCHILD_df, cols=-c(id), names_to="item", values_to="resp")

FBPARENT_df <- FB_PROXY_df  |>
  select(starts_with("FAM_FB"), id)
FBPARENT_df <- remove_na(FBPARENT_df)
FBPARENT_df <- pivot_longer(FBPARENT_df, cols=-c(id), names_to="item", values_to="resp")

FBCHILD_df $ group <- "Children"
FBPARENT_df $ group <- "Parent/Proxy"

FB_df <- rbind(FBCHILD_df, FBPARENT_df )

FICHILD_df <- FI_CHILD_df |>
  select(starts_with("FAM_FI"), id)
FICHILD_df <- remove_na(FICHILD_df)
FICHILD_df <- pivot_longer(FICHILD_df, cols=-c(id), names_to="item", values_to="resp")

FIPARENT_df <- FI_PROXY_df  |>
  select(starts_with("FAM_FI"), id)
FIPARENT_df<- remove_na(FIPARENT_df)
FIPARENT_df <- pivot_longer(FIPARENT_df, cols=-c(id), names_to="item", values_to="resp")

FICHILD_df  $ group <- "Children"
FIPARENT_df $ group <- "Parent/Proxy"

FI_df <- rbind(FICHILD_df, FIPARENT_df )

Family_df <- rbind(FB_df, FI_df)

save(FI_df, file="PROMISPME_Forrest_2021_Family.Rdata")
write.csv(FI_df, "PROMISPME_Forrest_2021_Family.csv", row.names=FALSE)

#-------- Process  Pediatric Global Health-7 Dataset ------
GHGlobal_CHILD_df <- GH_CHILD_df |>
  select(starts_with("Global"), starts_with("PedGlobal"),id)
GHGlobal_CHILD_df <- pivot_longer(GHGlobal_CHILD_df, cols=-c(id), names_to="item", values_to="resp")

GHGlobal_Proxy_df <- GH_PROXY_df |>
  select(starts_with("Global"),starts_with("PedGlobal"),id)
GHGlobal_Proxy_df  <- pivot_longer(GHGlobal_Proxy_df , cols=-c(id), names_to="item", values_to="resp")

GHGlobal_CHILD_df $ group <- "Children"
GHGlobal_Proxy_df $ group <- "Parent/Proxy"

GHGlobal_df <- rbind(GHGlobal_CHILD_df, GHGlobal_Proxy_df)

save(GHGlobal_df, file="PROMISPME_Forrest_2021_GHGlobal.Rdata")
write.csv(GHGlobal_df, "PROMISPME_Forrest_2021_GHGlobal.csv", row.names=FALSE)

#-------- Process Life Satisfaction Dataset ------
LSCHILD_df <- LS_CHILD_df |>
  select(starts_with("SWB_LS"), id)
LSCHILD_df <- remove_na(LSCHILD_df)
LSCHILD_df <- pivot_longer(LSCHILD_df, cols=-c(id), names_to="item", values_to="resp")

LSPARENT_df <- LS_PROXY_df  |>
  select(starts_with("SWB_LS"), id)
LSPARENT_df <- remove_na(LSPARENT_df)
LSPARENT_df  <- pivot_longer(LSPARENT_df , cols=-c(id), names_to="item", values_to="resp")

LSCHILD_df $ group <- "Children"
LSPARENT_df  $ group <- "Parent/Proxy"

LS_df <- rbind(LSCHILD_df, LSPARENT_df)

save(LS_df, file="PROMISPME_Forrest_2021_LS.Rdata")
write.csv(LS_df, "PROMISPME_Forrest_2021_LS.csv", row.names=FALSE)

#-------- Process Meaning & Purpose Dataset ------
MPCHILD_df <- MP_CHILD_df |>
  select(starts_with("SWB_FO"), id)
MPCHILD_df <- remove_na(MPCHILD_df)
MPCHILD_df <- pivot_longer(MPCHILD_df, cols=-c(id), names_to="item", values_to="resp")

MPPARENT_df <- MP_PROXY_df  |>
  select(starts_with("SWB_FO"), id)
MPPARENT_df  <- pivot_longer(MPPARENT_df , cols=-c(id), names_to="item", values_to="resp")

MPCHILD_df $ group <- "Children"
MPPARENT_df  $ group <- "Parent/Proxy"

MP_df <- rbind(MPCHILD_df ,MPPARENT_df)

save(MP_df , file="PROMISPME_Forrest_2021_MP.Rdata")
write.csv(MP_df , "PROMISPME_Forrest_2021_MP.csv", row.names=FALSE)

#-------- Process Physical Dataset ------
PhyCHILD_df <- Phy_CHILD_df |>
  select(starts_with("EoS_S"), id)
PhyCHILD_df <- pivot_longer(PhyCHILD_df, cols=-c(id), names_to="item", values_to="resp")

PhyPARENT_df <- Phy_PROXY_df  |>
  select(starts_with("EoS_S"), id)
PhyPARENT_df  <- pivot_longer(PhyPARENT_df , cols=-c(id), names_to="item", values_to="resp")

PhyCHILD_df $ group <- "Children"
PhyPARENT_df $ group <- "Parent/Proxy"

Phy_df <- rbind(PhyCHILD_df, PhyPARENT_df)

PhysActCHILD_df <- PhysAct_CHILD_df |>
  select(starts_with("PAC_M"), id)
PhysActCHILD_df <- pivot_longer(PhysActCHILD_df, cols=-c(id), names_to="item", values_to="resp")

PhysActPARENT_df <- PhysAct_PROXY_df  |>
  select(starts_with("PAC_M"), id)
PhysActPARENT_df <- pivot_longer(PhysActPARENT_df , cols=-c(id), names_to="item", values_to="resp")

PhysActCHILD_df $ group <- "Children"
PhysActPARENT_df $ group <- "Parent/Proxy"

PhysAct_df <- rbind(PhysActCHILD_df, PhysActPARENT_df)

Physical_df <- rbind(Phy_df, PhysAct_df)
save(Physical_df, file="PROMISPME_Forrest_2021_Physical.Rdata")
write.csv(Physical_df, "PROMISPME_Forrest_2021_Physical.csv", row.names=FALSE)

#-------- Process Physical Stress Affect Dataset ------
PosAffCHILD_df <- Pos_Aff_CHILD_df |>
  select(starts_with("SWB_P"), id)
PosAffCHILD_df <- pivot_longer(PosAffCHILD_df, cols=-c(id), names_to="item", values_to="resp")

PosAffPARENT_df <- Pos_Aff_PROXY_df  |>
  select(starts_with("SWB_P"), id)
PosAffPARENT_df <- pivot_longer(PosAffPARENT_df , cols=-c(id), names_to="item", values_to="resp")

PosAffCHILD_df  $ group <- "Children"
PosAffPARENT_df $ group <- "Parent/Proxy"

PosAff_df <- rbind(PosAffCHILD_df, PosAffPARENT_df)

save(PosAff_df, file="PROMISPME_Forrest_2021_PosAff.Rdata")
write.csv(PosAff_df, "PROMISPME_Forrest_2021_PosAff.csv", row.names=FALSE)

#-------- Process Pediatric Psychological Stress Experience Dataset ------
PsychCHILD_df <- Psych_CHILD_df |>
  select(starts_with("EoS_P"), id)
PsychCHILD_df <- pivot_longer(PsychCHILD_df, cols=-c(id), names_to="item", values_to="resp")

PsychPARENT_df <- Psych_PROXY_df  |>
  select(starts_with("EoS_P"), id)
PsychPARENT_df  <- pivot_longer(PsychPARENT_df , cols=-c(id), names_to="item", values_to="resp")

PsychCHILD_df  $ group <- "Children"
PsychPARENT_df  $ group <- "Parent/Proxy"

Psych_df <- rbind(PsychCHILD_df, PsychPARENT_df)

save(Psych_df, file="PROMISPME_Forrest_2021_Psych.Rdata")
write.csv(Psych_df, "PROMISPME_Forrest_2021_Psych.csv", row.names=FALSE)

#-------- Process Pediatric Psychological Stress Experience Dataset ------
StrengthCHILD_df <- Strength_CHILD_df |>
  select(starts_with("PAC_S"), id)
StrengthCHILD_df <- remove_na(StrengthCHILD_df)
StrengthCHILD_df <- pivot_longer(StrengthCHILD_df, cols=-c(id), names_to="item", values_to="resp")

StrengthPARENT_df <- Strength_PROXY_df  |>
  select(starts_with("PAC_S"), id)
StrengthPARENT_df  <- remove_na(StrengthPARENT_df )
StrengthPARENT_df <- pivot_longer(StrengthPARENT_df , cols=-c(id), names_to="item", values_to="resp")

PsychCHILD_df  $ group <- "Children"
PsychPARENT_df  $ group <- "Parent/Proxy"

Strength_df <- rbind(StrengthCHILD_df, StrengthPARENT_df)

save(Strength_df, file="PROMISPME_Forrest_2021_Strength.Rdata")
write.csv(Strength_df, "PROMISPME_Forrest_2021_Strength.csv", row.names=FALSE)
