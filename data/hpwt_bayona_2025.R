library(haven)
library(tidyr)
library(dplyr)

data <- read_sav("S1_Dataset.sav")

data_WC <- data %>%
  select(c("SubNO", "SexSub", "EducaSu", "EdadSu", "Auto1T1", "Auto2T1", "Auto3T1", "Auto4T1", "Auto5T1", 
           "Auto6T1", "Auto7T1", "Auto8T1", "Auto9T1", "TaskVar1T1", "TaskVar2T1", "TaskVar3T1", 
           "TaskVar4T1", "TaskSig1T1", "TaskSig2T1", "TaskSig3T1", "TaskSig4T1", "TaskID1T1", "TaskID2T1", 
           "TaskID3T1",	"TaskID4T1", "FeedJob1T1", "FeedJob2T1", "FeedJob3T1", "JobComp1T1", 
           "JobComp2T1", "JobComp3T1", "JobComp4T1", "InfoProc1T1", "InfoProc2T1", "InfoProc3T1",
           "InfoProc4T1", "ProbSol1T1", "ProbSol2T1", "ProbSol3T1", "ProbSol4T1", "SkillVar1T1",
           "SkillVar2T1", "SkillVar3T1", "SkillVar4T1", "Special1T1", "Special2T1", "Special3T1", 
           "Special4T1",	"SocSupp1T1", "SocSupp2T1", "SocSupp3T1", "SocSupp4T1", "SocSupp5T1",
           "SocSupp6T1",	"Interdp1T1",	"Interdp2T1",	"Interdp3T1",	"Interdp4T1",	"Interdp5T1",	
           "Interdp6T1",	"InteracOrg1T1",	"InteracOrg2T1",	"InteracOrg3T1",	"InteracOrg4T1",
           "FeedOthers1T1",	"FeedOthers2T1",	"FeedOthers3T1",	"Ergo1T1",	"Ergo2T1",	"Ergo3T1",
           "PhysDem1T1",	"PhysDem2T1",	"PhysDem3T1",	"WrkCond1T1",	"WrkCond2T1",	"WrkCond3T1",	
           "WrkCond4T1",	"WrkCond5T1",	"EquipUse1T1",	"EquipUse2T1",	"EquipUse3T1"))

data_JS <- data %>%
  select(c("SubNO", "SexSub", "EducaSu", "EdadSu", "JS1T1", "JS2T1", "JS3T1", "JS4T1", "JS5T1"))

data_JP <- data %>%
  select(c("SubNO", "SexSub", "EducaSu", "EdadSu", "LeaderNO", "TaskP1T1", "TaskP2T1", "TaskP3T1", "TaskP4T1"))

data_WC <- data_WC %>%
  rename("id" = "SubNO", "cov_gender" = "SexSub", "cov_education" = "EducaSu", "cov_age" = "EdadSu") %>%
  pivot_longer(-c("id", "cov_gender", "cov_education", "cov_age"),
               names_to = "item",
               values_to = "resp")

data_JS <- data_JS %>%
  rename("id" = "SubNO", "cov_gender" = "SexSub", "cov_education" = "EducaSu", "cov_age" = "EdadSu") %>%
  pivot_longer(-c("id", "cov_gender", "cov_education", "cov_age"),
               names_to = "item",
               values_to = "resp")

data_JP <- data_JP %>%
  rename("id" = "SubNO", "cov_gender" = "SexSub", "cov_education" = "EducaSu", "cov_age" = "EdadSu", "rater" = "LeaderNO") %>%
  pivot_longer(-c("id", "cov_gender", "cov_education", "cov_age", "rater"),
               names_to = "item",
               values_to = "resp")

data_WC <- data_WC %>%
  mutate(resp = ifelse(resp %% 1 != 0, NA, resp))

data_JS <- data_JS %>%
  mutate(resp = ifelse(resp %% 1 != 0, NA, resp))

data_JP <- data_JP %>%
  mutate(resp = ifelse(resp %% 1 != 0, NA, resp))

write.csv(data_WC, "hpwt_bayona_2025_workcharacteristics.csv", row.names=FALSE)
write.csv(data_JS, "hpwt_bayona_2025_jobsatisfaction.csv", row.names=FALSE)
write.csv(data_JP, "hpwt_bayona_2025_jobperformance.csv", row.names=FALSE)
