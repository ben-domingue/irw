library(EUfootball)

df<-data.frame(agent_a=Matches$Home,agent_b=Matches$Guest)
df$date<-as.numeric(strptime(Matches$date,format='%Y-%m-%d'))
df$score_a<-Matches$Goals90Home
df$score_b<-Matches$Goals90Guest
df$homefield<-'agent_a'
df$winner<-ifelse(df$score_a>df$score_b,'agent_a','agent_b')
df$winner<-ifelse(df$score_a==df$score_b,'draw',df$winner)

write.csv(df,file="eufootball_2010-2020.csv",quote=FALSE,row.names=FALSE)
