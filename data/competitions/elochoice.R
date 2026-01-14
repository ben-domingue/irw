##https://cran.r-project.org/web/packages/EloChoice/refman/EloChoice.html#physical

library(EloChoice)
data(physical)
df<-data.frame(agent_a=physical$Winner,agent_b=physical$Loser,rater=physical$raterID,winner="agent_a")
write.csv(df,file='elochoice_physical.csv',quote=FALSE,row.names=FALSE)
