library(haven)
library(tidyr)
library(dplyr)

data <- read_sav("S1_Dataset.sav")

data_WC <- data %>%
  select(c("SubNO", "SexSub", "EducaSu", "EdadSu", "Auto1T1_1", "Auto2T1_1", "Auto3T1_1", "Auto4T1_1", "Auto5T1_1", 
           "Auto6T1_1", "Auto7T1_1", "Auto8T1_1", "Auto9T1_1", "TaskVar1T1_1", "TaskVar2T1_1", "TaskVar3T1_1", 
           "TaskVar4T1_1", "TaskSig1T1_1", "TaskSig2T1_1", "TaskSig3T1_1", "TaskSig4T1_1", "TaskID1T1_1", "TaskID2T1_1", 
           "TaskID3T1_1",	"TaskID4T1_1", "FeedJob1T1_1", "FeedJob2T1_1", "FeedJob3T1_1", "JobComp1T1_1", 
           "JobComp2T1_1", "JobComp3T1_1", "JobComp4T1_1", "InfoProc1T1_1", "InfoProc2T1_1", "InfoProc3T1_1",
           "InfoProc4T1_1", "ProbSol1T1_1", "ProbSol2T1_1", "ProbSol3T1_1", "ProbSol4T1_1", "SkillVar1T1_1",
           "SkillVar2T1_1", "SkillVar3T1_1", "SkillVar4T1_1", "Special1T1_1", "Special2T1_1", "Special3T1_1", 
           "Special4T1_1",	"SocSupp1T1_1", "SocSupp2T1_1", "SocSupp3T1_1", "SocSupp4T1_1", "SocSupp5T1_1",
           "SocSupp6T1_1",	"Interdp1T1_1",	"Interdp2T1_1",	"Interdp3T1_1",	"Interdp4T1_1",	"Interdp5T1_1",	
           "Interdp6T1_1",	"InteracOrg1T1_1",	"InteracOrg2T1_1",	"InteracOrg3T1_1",	"InteracOrg4T1_1",
           "FeedOthers1T1_1",	"FeedOthers2T1_1",	"FeedOthers3T1_1",	"Ergo1T1_1",	"Ergo2T1_1",	"Ergo3T1_1",
           "PhysDem1T1_1",	"PhysDem2T1_1",	"PhysDem3T1_1",	"WrkCond1T1_1",	"WrkCond2T1_1",	"WrkCond3T1_1",	
           "WrkCond4T1_1",	"WrkCond5T1_1",	"EquipUse1T1_1",	"EquipUse2T1_1",	"EquipUse3T1_1"))

data_JS <- data %>%
  select(c("SubNO", "SexSub", "EducaSu", "EdadSu", "JS1T1_1", "JS2T1_1", "JS3T1_1", "JS4T1_1", "JS5T1_1"))

data_JP <- data %>%
  select(c("SubNO", "SexSub", "EducaSu", "EdadSu", "LeaderNO", "TaskP1T1_1", "TaskP2T1_1", "TaskP3T1_1", "TaskP4T1_1"))

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

write.csv(data_WC, "hpwt_bayona_2025_workcharacteristics.csv", row.names=FALSE)
write.csv(data_JS, "hpwt_bayona_2025_jobsatisfaction.csv", row.names=FALSE)
write.csv(data_JP, "hpwt_bayona_2025_jobperformance.csv", row.names=FALSE)
