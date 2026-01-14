##https://dataverse.harvard.edu/file.xhtml?persistentId=doi:10.7910/DVN/HJZSIM/6O2W5X&version=1.0

load("data-abcp.RData")
x<-the.set$the.set
df<-data.frame(agent_a=x$X1,agent_b=x$X2,rater=x$ref)
df$winner<-ifelse(x[,4],'agent_a','agent_b')
df$winner<-ifelse(x[,4]==x[,5],'draw',df$winner)
df$rater<-paste("expertsurvey_",df$rater,sep='')
dim(df)
df1<-df

load("data-bls.RData")
x<-the.set$the.set
df<-data.frame(agent_a=x$X1,agent_b=x$X2,rater=x$ref)
df$winner<-ifelse(x[,4],'agent_a','agent_b')
df$winner<-ifelse(x[,4]==x[,5],'draw',df$winner)
df$rater<-paste("legislativesurvey_",df$rater,sep='')
dim(df)
df2<-df

df<-data.frame(rbind(df1,df2))
write.csv(df,file="zucco2019_portfoliosalience.csv",quote=FALSE,row.names=FALSE)
