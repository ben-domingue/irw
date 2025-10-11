##https://cran.r-project.org/web/packages/BradleyTerry2/refman/BradleyTerry2.html
library(BradleyTerry2)

## CEMS
x<-CEMS$preferences
df<-data.frame(agent_a=x$school1,agent_b=x$school2,rater=x$student)
df$winner<-ifelse(x$tied==1,'draw','agent_a')
df$winner<-ifelse(x$win2==1,'agent_b',df$winner)
write.csv(df,file='bradleyterry2_cems.csv',quote=FALSE,row.names=FALSE)

